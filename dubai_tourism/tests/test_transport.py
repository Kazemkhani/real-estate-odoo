from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import tagged

from .common import TourismCommon


@tagged("post_install", "-at_install")
class TestTourismTransport(TourismCommon):

    def setUp(self):
        super().setUp()
        self.booking = self._make_booking(adults=4)

    def _assign(self, **kw):
        vals = {"booking_id": self.booking.id, "passenger_count": 4}
        vals.update(kw)
        return self.env["tourism.transport.assignment"].create(vals)

    def test_internal_requires_vehicle(self):
        with self.assertRaises(ValidationError):
            self._assign(transport_type="internal")  # no vehicle

    def test_internal_respects_vehicle_seats(self):
        small_van = self.env["tourism.vehicle"].create({
            "name": "Small Van", "vehicle_type": "van", "seats": 3,
        })
        with self.assertRaises(ValidationError):
            self._assign(transport_type="internal", vehicle_id=small_van.id, passenger_count=4)

    def test_external_requires_taxi_company(self):
        with self.assertRaises(ValidationError):
            self._assign(transport_type="external")  # no taxi company

    def test_commission_only_on_external(self):
        internal = self._assign(transport_type="internal", vehicle_id=self.bus.id, cost=500, commission_rate=15)
        self.assertEqual(internal.commission_amount, 0.0)
        external = self._assign(transport_type="external", taxi_company_id=self.taxi.id, cost=200, commission_rate=15)
        self.assertEqual(external.commission_amount, 30.0)  # 15% of 200

    def test_reference_and_booking_rollup(self):
        a = self._assign(transport_type="external", taxi_company_id=self.taxi.id, cost=100, commission_rate=10)
        self.assertTrue(a.name.startswith("TA"))
        self.assertEqual(self.booking.transport_count, 1)
        self.assertEqual(self.booking.transport_commission, 10.0)

    def test_trip_lifecycle_updates_vehicle(self):
        a = self._assign(transport_type="internal", vehicle_id=self.bus.id)
        a.action_start()
        self.assertEqual(a.state, "ongoing")
        self.assertEqual(self.bus.state, "on_trip")
        a.action_done()
        self.assertEqual(a.state, "done")
        self.assertEqual(self.bus.state, "available")

    def test_wizard_creates_assignment(self):
        wizard = self.env["tourism.assign.transport.wizard"].create({
            "booking_id": self.booking.id,
            "transport_type": "external",
            "taxi_company_id": self.taxi.id,
            "passenger_count": 4,
            "cost": 120,
            "commission_rate": 15,
        })
        wizard.action_assign()
        self.assertEqual(len(self.booking.transport_assignment_ids), 1)
        self.assertEqual(self.booking.transport_assignment_ids.commission_amount, 18.0)

    def test_wizard_validates_missing_vehicle(self):
        wizard = self.env["tourism.assign.transport.wizard"].create({
            "booking_id": self.booking.id,
            "transport_type": "internal",
            "passenger_count": 4,
        })
        with self.assertRaises(UserError):
            wizard.action_assign()
