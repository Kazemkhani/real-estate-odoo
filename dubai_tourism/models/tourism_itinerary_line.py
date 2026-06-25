from odoo import fields, models


class TourismItineraryLine(models.Model):
    """A single day of a package's itinerary — what travellers do and where."""

    _name = "tourism.itinerary.line"
    _description = "Itinerary Line"
    _order = "package_id, day_number, sequence"

    package_id = fields.Many2one("tourism.tour.package", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    day_number = fields.Integer(string="Day", default=1)
    title = fields.Char(required=True)
    destination_id = fields.Many2one("tourism.destination", string="Destination")
    description = fields.Text()
