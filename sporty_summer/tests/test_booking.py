from datetime import timedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import tagged

from .common import SportyCommon


@tagged("post_install", "-at_install")
class TestSportBooking(SportyCommon):

    def test_reference_is_auto_generated(self):
        booking = self._make_booking()
        self.assertNotEqual(booking.name, "New")
        self.assertTrue(booking.name.startswith("SB"))

    def test_duration_and_amount(self):
        booking = self._make_booking(hours=2)  # 2h @ 100/h
        self.assertEqual(booking.duration, 2.0)
        self.assertEqual(booking.amount_untaxed, 200.0)
        self.assertEqual(booking.amount_total, 200.0)

    def test_end_before_start_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.env["sport.booking"].create({
                "court_id": self.court.id,
                "customer_id": self.customer.id,
                "start_datetime": self.base,
                "end_datetime": self.base - timedelta(hours=1),
                "participant_count": 2,
            })

    def test_participant_limit_enforced(self):
        # Tennis allows max 4 participants per session.
        with self.assertRaises(ValidationError):
            self._make_booking(participants=5)

    def test_double_booking_is_rejected(self):
        self._make_booking(start=self.base, hours=2, state="confirmed")
        # Overlaps the first slot on the same court -> must be rejected on confirm.
        overlap = self._make_booking(start=self.base + timedelta(hours=1), hours=2)
        with self.assertRaises(ValidationError):
            overlap.action_confirm()

    def test_adjacent_slots_are_allowed(self):
        self._make_booking(start=self.base, hours=1, state="confirmed")
        # Starts exactly when the previous ends — no overlap.
        nxt = self._make_booking(start=self.base + timedelta(hours=1), hours=1)
        nxt.action_confirm()
        self.assertEqual(nxt.state, "confirmed")

    def test_draft_bookings_do_not_block_the_calendar(self):
        # Two draft bookings on the same slot are fine (they are only quotes).
        self._make_booking(start=self.base, hours=1)
        second = self._make_booking(start=self.base, hours=1, customer=self.customer2)
        self.assertEqual(second.state, "draft")

    def test_payment_gates_participation(self):
        booking = self._make_booking()
        booking.action_confirm()
        # Cannot mark as played before it is paid.
        with self.assertRaises(UserError):
            booking.action_play()
        booking.action_mark_paid()
        booking.action_play()
        self.assertEqual(booking.state, "done")

    def test_played_booking_cannot_be_cancelled(self):
        booking = self._make_booking(state="paid")
        booking.action_play()
        with self.assertRaises(UserError):
            booking.action_cancel()

    def test_loyalty_discount_for_frequent_visitor(self):
        # Five paid/played bookings flips the customer to frequent visitor (10% off).
        for i in range(5):
            self._make_booking(start=self.base + timedelta(days=i), hours=1, state="paid")
        self.assertTrue(self.customer.is_frequent_visitor)
        self.assertEqual(self.customer.loyalty_discount, 10.0)
        # A new booking for this customer now carries the discount.
        discounted = self._make_booking(start=self.base + timedelta(days=10), hours=1)
        self.assertEqual(discounted.amount_untaxed, 100.0)
        self.assertEqual(discounted.discount_amount, 10.0)
        self.assertEqual(discounted.amount_total, 90.0)
