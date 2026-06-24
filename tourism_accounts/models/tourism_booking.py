from odoo import Command, fields, models


class TourismBooking(models.Model):
    # Extend the booking defined in the 'dubai_tourism' module.
    _inherit = "tourism.booking"

    invoice_id = fields.Many2one("account.move", string="Invoice", copy=False, readonly=True)

    def action_register_payment(self):
        # Run the original payment logic (state -> paid, receipt email), then bill.
        res = super().action_register_payment()
        for booking in self:
            if booking.customer_id and not booking.invoice_id:
                booking.invoice_id = booking._create_customer_invoice()
        return res

    def _create_customer_invoice(self):
        """Create a draft customer invoice itemising adults, children and any
        family/group discount."""
        self.ensure_one()
        lines = [Command.create({
            "name": "%s — Adults (%d)" % (self.package_id.name, self.adult_count),
            "quantity": self.adult_count or 1,
            "price_unit": self.package_id.price_adult,
        })]
        if self.child_count:
            lines.append(Command.create({
                "name": "%s — Children (%d)" % (self.package_id.name, self.child_count),
                "quantity": self.child_count,
                "price_unit": self.package_id.price_child,
            }))
        if self.discount_total:
            lines.append(Command.create({
                "name": "Family / group discount",
                "quantity": 1,
                "price_unit": -self.discount_total,
            }))
        return self.env["account.move"].create({
            "partner_id": self.customer_id.id,
            "move_type": "out_invoice",
            "invoice_origin": self.name,
            "invoice_line_ids": lines,
        })

    def action_view_invoice(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Invoice",
            "res_model": "account.move",
            "view_mode": "form",
            "res_id": self.invoice_id.id,
        }
