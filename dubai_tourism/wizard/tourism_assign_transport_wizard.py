from odoo import api, fields, models
from odoo.exceptions import UserError


class TourismAssignTransportWizard(models.TransientModel):
    """A guided dialog to attach transport to a booking — pick internal fleet or
    a third-party taxi company, and the assignment is created for you."""

    _name = "tourism.assign.transport.wizard"
    _description = "Assign Transport to a Booking"

    booking_id = fields.Many2one(
        "tourism.booking", string="Booking", required=True,
        default=lambda self: self.env.context.get("default_booking_id"),
    )
    transport_type = fields.Selection(
        selection=[("internal", "Internal Fleet"), ("external", "Third-Party Taxi")],
        default="internal",
        required=True,
    )
    vehicle_id = fields.Many2one(
        "tourism.vehicle", string="Fleet Vehicle", domain=[("state", "=", "available")]
    )
    taxi_company_id = fields.Many2one(
        "res.partner", string="Taxi Company", domain=[("is_taxi_company", "=", True)]
    )
    passenger_count = fields.Integer(
        default=lambda self: self.env.context.get("default_passenger_count", 1), required=True
    )
    pickup_location = fields.Char()
    dropoff_location = fields.Char()
    cost = fields.Monetary()
    commission_rate = fields.Float(string="Commission (%)", default=15.0)
    currency_id = fields.Many2one(related="booking_id.currency_id")

    def action_assign(self):
        self.ensure_one()
        if self.transport_type == "internal" and not self.vehicle_id:
            raise UserError("Please choose a fleet vehicle for an internal trip.")
        if self.transport_type == "external" and not self.taxi_company_id:
            raise UserError("Please choose a taxi company for a third-party trip.")
        self.env["tourism.transport.assignment"].create({
            "booking_id": self.booking_id.id,
            "transport_type": self.transport_type,
            "vehicle_id": self.vehicle_id.id if self.transport_type == "internal" else False,
            "taxi_company_id": self.taxi_company_id.id if self.transport_type == "external" else False,
            "passenger_count": self.passenger_count,
            "pickup_location": self.pickup_location,
            "dropoff_location": self.dropoff_location,
            "cost": self.cost,
            "commission_rate": self.commission_rate,
        })
        return {"type": "ir.actions.act_window_close"}
