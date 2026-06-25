from odoo import fields, models


class SportType(models.Model):
    """A kind of sport (Tennis, Football...) carrying the rules that the rest of
    the system enforces — most importantly the per-session participant limit."""

    _name = "sport.type"
    _description = "Sport Type"
    _order = "name"

    name = fields.Char(required=True)
    code = fields.Char(help="Short code used in references, e.g. TEN for Tennis.")
    max_participants = fields.Integer(
        string="Max Participants / Session",
        default=4,
        required=True,
        help="Maximum number of players allowed in a single game session for this sport.",
    )
    default_duration = fields.Float(
        string="Default Duration (h)",
        default=1.0,
        help="Pre-fills the slot length when a new booking is created.",
    )
    color = fields.Integer(string="Color")
    active = fields.Boolean(default=True)

    court_ids = fields.One2many("sport.court", "sport_type_id", string="Courts")

    _check_max_participants = models.Constraint(
        "CHECK(max_participants > 0)",
        "The maximum number of participants must be strictly positive.",
    )
