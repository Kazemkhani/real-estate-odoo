from odoo.exceptions import ValidationError
from odoo.tests.common import tagged

from .common import SportyCommon


@tagged("post_install", "-at_install")
class TestEquipment(SportyCommon):

    def setUp(self):
        super().setUp()
        self.racket = self.env["sport.equipment"].create({
            "name": "Tennis Racket",
            "sport_type_id": self.tennis.id,
            "total_quantity": 5,
        })

    def _loan(self, qty, state="loaned", customer=None):
        return self.env["sport.equipment.loan"].create({
            "equipment_id": self.racket.id,
            "customer_id": (customer or self.customer).id,
            "quantity": qty,
            "state": state,
        })

    def test_stock_tracking(self):
        self.assertEqual(self.racket.available_quantity, 5)
        self._loan(2)
        self.assertEqual(self.racket.loaned_quantity, 2)
        self.assertEqual(self.racket.available_quantity, 3)

    def test_return_replenishes_stock(self):
        loan = self._loan(3)
        self.assertEqual(self.racket.available_quantity, 2)
        loan.action_return()
        self.assertEqual(loan.state, "returned")
        self.assertTrue(loan.return_date)
        self.assertEqual(self.racket.available_quantity, 5)

    def test_lost_equipment_leaves_circulation(self):
        loan = self._loan(1)
        loan.action_mark_lost()
        self.assertEqual(self.racket.lost_quantity, 1)
        # Lost items reduce on-hand stock permanently (until restocked).
        self.assertEqual(self.racket.available_quantity, 4)

    def test_cannot_over_loan(self):
        self._loan(4)  # 4 of 5 out
        with self.assertRaises(ValidationError):
            self._loan(3)  # would need 7 of 5

    def test_loan_reference_generated(self):
        loan = self._loan(1)
        self.assertTrue(loan.name.startswith("EL"))
