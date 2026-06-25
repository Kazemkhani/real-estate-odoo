from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .res_config_settings import (
    DEFAULT_FAMILY_DISCOUNT,
    DEFAULT_GROUP_DISCOUNT,
    DEFAULT_GROUP_THRESHOLD,
)


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
    departure_id = fields.Many2one(
        "tourism.departure", string="Departure", tracking=True, ondelete="restrict",
        help="Optional: attach this booking to a scheduled departure to manage seats per trip.",
    )
    guide_id = fields.Many2one(related="departure_id.guide_id", string="Tour Guide", readonly=True)
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
    def _discount_config(self):
        """Read the discount rules from Settings, falling back to the case-study
        defaults when a parameter has never been set."""
        get = self.env["ir.config_parameter"].sudo().get_param
        return {
            "family": float(get("dubai_tourism.family_discount", DEFAULT_FAMILY_DISCOUNT)),
            "group": float(get("dubai_tourism.group_discount", DEFAULT_GROUP_DISCOUNT)),
            "threshold": int(float(get("dubai_tourism.group_threshold", DEFAULT_GROUP_THRESHOLD))),
        }

    @api.depends("adult_count", "child_count")
    def _compute_group_size(self):
        threshold = self._discount_config()["threshold"]
        for booking in self:
            booking.group_size = booking.adult_count + booking.child_count
            booking.has_young_children = booking.child_count > 0
            booking.is_group = booking.group_size >= threshold

    @api.depends("adult_count", "child_count", "package_id.effective_price_adult",
                 "package_id.price_child")
    def _compute_amounts(self):
        cfg = self._discount_config()
        for booking in self:
            # Featured packages may carry a promotional adult price.
            adults = booking.adult_count * booking.package_id.effective_price_adult
            children = booking.child_count * booking.package_id.price_child
            subtotal = adults + children
            size = booking.adult_count + booking.child_count
            family = subtotal * cfg["family"] / 100.0 if booking.child_count > 0 else 0.0
            group = subtotal * cfg["group"] / 100.0 if size >= cfg["threshold"] else 0.0
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

    # --- Onchange ----------------------------------------------------------
    @api.onchange("departure_id")
    def _onchange_departure(self):
        # A departure fixes the package and the date for the trip.
        if self.departure_id:
            self.package_id = self.departure_id.package_id
            self.departure_date = self.departure_id.departure_date

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

    @api.constrains("departure_id", "package_id", "adult_count", "child_count", "state")
    def _check_departure(self):
        """When a booking is tied to a scheduled departure, it must match that
        departure's package and must not overbook the trip's seats."""
        for booking in self:
            dep = booking.departure_id
            if not dep:
                continue
            if booking.state == "cancelled":
                continue
            if booking.package_id != dep.package_id:
                raise ValidationError(
                    "Booking %s must use the package of its departure (%s)."
                    % (booking.name, dep.package_id.name)
                )
            booked = sum(
                b.group_size for b in dep.booking_ids
                if b.state != "cancelled"
            )
            if booked > dep.capacity:
                raise ValidationError(
                    "Departure '%s' is full: %d/%d seats. This booking would overbook it."
                    % (dep.name, booked, dep.capacity)
                )

    # --- Sequence ----------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # A departure fixes the package and date. In the form these fields are
            # read-only once a departure is picked, so the web client doesn't send
            # them — derive them here so the required package_id is never null.
            if vals.get("departure_id"):
                departure = self.env["tourism.departure"].browse(vals["departure_id"])
                vals.setdefault("package_id", departure.package_id.id)
                vals.setdefault("departure_date", departure.departure_date)
            if not vals.get("name") or vals["name"] == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("tourism.booking") or "New"
        return super().create(vals_list)

    # --- Email helper ------------------------------------------------------
    def _auto_email_enabled(self):
        val = self.env["ir.config_parameter"].sudo().get_param("dubai_tourism.auto_email")
        # config params are strings — guard against the literal "False"/"0"/empty.
        return str(val).lower() not in ("false", "0", "", "none")

    def _send_mail(self, template_xmlid):
        """Email the customer using a template, if auto-emailing is enabled and a
        valid template/email exists. Failures never block the booking flow."""
        if not self._auto_email_enabled():
            return
        template = self.env.ref(template_xmlid, raise_if_not_found=False)
        if not template:
            return
        for booking in self:
            if booking.customer_id.email:
                template.send_mail(booking.id, force_send=False)

    # --- State actions -----------------------------------------------------
    def action_confirm(self):
        for booking in self:
            if booking.state != "draft":
                raise UserError("Only draft bookings can be confirmed.")
            booking.state = "confirmed"
        self._send_mail("dubai_tourism.mail_template_booking_confirmation")
        return True

    def action_register_payment(self):
        for booking in self:
            if booking.state not in ("draft", "confirmed"):
                raise UserError("Only an open booking can be marked as paid.")
            booking.state = "paid"
        self._send_mail("dubai_tourism.mail_template_booking_receipt")
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

    # --- Scheduled action --------------------------------------------------
    @api.model
    def _cron_cancel_overdue_unpaid(self):
        """Cancel bookings that are still unpaid a configurable number of days
        after their departure date. Disabled when the setting is 0."""
        days = int(float(self.env["ir.config_parameter"].sudo().get_param(
            "dubai_tourism.auto_cancel_days", 0)))
        if days <= 0:
            return
        from datetime import timedelta
        cutoff = fields.Date.today() - timedelta(days=days)
        overdue = self.search([
            ("state", "in", ("draft", "confirmed")),
            ("departure_date", "<", cutoff),
        ])
        if overdue:
            overdue.write({"state": "cancelled"})
            for booking in overdue:
                booking.message_post(body="Automatically cancelled: unpaid past departure.")
