from odoo import api, fields, models
from odoo.exceptions import UserError


class TourismDeparture(models.Model):
    """A scheduled departure of a package on a given date, with its own seat
    capacity. Bookings attach to a departure so the agency can prevent
    overbooking a specific trip and assign a guide and vehicle."""

    _name = "tourism.departure"
    _description = "Scheduled Departure"
    _order = "departure_date, id"
    _inherit = ["mail.thread"]

    name = fields.Char(compute="_compute_name", store=True)
    package_id = fields.Many2one("tourism.tour.package", string="Package", required=True, tracking=True)
    departure_date = fields.Date(required=True, tracking=True, default=fields.Date.context_today)
    capacity = fields.Integer(default=20, required=True)
    guide_id = fields.Many2one(
        "res.partner", string="Tour Guide", domain=[("is_tour_guide", "=", True)], tracking=True
    )
    vehicle_id = fields.Many2one("tourism.vehicle", string="Assigned Vehicle")
    currency_id = fields.Many2one(related="package_id.currency_id", readonly=True)

    state = fields.Selection(
        selection=[
            ("scheduled", "Scheduled"),
            ("confirmed", "Confirmed"),
            ("departed", "Departed"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="scheduled",
        required=True,
        tracking=True,
    )

    booking_ids = fields.One2many("tourism.booking", "departure_id", string="Bookings")
    seats_booked = fields.Integer(compute="_compute_seats", store=True)
    seats_available = fields.Integer(compute="_compute_seats", store=True)
    is_full = fields.Boolean(compute="_compute_seats", store=True)
    revenue = fields.Monetary(compute="_compute_seats", store=True)

    _check_capacity = models.Constraint(
        "CHECK(capacity > 0)",
        "A departure must offer at least one seat.",
    )

    @api.depends("package_id", "departure_date")
    def _compute_name(self):
        for dep in self:
            if dep.package_id and dep.departure_date:
                dep.name = "%s — %s" % (dep.package_id.name, dep.departure_date)
            else:
                dep.name = dep.package_id.name or "Departure"

    @api.depends("booking_ids.state", "booking_ids.group_size", "booking_ids.amount_total", "capacity")
    def _compute_seats(self):
        for dep in self:
            live = dep.booking_ids.filtered(lambda b: b.state != "cancelled")
            booked = sum(live.mapped("group_size"))
            dep.seats_booked = booked
            dep.seats_available = max(dep.capacity - booked, 0)
            dep.is_full = booked >= dep.capacity
            billable = dep.booking_ids.filtered(lambda b: b.state in ("paid", "completed"))
            dep.revenue = sum(billable.mapped("amount_total"))

    @api.onchange("package_id")
    def _onchange_package(self):
        if self.package_id and self.package_id.capacity:
            self.capacity = self.package_id.capacity

    def action_confirm(self):
        self.write({"state": "confirmed"})
        return True

    def action_depart(self):
        self.write({"state": "departed"})
        return True

    def action_done(self):
        self.write({"state": "done"})
        return True

    def action_cancel(self):
        for dep in self:
            if any(b.state in ("paid", "completed") for b in dep.booking_ids):
                raise UserError(
                    "Departure '%s' has paid bookings and cannot be cancelled as-is." % dep.name
                )
            dep.state = "cancelled"
        return True

    def action_view_bookings(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Bookings",
            "res_model": "tourism.booking",
            "view_mode": "list,form",
            "domain": [("departure_id", "=", self.id)],
            "context": {
                "default_departure_id": self.id,
                "default_package_id": self.package_id.id,
            },
        }
