from odoo.exceptions import ValidationError
from odoo.tests.common import tagged
from odoo.tools import mute_logger

from .common import SportyCommon


@tagged("post_install", "-at_install")
class TestCoaching(SportyCommon):

    def setUp(self):
        super().setUp()
        self.coach = self.env["res.partner"].create({"name": "Coach", "is_coach": True})
        self.coaching_class = self.env["sport.coaching.class"].create({
            "name": "Junior Camp",
            "sport_type_id": self.tennis.id,
            "coach_id": self.coach.id,
            "capacity": 2,
            "price": 200.0,
            "state": "open",
        })

    def _register(self, customer, state="confirmed"):
        return self.env["sport.class.registration"].create({
            "class_id": self.coaching_class.id,
            "customer_id": customer.id,
            "state": state,
        })

    def test_seats_tracking(self):
        self.assertEqual(self.coaching_class.seats_taken, 0)
        self.assertEqual(self.coaching_class.seats_available, 2)
        self._register(self.customer)
        self.assertEqual(self.coaching_class.seats_taken, 1)
        self.assertEqual(self.coaching_class.seats_available, 1)
        self.assertFalse(self.coaching_class.is_full)

    def test_first_come_first_served_capacity(self):
        self._register(self.customer)
        self._register(self.customer2)
        self.assertTrue(self.coaching_class.is_full)
        # A third confirmed registration must be rejected — class is full.
        third = self.env["res.partner"].create({"name": "Third"})
        with self.assertRaises(ValidationError):
            self._register(third)

    def test_draft_registrations_do_not_consume_seats(self):
        self._register(self.customer, state="draft")
        self._register(self.customer2, state="draft")
        self.assertEqual(self.coaching_class.seats_taken, 0)
        self.assertEqual(self.coaching_class.seats_available, 2)

    def test_registration_reference_generated(self):
        reg = self._register(self.customer, state="draft")
        self.assertTrue(reg.name.startswith("REG"))

    @mute_logger("odoo.sql_db")
    def test_duplicate_registration_blocked(self):
        self._register(self.customer, state="draft")
        # UNIQUE(class_id, customer_id) — the savepoint keeps the cursor usable
        # after the expected IntegrityError.
        with self.assertRaises(Exception), self.env.cr.savepoint():
            self._register(self.customer, state="draft")
