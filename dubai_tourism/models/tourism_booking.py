from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

# Commercial rules from the case study:
#   * families travelling with young children get a benefit,
#   * groups of ten or more get a discounted rate.
FAMILY_DISCOUNT_PERCENT = 5.0      # applied when at least one child travels
GROUP_DISCOUNT_PERCENT = 10.0      # applied when the group reaches the threshold
GROUP_THRESHOLD = 10


class TourismBooking(models.Model):
    """A customer's reservation of a tour package — pricing (with family & group
    discounts), the sale lifecycle, transport and payment all live here."""

    _name = "tourism.booking"
    _description = "Tour Booking"
    _order = "departure_date desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Reference", required=True, copy=False, readonly=True, default="New")
    customer_id = fields.Many2one("res.partner", string="Customer", required=True, tracking=True)
    package_id = fields.Many2one("tourism.tour.package", string="Package", required=True, tracking=True)
    salesperson_id = fields.Many2one(
        "res.users", string="Agent", default=lambda self: self.env.user, tracking=True
    )
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="package_id.currency_id", store=True, readonly=True)

    departure_date = fields.Date(required=True, tracking=True, default=fields.Date.context_today)
    duration_days = fields.Integer(related="package_id.duration_days", readonly=True)

    adult_count = fields.Integer(string="Adults", default=1, required=True)
    child_count = fields.Integer(string="Children", default=0)
    group_size = fields.Integer(compute="_compute_group_size", store=True)
    has_young_children = fields.Boolean(compute="_compute_group_size", store=True)
    is_group = fields.Boolean(string="Group Booking", compute="_compute_group_size", store=True)

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("paid", "Paid"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        copy=False,
        tracking=True,
    )

    # --- Pricing ---
    amount_adults = fields.Monetary(compute="_compute_amounts", store=True)
    amount_children = fields.Monetary(compute="_compute_amounts", store=True)
    amount_untaxed = fields.Monetary(string="Subtotal", compute="_compute_amounts", store=True)
    family_discount = fields.Monetary(compute="_compute_amounts", store=True)
    group_discount = fields.Monetary(compute="_compute_amounts", store=True)
    discount_total = fields.Monetary(compute="_compute_amounts", store=True)
    amount_total = fields.Monetary(string="Total", compute="_compute_amounts", store=True)

    # --- Transport ---
    transport_assignment_ids = fields.One2many(
        "tourism.transport.assignment", "booking_id", string="Transport"
    )
    transport_count = fields.Integer(compute="_compute_transport_count")
    transport_commission = fields.Monetary(compute="_compute_transport_count", store=True)

    note = fields.Text()

    _check_adults = models.Constraint(
        "CHECK(adult_count > 0)",
        "A booking needs at least one adult traveller.",
    )
    _check_children = models.Constraint(
        "CHECK(child_count >= 0)",
        "The number of children cannot be negative.",
    )

    # --- Computes ----------------------------------------------------------
    @api.depends("adult_count", "child_count")
    def _compute_group_size(self):
        for booking in self:
            booking.group_size = booking.adult_count + booking.child_count
            booking.has_young_children = booking.child_count > 0
            booking.is_group = (booking.adult_count + booking.child_count) >= GROUP_THRESHOLD

    @api.depends("adult_count", "child_count", "package_id.price_adult", "package_id.price_child")
    def _compute_amounts(self):
        for booking in self:
            adults = booking.adult_count * booking.package_id.price_adult
            children = booking.child_count * booking.package_id.price_child
            subtotal = adults + children
            family = subtotal * FAMILY_DISCOUNT_PERCENT / 100.0 if booking.child_count > 0 else 0.0
            group = subtotal * GROUP_DISCOUNT_PERCENT / 100.0 if (booking.adult_count + booking.child_count) >= GROUP_THRESHOLD else 0.0
            booking.amount_adults = adults
            booking.amount_children = children
            booking.amount_untaxed = subtotal
            booking.family_discount = family
            booking.group_discount = group
            booking.discount_total = family + group
            booking.amount_total = subtotal - family - group

    @api.depends("transport_assignment_ids.commission_amount", "transport_assignment_ids.state")
    def _compute_transport_count(self):
        for booking in self:
            booking.transport_count = len(booking.transport_assignment_ids)
            live = booking.transport_assignment_ids.filtered(lambda a: a.state != "cancelled")
            booking.transport_commission = sum(live.mapped("commission_amount"))

    # --- Constraints -------------------------------------------------------
    @api.constrains("adult_count", "child_count", "package_id")
    def _check_capacity(self):
        for booking in self:
            cap = booking.package_id.capacity
            size = booking.adult_count + booking.child_count
            if cap and size > cap:
                raise ValidationError(
                    "%s accepts at most %d travellers per departure, but %d were requested."
                    % (booking.package_id.name, cap, size)
                )

    # --- Sequence ----------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals["name"] == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("tourism.booking") or "New"
        return super().create(vals_list)

    # --- State actions -----------------------------------------------------
    def action_confirm(self):
        for booking in self:
            if booking.state != "draft":
                raise UserError("Only draft bookings can be confirmed.")
            booking.state = "confirmed"
        return True

    def action_register_payment(self):
        for booking in self:
            if booking.state not in ("draft", "confirmed"):
                raise UserError("Only an open booking can be marked as paid.")
            booking.state = "paid"
        return True

    def action_complete(self):
        # Payment gate: a tour is only completed once it has been paid for.
        for booking in self:
            if booking.state != "paid":
                raise UserError(
                    "Booking %s must be paid before it can be completed." % booking.name
                )
            booking.state = "completed"
        return True

    def action_cancel(self):
        for booking in self:
            if booking.state == "completed":
                raise UserError("A completed booking cannot be cancelled.")
            booking.state = "cancelled"
        return True

    def action_reset_to_draft(self):
        self.write({"state": "draft"})
        return True

    # --- Wizards / smart buttons ------------------------------------------
    def action_assign_transport(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Assign Transport",
            "res_model": "tourism.assign.transport.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_booking_id": self.id, "default_passenger_count": self.group_size},
        }

    def action_view_transport(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Transport",
            "res_model": "tourism.transport.assignment",
            "view_mode": "list,form",
            "domain": [("booking_id", "=", self.id)],
            "context": {"default_booking_id": self.id, "default_passenger_count": self.group_size},
        }
