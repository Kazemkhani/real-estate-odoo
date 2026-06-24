from odoo.tests.common import TransactionCase


class TourismCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.destination = cls.env["tourism.destination"].create({"name": "Burj Khalifa"})
        cls.package = cls.env["tourism.tour.package"].create({
            "name": "City Tour",
            "price_adult": 200.0,
            "price_child": 100.0,
            "capacity": 30,
            "destination_ids": [(6, 0, [cls.destination.id])],
        })
        cls.customer = cls.env["res.partner"].create({"name": "Tourist One"})
        cls.taxi = cls.env["res.partner"].create({"name": "Taxi Co", "is_taxi_company": True})
        cls.bus = cls.env["tourism.vehicle"].create({
            "name": "Coach 1", "vehicle_type": "bus", "seats": 30,
        })

    def _make_booking(self, adults=2, children=0, package=None, customer=None, **kw):
        vals = {
            "customer_id": (customer or self.customer).id,
            "package_id": (package or self.package).id,
            "departure_date": "2030-01-01",
            "adult_count": adults,
            "child_count": children,
        }
        vals.update(kw)
        return self.env["tourism.booking"].create(vals)
