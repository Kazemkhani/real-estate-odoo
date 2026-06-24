from odoo import api, fields, models


class TourismDestination(models.Model):
    """A place a tour visits (Burj Khalifa, the desert, the Marina...). Popularity
    is derived from how many confirmed bookings reach it, so marketing can see
    what's actually selling."""

    _name = "tourism.destination"
    _description = "Tourism Destination"
    _order = "name"

    name = fields.Char(required=True)
    city = fields.Char(default="Dubai")
    country_id = fields.Many2one("res.country", string="Country")
    description = fields.Text()
    image = fields.Image("Photo", max_width=1920, max_height=1920)
    color = fields.Integer()
    active = fields.Boolean(default=True)

    package_ids = fields.Many2many(
        "tourism.tour.package", "tourism_package_destination_rel",
        "destination_id", "package_id", string="Tour Packages",
    )
    package_count = fields.Integer(compute="_compute_stats")
    # How many travellers (across confirmed/paid/completed bookings) have this
    # destination on their itinerary — a simple popularity signal.
    booking_count = fields.Integer(compute="_compute_stats", store=True)

    @api.depends("package_ids.booking_ids.state", "package_ids.booking_ids.group_size")
    def _compute_stats(self):
        for dest in self:
            dest.package_count = len(dest.package_ids)
            travellers = 0
            for package in dest.package_ids:
                for booking in package.booking_ids:
                    if booking.state in ("confirmed", "paid", "completed"):
                        travellers += booking.group_size
            dest.booking_count = travellers
