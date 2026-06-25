from odoo.tests.common import TransactionCase, tagged, Form


@tagged("post_install", "-at_install")
class TestBookingFormFlow(TransactionCase):
    """Reproduce the UI 'New booking' flow exactly: Form() runs the form view's
    default_get + onchanges + create, catching errors a plain create() misses."""

    def test_new_booking_through_form(self):
        package = self.env["tourism.tour.package"].create({"name": "City", "price_adult": 200.0})
        customer = self.env["res.partner"].create({"name": "Walk-in"})
        form = Form(self.env["tourism.booking"])
        form.customer_id = customer
        form.package_id = package
        form.adult_count = 2
        booking = form.save()
        self.assertTrue(booking.name.startswith("TB"))
        self.assertEqual(booking.amount_total, 400.0)

    def test_new_booking_from_departure_through_form(self):
        package = self.env["tourism.tour.package"].create({"name": "Desert", "price_adult": 300.0})
        departure = self.env["tourism.departure"].create({
            "package_id": package.id, "departure_date": "2030-05-01", "capacity": 20,
        })
        customer = self.env["res.partner"].create({"name": "Group"})
        form = Form(self.env["tourism.booking"])
        form.departure_id = departure
        form.customer_id = customer
        form.adult_count = 3
        booking = form.save()
        self.assertEqual(booking.package_id, package)
