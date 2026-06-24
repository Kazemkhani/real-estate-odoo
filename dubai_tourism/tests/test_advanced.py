from datetime import date, timedelta

from odoo.exceptions import ValidationError
from odoo.tests.common import tagged

from .common import TourismCommon


@tagged("post_install", "-at_install")
class TestConfigurableDiscounts(TourismCommon):

    def _set(self, key, value):
        self.env["ir.config_parameter"].sudo().set_param(key, value)

    def test_family_discount_is_configurable(self):
        self._set("dubai_tourism.family_discount", "20")
        booking = self._make_booking(adults=2, children=1)  # subtotal 500
        self.assertEqual(booking.family_discount, 100.0)     # 20% now
        self.assertEqual(booking.amount_total, 400.0)

    def test_group_threshold_is_configurable(self):
        self._set("dubai_tourism.group_threshold", "3")
        booking = self._make_booking(adults=3, children=0)   # 600, now a group
        self.assertTrue(booking.is_group)
        self.assertEqual(booking.group_discount, 60.0)       # default 10%


@tagged("post_install", "-at_install")
class TestDepartures(TourismCommon):

    def _departure(self, capacity=10, **kw):
        vals = {
            "package_id": self.package.id,
            "departure_date": "2030-06-01",
            "capacity": capacity,
        }
        vals.update(kw)
        return self.env["tourism.departure"].create(vals)

    def test_seat_tracking(self):
        dep = self._departure(capacity=10)
        self.assertEqual(dep.seats_available, 10)
        self._make_booking(adults=4, departure_id=dep.id)
        self.assertEqual(dep.seats_booked, 4)
        self.assertEqual(dep.seats_available, 6)
        self.assertFalse(dep.is_full)

    def test_overbooking_is_rejected(self):
        dep = self._departure(capacity=5)
        self._make_booking(adults=4, departure_id=dep.id)
        with self.assertRaises(ValidationError):
            self._make_booking(adults=3, departure_id=dep.id)  # 4 + 3 > 5

    def test_cancelled_booking_frees_seats(self):
        dep = self._departure(capacity=5)
        b1 = self._make_booking(adults=4, departure_id=dep.id)
        b1.action_cancel()
        # Now a new 4-seat booking fits again.
        b2 = self._make_booking(adults=4, departure_id=dep.id)
        self.assertEqual(dep.seats_booked, 4)
        self.assertEqual(b2.state, "draft")

    def test_booking_package_must_match_departure(self):
        other = self.env["tourism.tour.package"].create({"name": "Other", "price_adult": 100})
        dep = self._departure(capacity=10)
        with self.assertRaises(ValidationError):
            self._make_booking(adults=2, departure_id=dep.id, package=other)

    def test_departure_with_paid_bookings_cannot_cancel(self):
        from odoo.exceptions import UserError
        dep = self._departure(capacity=10)
        self._make_booking(adults=2, departure_id=dep.id, state="paid")
        with self.assertRaises(UserError):
            dep.action_cancel()


@tagged("post_install", "-at_install")
class TestAutomation(TourismCommon):

    def test_auto_email_on_confirm(self):
        self.env["ir.config_parameter"].sudo().set_param("dubai_tourism.auto_email", "True")
        self.customer.email = "tourist@example.com"
        booking = self._make_booking()
        before = self.env["mail.mail"].search_count([])
        booking.action_confirm()  # should queue a confirmation email, never raise
        after = self.env["mail.mail"].search_count([])
        self.assertGreater(after, before)

    def test_no_email_when_disabled(self):
        self.env["ir.config_parameter"].sudo().set_param("dubai_tourism.auto_email", "")
        self.customer.email = "tourist@example.com"
        booking = self._make_booking()
        before = self.env["mail.mail"].search_count([])
        booking.action_confirm()
        self.assertEqual(self.env["mail.mail"].search_count([]), before)

    def test_cron_cancels_overdue_unpaid(self):
        self.env["ir.config_parameter"].sudo().set_param("dubai_tourism.auto_cancel_days", "1")
        past = self.env["tourism.booking"].create({
            "customer_id": self.customer.id,
            "package_id": self.package.id,
            "departure_date": date(2000, 1, 1),
            "adult_count": 2,
        })
        future = self._make_booking(adults=2, departure_date=date.today() + timedelta(days=30))
        self.env["tourism.booking"]._cron_cancel_overdue_unpaid()
        self.assertEqual(past.state, "cancelled")
        self.assertEqual(future.state, "draft")

    def test_cron_disabled_by_default(self):
        self.env["ir.config_parameter"].sudo().set_param("dubai_tourism.auto_cancel_days", "0")
        past = self.env["tourism.booking"].create({
            "customer_id": self.customer.id,
            "package_id": self.package.id,
            "departure_date": date(2000, 1, 1),
            "adult_count": 2,
        })
        self.env["tourism.booking"]._cron_cancel_overdue_unpaid()
        self.assertEqual(past.state, "draft")  # untouched when disabled
