from odoo import api, fields, models


class TourismVehicle(models.Model):
    """A vehicle in the agency's own fleet (buses and vans). Larger groups ride
    internal vehicles; small groups are sent to partnered taxi companies."""

    _name = "tourism.vehicle"
    _description = "Fleet Vehicle"
    _order = "name"

    name = fields.Char(required=True)
    vehicle_type = fields.Selection(
        selection=[("bus", "Bus"), ("van", "Van"), ("car", "Car")],
        default="van",
        required=True,
    )
    license_plate = fields.Char()
    seats = fields.Integer(string="Seats", default=14, required=True)
    driver_id = fields.Many2one("res.partner", string="Driver")
    state = fields.Selection(
        selection=[
            ("available", "Available"),
            ("on_trip", "On Trip"),
            ("maintenance", "Maintenance"),
        ],
        default="available",
        required=True,
    )
    active = fields.Boolean(default=True)
    color = fields.Integer()

    assignment_ids = fields.One2many("tourism.transport.assignment", "vehicle_id", string="Trips")
    assignment_count = fields.Integer(compute="_compute_assignment_count")

    _check_seats = models.Constraint(
        "CHECK(seats > 0)",
        "A vehicle must have at least one seat.",
    )

    @api.depends("assignment_ids")
    def _compute_assignment_count(self):
        for vehicle in self:
            vehicle.assignment_count = len(vehicle.assignment_ids)
