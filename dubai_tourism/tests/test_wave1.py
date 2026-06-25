from odoo.tests.common import tagged

from .common import TourismCommon


@tagged("post_install", "-at_install")
class TestWave1(TourismCommon):

    def test_featured_promo_price_applies(self):
        self.package.write({"is_featured": True, "promo_price": 150.0})
        self.assertEqual(self.package.effective_price_adult, 150.0)
        booking = self._make_booking(adults=2, children=0)  # 2 * 150
        self.assertEqual(booking.amount_untaxed, 300.0)

    def test_promo_ignored_when_not_featured(self):
        # A promo price only applies on a featured package.
        self.package.write({"is_featured": False, "promo_price": 150.0})
        self.assertEqual(self.package.effective_price_adult, 200.0)
        booking = self._make_booking(adults=2)
        self.assertEqual(booking.amount_untaxed, 400.0)

    def test_fleet_utilization(self):
        van = self.env["tourism.vehicle"].create({"name": "Van", "vehicle_type": "van", "seats": 10})
        booking = self._make_booking(adults=5)
        assignment = self.env["tourism.transport.assignment"].create({
            "booking_id": booking.id,
            "transport_type": "internal",
            "vehicle_id": van.id,
            "passenger_count": 5,
        })
        self.assertEqual(van.trips_done, 0)
        assignment.action_start()
        assignment.action_done()
        self.assertEqual(van.trips_done, 1)
        self.assertEqual(van.passengers_transported, 5)
        self.assertEqual(van.utilization, 50.0)  # 5 of 10 seats
