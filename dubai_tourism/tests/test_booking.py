from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import tagged

from .common import TourismCommon


@tagged("post_install", "-at_install")
class TestTourismBooking(TourismCommon):

    def test_reference_auto_generated(self):
        booking = self._make_booking()
        self.assertTrue(booking.name.startswith("TB"))

    def test_basic_pricing_no_discount(self):
        booking = self._make_booking(adults=2, children=0)  # 2 * 200
        self.assertEqual(booking.group_size, 2)
        self.assertEqual(booking.amount_untaxed, 400.0)
        self.assertEqual(booking.discount_total, 0.0)
        self.assertEqual(booking.amount_total, 400.0)

    def test_family_discount_applies_with_children(self):
        booking = self._make_booking(adults=2, children=1)  # 400 + 100 = 500
        self.assertTrue(booking.has_young_children)
        self.assertEqual(booking.amount_untaxed, 500.0)
        self.assertEqual(booking.family_discount, 25.0)   # 5%
        self.assertEqual(booking.amount_total, 475.0)

    def test_group_discount_applies_at_threshold(self):
        booking = self._make_booking(adults=10, children=0)  # 2000
        self.assertTrue(booking.is_group)
        self.assertEqual(booking.group_discount, 200.0)   # 10%
        self.assertEqual(booking.amount_total, 1800.0)

    def test_family_and_group_discounts_stack(self):
        booking = self._make_booking(adults=9, children=1)  # 1800 + 100 = 1900, group size 10
        self.assertTrue(booking.is_group)
        self.assertTrue(booking.has_young_children)
        self.assertEqual(booking.family_discount, 95.0)    # 5% of 1900
        self.assertEqual(booking.group_discount, 190.0)    # 10% of 1900
        self.assertEqual(booking.amount_total, 1615.0)

    def test_capacity_is_enforced(self):
        small = self.env["tourism.tour.package"].create({
            "name": "Mini", "price_adult": 100.0, "capacity": 4,
        })
        with self.assertRaises(ValidationError):
            self._make_booking(adults=5, package=small)

    def test_state_machine_and_payment_gate(self):
        booking = self._make_booking()
        booking.action_confirm()
        self.assertEqual(booking.state, "confirmed")
        # Cannot complete before payment.
        with self.assertRaises(UserError):
            booking.action_complete()
        booking.action_register_payment()
        booking.action_complete()
        self.assertEqual(booking.state, "completed")

    def test_completed_cannot_be_cancelled(self):
        booking = self._make_booking(state="paid")
        booking.action_complete()
        with self.assertRaises(UserError):
            booking.action_cancel()

    def test_partner_total_spent(self):
        self._make_booking(adults=2, state="paid")        # 400 counts
        self._make_booking(adults=1, state="draft")       # excluded
        self.assertEqual(self.customer.tourism_total_spent, 400.0)
        self.assertEqual(self.customer.tourism_booking_count, 2)
