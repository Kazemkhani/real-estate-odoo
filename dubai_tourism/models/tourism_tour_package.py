from odoo import api, fields, models


class TourismTourPackage(models.Model):
    """A sellable tour product — a set of destinations, a duration and per-person
    pricing. Carries live commercial stats (bookings, revenue, rating)."""

    _name = "tourism.tour.package"
    _description = "Tour Package"
    _order = "sequence, name"

    name = fields.Char(required=True)
    code = fields.Char()
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    category = fields.Selection(
        selection=[
            ("city", "City Tour"),
            ("desert", "Desert Safari"),
            ("cruise", "Cruise"),
            ("cultural", "Cultural & Heritage"),
            ("adventure", "Adventure"),
            ("luxury", "Luxury"),
        ],
        default="city",
        required=True,
    )
    description = fields.Text()
    image = fields.Image("Cover", max_width=1920, max_height=1920)
    color = fields.Integer()

    destination_ids = fields.Many2many(
        "tourism.destination", "tourism_package_destination_rel",
        "package_id", "destination_id", string="Destinations",
    )
    duration_days = fields.Integer(string="Duration (days)", default=1)
    capacity = fields.Integer(
        string="Max Travellers / Departure", default=20,
        help="Maximum group size accepted on a single departure. 0 means unlimited.",
    )

    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)
    price_adult = fields.Monetary(string="Price / Adult", required=True, default=200.0)
    price_child = fields.Monetary(string="Price / Child", default=100.0)

    # Marketing: featured packages can carry a promotional adult price that
    # overrides the standard one on new bookings.
    is_featured = fields.Boolean(string="Featured")
    promo_price = fields.Monetary(string="Promo Price / Adult",
                                  help="If set on a featured package, used instead of the adult price.")
    effective_price_adult = fields.Monetary(compute="_compute_effective_price", store=True)

    @api.depends("is_featured", "promo_price", "price_adult")
    def _compute_effective_price(self):
        for package in self:
            if package.is_featured and package.promo_price > 0:
                package.effective_price_adult = package.promo_price
            else:
                package.effective_price_adult = package.price_adult

    booking_ids = fields.One2many("tourism.booking", "package_id", string="Bookings")
    review_ids = fields.One2many("tourism.review", "package_id", string="Reviews")
    itinerary_line_ids = fields.One2many("tourism.itinerary.line", "package_id", string="Itinerary")
    departure_ids = fields.One2many("tourism.departure", "package_id", string="Departures")
    departure_count = fields.Integer(compute="_compute_departure_count")

    @api.depends("departure_ids")
    def _compute_departure_count(self):
        for package in self:
            package.departure_count = len(package.departure_ids)

    # stored so it can be used as a measure in graph/pivot (read_group needs a column)
    booking_count = fields.Integer(compute="_compute_booking_stats", store=True)
    confirmed_revenue = fields.Monetary(compute="_compute_booking_stats", store=True)
    traveller_count = fields.Integer(compute="_compute_booking_stats", store=True)
    avg_rating = fields.Float(compute="_compute_rating", store=True, aggregator="avg")
    review_count = fields.Integer(compute="_compute_rating")

    _check_prices = models.Constraint(
        "CHECK(price_adult >= 0 AND price_child >= 0)",
        "Prices cannot be negative.",
    )
    _check_capacity = models.Constraint(
        "CHECK(capacity >= 0)",
        "Capacity cannot be negative.",
    )

    @api.depends("booking_ids", "booking_ids.state", "booking_ids.amount_total", "booking_ids.group_size")
    def _compute_booking_stats(self):
        for package in self:
            billable = package.booking_ids.filtered(lambda b: b.state in ("paid", "completed"))
            package.booking_count = len(package.booking_ids)
            package.confirmed_revenue = sum(billable.mapped("amount_total"))
            package.traveller_count = sum(billable.mapped("group_size"))

    @api.depends("review_ids.rating")
    def _compute_rating(self):
        for package in self:
            ratings = [int(r.rating) for r in package.review_ids if r.rating]
            package.review_count = len(ratings)
            package.avg_rating = (sum(ratings) / len(ratings)) if ratings else 0.0

    def action_view_bookings(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Bookings",
            "res_model": "tourism.booking",
            "view_mode": "list,form,calendar",
            "domain": [("package_id", "=", self.id)],
            "context": {"default_package_id": self.id},
        }

    def action_view_reviews(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Reviews",
            "res_model": "tourism.review",
            "view_mode": "list,form",
            "domain": [("package_id", "=", self.id)],
            "context": {"default_package_id": self.id},
        }

    def action_view_departures(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Departures",
            "res_model": "tourism.departure",
            "view_mode": "list,calendar,form",
            "domain": [("package_id", "=", self.id)],
            "context": {"default_package_id": self.id},
        }
