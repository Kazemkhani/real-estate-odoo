from odoo.tests.common import tagged

from .common import TourismCommon


@tagged("post_install", "-at_install")
class TestPackageAndReview(TourismCommon):

    def test_package_booking_stats(self):
        self._make_booking(adults=2, state="paid")        # 400
        self._make_booking(adults=3, state="completed")   # 600
        self._make_booking(adults=1, state="draft")       # excluded from revenue
        self.assertEqual(self.package.booking_count, 3)
        self.assertEqual(self.package.confirmed_revenue, 1000.0)
        self.assertEqual(self.package.traveller_count, 5)

    def test_average_rating(self):
        self.assertEqual(self.package.avg_rating, 0.0)
        self.env["tourism.review"].create({
            "package_id": self.package.id, "customer_id": self.customer.id, "rating": "5",
        })
        self.env["tourism.review"].create({
            "package_id": self.package.id, "customer_id": self.customer.id, "rating": "3",
        })
        self.assertEqual(self.package.review_count, 2)
        self.assertEqual(self.package.avg_rating, 4.0)

    def test_destination_popularity(self):
        # Confirmed/paid bookings count their travellers towards the destination.
        self._make_booking(adults=3, state="paid")
        self._make_booking(adults=2, state="draft")  # draft excluded
        self.assertEqual(self.destination.booking_count, 3)
