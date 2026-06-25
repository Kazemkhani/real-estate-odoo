from odoo import api, fields, models
from odoo.exceptions import UserError


class SportCoachingClass(models.Model):
    """A summer coaching program run by a private coach. Seats are limited and
    allocated first-come, first-served through registrations."""

    _name = "sport.coaching.class"
    _description = "Coaching Class"
    _order = "start_date, name"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True, tracking=True)
    sport_type_id = fields.Many2one("sport.type", string="Sport", required=True)
    coach_id = fields.Many2one(
        "res.partner", string="Coach", domain=[("is_coach", "=", True)], tracking=True
    )
    start_date = fields.Date(tracking=True)
    end_date = fields.Date()
    schedule = fields.Char(help="Human-readable schedule, e.g. 'Mon & Wed, 17:00–18:00'.")
    price = fields.Float(string="Price / Seat", default=200.0)
    capacity = fields.Integer(string="Seats", default=10, required=True)
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)

    state = fields.Selection(
        selection=[("draft", "Draft"), ("open", "Open"), ("closed", "Closed"), ("cancelled", "Cancelled")],
        default="draft",
        required=True,
        tracking=True,
    )

    registration_ids = fields.One2many("sport.class.registration", "class_id", string="Registrations")
    seats_taken = fields.Integer(compute="_compute_seats", store=True)
    seats_available = fields.Integer(compute="_compute_seats", store=True)
    is_full = fields.Boolean(compute="_compute_seats", store=True)

    _check_capacity = models.Constraint(
        "CHECK(capacity > 0)",
        "A coaching class must offer at least one seat.",
    )

    @api.depends("registration_ids.state", "capacity")
    def _compute_seats(self):
        for cls in self:
            taken = len(cls.registration_ids.filtered(lambda r: r.state in ("confirmed", "paid")))
            cls.seats_taken = taken
            cls.seats_available = max(cls.capacity - taken, 0)
            cls.is_full = taken >= cls.capacity

    def action_open(self):
        self.write({"state": "open"})
        return True

    def action_close(self):
        self.write({"state": "closed"})
        return True

    def action_cancel(self):
        for cls in self:
            if any(r.state == "paid" for r in cls.registration_ids):
                raise UserError(
                    "Class '%s' has paid registrations and cannot be cancelled as-is." % cls.name
                )
            cls.state = "cancelled"
        return True
