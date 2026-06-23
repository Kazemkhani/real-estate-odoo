from odoo import api, fields, models

# A customer becomes a "frequent visitor" once they reach this many real visits
# (paid or played bookings), which unlocks an automatic loyalty discount.
FREQUENT_VISITOR_THRESHOLD = 5
LOYALTY_DISCOUNT_PERCENT = 10.0


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_coach = fields.Boolean(string="Is a Coach")
    booking_ids = fields.One2many("sport.booking", "customer_id", string="Bookings")
    booking_count = fields.Integer(compute="_compute_loyalty", store=True)
    is_frequent_visitor = fields.Boolean(
        string="Frequent Visitor", compute="_compute_loyalty", store=True
    )
    loyalty_discount = fields.Float(
        string="Loyalty Discount (%)", compute="_compute_loyalty", store=True
    )

    @api.depends("booking_ids.state")
    def _compute_loyalty(self):
        for partner in self:
            visits = len(partner.booking_ids.filtered(lambda b: b.state in ("paid", "done")))
            partner.booking_count = visits
            partner.is_frequent_visitor = visits >= FREQUENT_VISITOR_THRESHOLD
            partner.loyalty_discount = LOYALTY_DISCOUNT_PERCENT if partner.is_frequent_visitor else 0.0
