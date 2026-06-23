from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests.common import tagged


@tagged("post_install", "-at_install")
class TestEstateAccounts(AccountTestInvoicingCommon):
    """Selling a property must raise a customer invoice for the buyer.

    Builds on AccountTestInvoicingCommon so a chart of accounts / journals
    exist and account.move records can be created in the test database.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.estate_property = cls.env["estate.property"].create({
            "name": "Billable Villa",
            "expected_price": 200000.0,
        })
        cls.offer = cls.env["estate.property.offer"].create({
            "property_id": cls.estate_property.id,
            "partner_id": cls.partner_a.id,
            "price": 200000.0,
        })
        cls.offer.accept_offer()  # sets buyer + selling_price = 200000

    def test_selling_creates_customer_invoice(self):
        invoices_before = self.env["account.move"].search([
            ("partner_id", "=", self.partner_a.id),
            ("move_type", "=", "out_invoice"),
        ])
        self.estate_property.sell_property()
        invoices_after = self.env["account.move"].search([
            ("partner_id", "=", self.partner_a.id),
            ("move_type", "=", "out_invoice"),
        ])
        new_invoices = invoices_after - invoices_before
        self.assertEqual(len(new_invoices), 1, "Selling must create exactly one invoice")

        invoice = new_invoices
        self.assertEqual(invoice.move_type, "out_invoice")
        self.assertEqual(len(invoice.invoice_line_ids), 2, "Commission line + admin fee line")

        # 6% commission on a 200000 sale = 12000, plus a flat 100 admin fee.
        prices = sorted(invoice.invoice_line_ids.mapped("price_unit"))
        self.assertEqual(prices, [100.0, 12000.0])

    def test_no_invoice_when_property_has_no_buyer(self):
        prop = self.env["estate.property"].create({
            "name": "Direct Sale",
            "expected_price": 50000.0,
        })
        before = self.env["account.move"].search_count([("move_type", "=", "out_invoice")])
        prop.sell_property()  # no buyer_id -> bridge skips invoicing
        after = self.env["account.move"].search_count([("move_type", "=", "out_invoice")])
        self.assertEqual(before, after, "No buyer means no invoice should be created")
