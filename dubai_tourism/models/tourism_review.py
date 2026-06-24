from odoo import api, fields, models


class TourismReview(models.Model):
    """A customer's star rating of a completed tour. Feeds the package average
    rating used for ranking and marketing."""

    _name = "tourism.review"
    _description = "Tour Review"
    _order = "create_date desc"

    booking_id = fields.Many2one("tourism.booking", string="Booking", ondelete="cascade")
    package_id = fields.Many2one(
        "tourism.tour.package", string="Package", required=True, ondelete="cascade",
    )
    customer_id = fields.Many2one("res.partner", string="Customer", required=True)
    rating = fields.Selection(
        selection=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5")],
        required=True,
        default="5",
    )
    comment = fields.Text()

    @api.onchange("booking_id")
    def _onchange_booking(self):
        if self.booking_id:
            self.package_id = self.booking_id.package_id
            self.customer_id = self.booking_id.customer_id
