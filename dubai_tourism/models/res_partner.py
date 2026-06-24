from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_taxi_company = fields.Boolean(string="Taxi Company")
    tourism_booking_ids = fields.One2many("tourism.booking", "customer_id", string="Tour Bookings")
    tourism_booking_count = fields.Integer(compute="_compute_tourism_stats")
    tourism_total_spent = fields.Monetary(
        compute="_compute_tourism_stats", currency_field="company_currency_id"
    )
    company_currency_id = fields.Many2one(
        "res.currency", compute="_compute_company_currency", string="Company Currency"
    )

    def _compute_company_currency(self):
        for partner in self:
            partner.company_currency_id = partner.company_id.currency_id or self.env.company.currency_id

    @api.depends("tourism_booking_ids.state", "tourism_booking_ids.amount_total")
    def _compute_tourism_stats(self):
        for partner in self:
            bookings = partner.tourism_booking_ids
            partner.tourism_booking_count = len(bookings)
            paid = bookings.filtered(lambda b: b.state in ("paid", "completed"))
            partner.tourism_total_spent = sum(paid.mapped("amount_total"))

    def action_view_tourism_bookings(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Tour Bookings",
            "res_model": "tourism.booking",
            "view_mode": "list,form,calendar",
            "domain": [("customer_id", "=", self.id)],
            "context": {"default_customer_id": self.id},
        }
