from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests.common import tagged


@tagged("post_install", "-at_install")
class TestTourismInvoice(AccountTestInvoicingCommon):
    """Paying a tour booking raises a customer invoice. Built on
    AccountTestInvoicingCommon so a chart of accounts / journals exist."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # The accounting test user isn't a Dubai Tourism user, so create the
        # tourism records as sudo; the invoicing assertions below are unaffected.
        cls.package = cls.env["tourism.tour.package"].sudo().create({
            "name": "City Tour",
            "price_adult": 200.0,
            "price_child": 100.0,
            "capacity": 30,
        })

    def _booking(self, adults=2, children=0):
        return self.env["tourism.booking"].sudo().create({
            "customer_id": self.partner_a.id,
            "package_id": self.package.id,
            "departure_date": "2030-01-01",
            "adult_count": adults,
            "child_count": children,
        })

    def test_payment_creates_invoice(self):
        booking = self._booking(adults=2, children=1)  # 2*200 + 100 = 500, family 5% = 25
        booking.action_register_payment()
        self.assertTrue(booking.invoice_id, "An invoice should be created on payment")
        self.assertEqual(booking.invoice_id.move_type, "out_invoice")
        self.assertEqual(booking.invoice_id.partner_id, self.partner_a)
        # Adults line + children line + discount line
        self.assertEqual(len(booking.invoice_id.invoice_line_ids), 3)

    def test_invoice_origin_and_simple_line(self):
        booking = self._booking(adults=2)  # no children, no discount -> one line
        booking.action_register_payment()
        invoice = booking.invoice_id
        self.assertEqual(invoice.invoice_origin, booking.name)
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        line = invoice.invoice_line_ids
        self.assertEqual(line.quantity, 2)
        self.assertEqual(line.price_unit, 200.0)
