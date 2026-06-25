from odoo import api, fields, models


class SportCourt(models.Model):
    """A bookable court / pitch. Each court belongs to one sport, which fixes its
    capacity rule and feeds the booking calendar."""

    _name = "sport.court"
    _description = "Sport Court"
    _order = "sport_type_id, name"

    name = fields.Char(required=True)
    sport_type_id = fields.Many2one("sport.type", string="Sport", required=True, ondelete="restrict")
    # Mirror the capacity onto the court so views/searches can use it directly.
    max_participants = fields.Integer(related="sport_type_id.max_participants", store=True, readonly=True)
    hourly_price = fields.Float(string="Price / Hour", required=True, default=50.0)
    state = fields.Selection(
        selection=[("available", "Available"), ("maintenance", "Under Maintenance")],
        default="available",
        required=True,
    )
    active = fields.Boolean(default=True)
    color = fields.Integer(related="sport_type_id.color", store=True)
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)

    booking_ids = fields.One2many("sport.booking", "court_id", string="Bookings")
    booking_count = fields.Integer(compute="_compute_booking_count")

    _check_hourly_price = models.Constraint(
        "CHECK(hourly_price >= 0)",
        "The hourly price cannot be negative.",
    )

    @api.depends("booking_ids")
    def _compute_booking_count(self):
        for court in self:
            court.booking_count = len(court.booking_ids)

    def action_view_bookings(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Bookings",
            "res_model": "sport.booking",
            "view_mode": "calendar,list,form",
            "domain": [("court_id", "=", self.id)],
            "context": {"default_court_id": self.id},
        }
