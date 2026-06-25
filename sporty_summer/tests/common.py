from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase


class SportyCommon(TransactionCase):
    """Shared fixtures: one sport, one court, a couple of customers."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tennis = cls.env["sport.type"].create({
            "name": "Tennis",
            "max_participants": 4,
            "default_duration": 1.0,
        })
        cls.court = cls.env["sport.court"].create({
            "name": "Court A",
            "sport_type_id": cls.tennis.id,
            "hourly_price": 100.0,
        })
        cls.customer = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.customer2 = cls.env["res.partner"].create({"name": "Second Customer"})
        # A fixed, far-future base time keeps the slots deterministic.
        cls.base = datetime(2030, 1, 1, 10, 0, 0)

    def _make_booking(self, start=None, hours=1, court=None, customer=None, participants=2, **kw):
        start = start or self.base
        vals = {
            "court_id": (court or self.court).id,
            "customer_id": (customer or self.customer).id,
            "start_datetime": start,
            "end_datetime": start + timedelta(hours=hours),
            "participant_count": participants,
        }
        vals.update(kw)
        return self.env["sport.booking"].create(vals)
