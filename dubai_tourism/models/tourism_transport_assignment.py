from odoo import api, fields, models
from odoo.exceptions import ValidationError


class TourismTransportAssignment(models.Model):
    """How a booking's travellers actually get around. Either an internal fleet
    vehicle, or a partnered third-party taxi company — on which the agency earns
    a commission (one of its two revenue streams)."""

    _name = "tourism.transport.assignment"
    _description = "Transport Assignment"
    _order = "pickup_datetime desc, id desc"

    name = fields.Char(string="Reference", required=True, copy=False, readonly=True, default="New")
    booking_id = fields.Many2one("tourism.booking", string="Booking", required=True, ondelete="cascade")
    customer_id = fields.Many2one(related="booking_id.customer_id", store=True, readonly=True)
    currency_id = fields.Many2one(related="booking_id.currency_id", store=True, readonly=True)

    transport_type = fields.Selection(
        selection=[("internal", "Internal Fleet"), ("external", "Third-Party Taxi")],
        default="internal",
        required=True,
    )
    vehicle_id = fields.Many2one("tourism.vehicle", string="Fleet Vehicle")
    taxi_company_id = fields.Many2one(
        "res.partner", string="Taxi Company", domain=[("is_taxi_company", "=", True)],
    )

    pickup_datetime = fields.Datetime(string="Pick-up", default=lambda self: fields.Datetime.now())
    pickup_location = fields.Char()
    dropoff_location = fields.Char()
    passenger_count = fields.Integer(default=1, required=True)

    cost = fields.Monetary(string="Transport Cost", help="What the trip costs the agency.")
    commission_rate = fields.Float(
        string="Commission (%)", default=15.0,
        help="Commission the agency earns — typically on third-party transport.",
    )
    commission_amount = fields.Monetary(compute="_compute_commission", store=True)

    state = fields.Selection(
        selection=[
            ("planned", "Planned"),
            ("ongoing", "Ongoing"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="planned",
        required=True,
    )

    _check_passengers = models.Constraint(
        "CHECK(passenger_count > 0)",
        "A transport assignment must carry at least one passenger.",
    )

    @api.depends("transport_type", "cost", "commission_rate")
    def _compute_commission(self):
        for assignment in self:
            # Commission is earned on third-party transport; internal trips are a cost.
            if assignment.transport_type == "external":
                assignment.commission_amount = assignment.cost * assignment.commission_rate / 100.0
            else:
                assignment.commission_amount = 0.0

    @api.onchange("transport_type")
    def _onchange_transport_type(self):
        # Keep only the field relevant to the chosen mode populated.
        if self.transport_type == "internal":
            self.taxi_company_id = False
        else:
            self.vehicle_id = False

    @api.constrains("transport_type", "vehicle_id", "taxi_company_id", "passenger_count")
    def _check_transport(self):
        for assignment in self:
            if assignment.transport_type == "internal":
                if not assignment.vehicle_id:
                    raise ValidationError("An internal trip needs a fleet vehicle.")
                if assignment.passenger_count > assignment.vehicle_id.seats:
                    raise ValidationError(
                        "%s seats %d, but %d passengers were assigned."
                        % (assignment.vehicle_id.name, assignment.vehicle_id.seats, assignment.passenger_count)
                    )
            else:  # external
                if not assignment.taxi_company_id:
                    raise ValidationError("A third-party trip needs a taxi company.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals["name"] == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("tourism.transport.assignment") or "New"
        return super().create(vals_list)

    def action_start(self):
        for a in self:
            a.state = "ongoing"
            if a.vehicle_id:
                a.vehicle_id.state = "on_trip"
        return True

    def action_done(self):
        for a in self:
            a.state = "done"
            if a.vehicle_id:
                a.vehicle_id.state = "available"
        return True

    def action_cancel(self):
        self.write({"state": "cancelled"})
        return True
