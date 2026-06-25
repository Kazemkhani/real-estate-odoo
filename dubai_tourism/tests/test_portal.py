from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestTourismPortal(HttpCase):
    """The customer portal lists a logged-in customer's own bookings."""

    def test_portal_my_tours_page(self):
        partner = self.env["res.partner"].create({"name": "Portal Cust", "email": "pc@example.com"})
        self.env["res.users"].create({
            "name": "Portal Cust",
            "login": "pc@example.com",
            "password": "portalpw",
            "partner_id": partner.id,
            "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])],
        })
        package = self.env["tourism.tour.package"].create({"name": "Desert Tour", "price_adult": 100.0})
        booking = self.env["tourism.booking"].create({
            "customer_id": partner.id,
            "package_id": package.id,
            "departure_date": "2030-01-01",
            "adult_count": 2,
        })

        self.authenticate("pc@example.com", "portalpw")
        res = self.url_open("/my/tours")
        self.assertEqual(res.status_code, 200)
        self.assertIn(booking.name, res.text)
        self.assertIn("Desert Tour", res.text)

        # The detail page is reachable for the owner.
        detail = self.url_open("/my/tours/%d" % booking.id)
        self.assertEqual(detail.status_code, 200)
        self.assertIn(booking.name, detail.text)

    def test_portal_cannot_see_others_booking(self):
        owner = self.env["res.partner"].create({"name": "Owner", "email": "own@example.com"})
        other = self.env["res.partner"].create({"name": "Other", "email": "oth@example.com"})
        self.env["res.users"].create({
            "name": "Other", "login": "oth@example.com", "password": "pw2",
            "partner_id": other.id,
            "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])],
        })
        package = self.env["tourism.tour.package"].create({"name": "Private Tour", "price_adult": 100.0})
        booking = self.env["tourism.booking"].create({
            "customer_id": owner.id, "package_id": package.id,
            "departure_date": "2030-01-01", "adult_count": 1,
        })
        self.authenticate("oth@example.com", "pw2")
        # Not the owner -> redirected away from the detail page.
        res = self.url_open("/my/tours/%d" % booking.id, allow_redirects=False)
        self.assertIn(res.status_code, (301, 302, 303))
