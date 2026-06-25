"""Full A–Z audit: every model's form-create flow (as the UI does it), the QWeb
report, and role-based security. These guard against the whole class of
'can't create a record from the form' defects."""
from odoo.tests.common import TransactionCase, tagged, Form, new_test_user


@tagged("post_install", "-at_install")
class TestFormCreateAllModels(TransactionCase):
    """Create every model through Form() — runs default_get + onchanges + save,
    exactly like clicking 'New' and 'Save' in the web client."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Audit Partner"})
        cls.package = cls.env["tourism.tour.package"].create({"name": "Audit Pkg", "price_adult": 200.0})

    def test_form_destination(self):
        f = Form(self.env["tourism.destination"]); f.name = "Burj"; self.assertTrue(f.save())

    def test_form_package(self):
        f = Form(self.env["tourism.tour.package"]); f.name = "City Tour"
        rec = f.save()
        self.assertEqual(rec.effective_price_adult, rec.price_adult)

    def test_form_package_with_itinerary(self):
        f = Form(self.env["tourism.tour.package"]); f.name = "With Plan"
        with f.itinerary_line_ids.new() as line:
            line.title = "Day 1 — Downtown"
        self.assertTrue(f.save().itinerary_line_ids)

    def test_form_departure(self):
        f = Form(self.env["tourism.departure"]); f.package_id = self.package
        rec = f.save()
        self.assertTrue(rec.name)
        self.assertEqual(rec.seats_available, rec.capacity)

    def test_form_vehicle(self):
        f = Form(self.env["tourism.vehicle"]); f.name = "Coach 9"; f.seats = 30
        self.assertEqual(f.save().state, "available")

    def test_form_review(self):
        f = Form(self.env["tourism.review"]); f.package_id = self.package; f.customer_id = self.partner
        f.rating = "4"
        self.assertEqual(f.save().rating, "4")

    def test_form_booking_plain(self):
        f = Form(self.env["tourism.booking"]); f.customer_id = self.partner; f.package_id = self.package
        f.adult_count = 2
        b = f.save()
        self.assertTrue(b.package_id and b.name.startswith("TB"))

    def test_form_booking_from_departure(self):
        dep = self.env["tourism.departure"].create({
            "package_id": self.package.id, "departure_date": "2030-09-01", "capacity": 20})
        f = Form(self.env["tourism.booking"]); f.departure_id = dep; f.customer_id = self.partner
        f.adult_count = 2
        b = f.save()
        self.assertEqual(b.package_id, self.package)         # the bug we fixed
        self.assertEqual(str(b.departure_date), "2030-09-01")

    def test_form_transport_internal(self):
        booking = self.env["tourism.booking"].create({
            "customer_id": self.partner.id, "package_id": self.package.id,
            "departure_date": "2030-09-01", "adult_count": 3})
        vehicle = self.env["tourism.vehicle"].create({"name": "Van", "vehicle_type": "van", "seats": 14})
        f = Form(self.env["tourism.transport.assignment"])
        f.booking_id = booking
        f.vehicle_id = vehicle
        f.passenger_count = 3
        self.assertEqual(f.save().transport_type, "internal")


@tagged("post_install", "-at_install")
class TestReportAndSecurity(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "R Partner"})
        cls.package = cls.env["tourism.tour.package"].create({"name": "R Pkg", "price_adult": 200.0, "price_child": 100.0})
        cls.env["tourism.itinerary.line"].create({"package_id": cls.package.id, "title": "Day 1"})

    def test_voucher_report_renders(self):
        guide = self.env["res.partner"].create({"name": "Guide", "is_tour_guide": True})
        dep = self.env["tourism.departure"].create({
            "package_id": self.package.id, "departure_date": "2030-10-01", "guide_id": guide.id, "capacity": 20})
        booking = self.env["tourism.booking"].create({
            "customer_id": self.partner.id, "package_id": self.package.id, "departure_id": dep.id,
            "departure_date": "2030-10-01", "adult_count": 2, "child_count": 1})  # triggers discount + itinerary + guide
        html, _ = self.env["ir.actions.report"]._render_qweb_html(
            "dubai_tourism.report_tourism_booking", booking.ids)
        self.assertIn(booking.name.encode(), html)
        self.assertIn(b"Itinerary", html)

    def test_agent_creates_and_sees_only_own(self):
        agent = new_test_user(self.env, login="agent_audit",
                              groups="dubai_tourism.group_tourism_agent")
        other_agent = new_test_user(self.env, login="agent_other",
                                    groups="dubai_tourism.group_tourism_agent")
        booking = self.env["tourism.booking"].with_user(agent).create({
            "customer_id": self.partner.id, "package_id": self.package.id,
            "departure_date": "2030-10-01", "adult_count": 1})
        # The owner sees it...
        self.assertIn(booking, self.env["tourism.booking"].with_user(agent).search([]))
        # ...another agent does not (record rule).
        self.assertNotIn(booking, self.env["tourism.booking"].with_user(other_agent).search([]))

    def test_report_measures_are_aggregatable(self):
        """Every field used as a graph/pivot measure must be stored, or the report
        crashes on aggregation (the Package Performance pivot 'Oops!' bug)."""
        self.env["tourism.tour.package"]._read_group(
            [], ["category"],
            ["confirmed_revenue:sum", "booking_count:sum", "traveller_count:sum", "avg_rating:avg"])
        self.env["tourism.destination"]._read_group([], [], ["booking_count:sum"])
        self.env["tourism.transport.assignment"]._read_group(
            [], ["transport_type"], ["passenger_count:sum", "commission_amount:sum"])
        self.env["tourism.vehicle"]._read_group(
            [], [], ["trips_done:sum", "passengers_transported:sum", "utilization:avg"])
        self.env["tourism.booking"]._read_group(
            [], ["package_id"], ["amount_total:sum", "group_size:sum"])

    def test_manager_sees_all(self):
        manager = new_test_user(self.env, login="mgr_audit",
                                groups="dubai_tourism.group_tourism_manager")
        agent = new_test_user(self.env, login="agent_audit2",
                              groups="dubai_tourism.group_tourism_agent")
        booking = self.env["tourism.booking"].with_user(agent).create({
            "customer_id": self.partner.id, "package_id": self.package.id,
            "departure_date": "2030-10-01", "adult_count": 1})
        self.assertIn(booking, self.env["tourism.booking"].with_user(manager).search([]))
