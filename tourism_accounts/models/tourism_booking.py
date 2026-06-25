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
        family/group discount, with the company's default sales tax applied."""
        self.ensure_one()
        # Apply the company's default sale tax (if configured) to every line.
        tax = self.company_id.account_sale_tax_id
        tax_cmd = [Command.set(tax.ids)] if tax else False

        def line(name, qty, price):
            vals = {"name": name, "quantity": qty, "price_unit": price}
            if tax_cmd:
                vals["tax_ids"] = tax_cmd
            return Command.create(vals)

        lines = [line("%s — Adults (%d)" % (self.package_id.name, self.adult_count),
                      self.adult_count or 1, self.package_id.effective_price_adult)]
        if self.child_count:
            lines.append(line("%s — Children (%d)" % (self.package_id.name, self.child_count),
                              self.child_count, self.package_id.price_child))
        if self.discount_total:
            lines.append(line("Family / group discount", 1, -self.discount_total))
        return self.env["account.move"].create({
            "partner_id": self.customer_id.id,
            "move_type": "out_invoice",
            "invoice_origin": self.name,
            # Bill in the booking's currency (defaults to the company currency).
            "currency_id": (self.currency_id or self.company_id.currency_id).id,
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
