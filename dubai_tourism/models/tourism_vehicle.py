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
    trips_done = fields.Integer(compute="_compute_assignment_count", store=True)
    passengers_transported = fields.Integer(compute="_compute_assignment_count", store=True)
    # Average seat fill across completed trips (a simple utilisation signal).
    utilization = fields.Float(string="Avg Seat Fill (%)", compute="_compute_assignment_count", store=True,
                               aggregator="avg")

    _check_seats = models.Constraint(
        "CHECK(seats > 0)",
        "A vehicle must have at least one seat.",
    )

    @api.depends("assignment_ids.state", "assignment_ids.passenger_count", "seats")
    def _compute_assignment_count(self):
        for vehicle in self:
            vehicle.assignment_count = len(vehicle.assignment_ids)
            done = vehicle.assignment_ids.filtered(lambda a: a.state == "done")
            vehicle.trips_done = len(done)
            vehicle.passengers_transported = sum(done.mapped("passenger_count"))
            if done and vehicle.seats:
                fills = [min(a.passenger_count / vehicle.seats, 1.0) for a in done]
                vehicle.utilization = round(100.0 * sum(fills) / len(fills), 1)
            else:
                vehicle.utilization = 0.0
