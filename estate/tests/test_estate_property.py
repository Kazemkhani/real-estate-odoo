from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import tagged

from .common import EstateCommon


@tagged("post_install", "-at_install")
class TestEstateProperty(EstateCommon):
    """Lifecycle, computed fields and guard rails on estate.property."""

    # --- Computed fields ---------------------------------------------------
    def test_total_area_without_garden(self):
        prop = self._make_property(living_area=100, has_garden=False, garden_area=50)
        self.assertEqual(prop.total_area, 100, "Garden area must be ignored when has_garden is False")

    def test_total_area_with_garden(self):
        prop = self._make_property(living_area=100, has_garden=True, garden_area=50)
        self.assertEqual(prop.total_area, 150, "Total area must add living + garden when has_garden is True")

    def test_best_price_and_offer_count(self):
        prop = self._make_property()
        self.assertEqual(prop.best_price, 0.0)
        self.assertEqual(prop.offer_count, 0)
        self._make_offer(prop, price=90000)
        self._make_offer(prop, partner=self.other_buyer, price=95000)
        self.assertEqual(prop.best_price, 95000.0, "Best price must be the highest offer")
        self.assertEqual(prop.offer_count, 2)

    # --- State machine -----------------------------------------------------
    def test_sell_property(self):
        prop = self._make_property()
        prop.sell_property()
        self.assertEqual(prop.state, "sold")

    def test_cannot_sell_cancelled_property(self):
        prop = self._make_property()
        prop.cancel_property()
        with self.assertRaises(UserError):
            prop.sell_property()

    def test_cannot_cancel_sold_property(self):
        prop = self._make_property()
        prop.sell_property()
        with self.assertRaises(UserError):
            prop.cancel_property()

    # --- Constraints & guards ---------------------------------------------
    def test_selling_price_below_90_percent_is_rejected(self):
        prop = self._make_property(expected_price=100000)
        offer = self._make_offer(prop, price=80000)  # 80% of expected
        with self.assertRaises(ValidationError):
            offer.accept_offer()

    def test_selling_price_at_90_percent_is_accepted(self):
        prop = self._make_property(expected_price=100000)
        offer = self._make_offer(prop, price=90000)  # exactly 90%
        offer.accept_offer()
        self.assertEqual(prop.selling_price, 90000)

    def test_new_property_can_be_deleted(self):
        prop = self._make_property()
        prop.unlink()  # must not raise

    def test_property_with_offer_cannot_be_deleted(self):
        prop = self._make_property()
        self._make_offer(prop)  # moves the property to "offer_received"
        self.assertEqual(prop.state, "offer_received")
        with self.assertRaises(UserError):
            prop.unlink()
