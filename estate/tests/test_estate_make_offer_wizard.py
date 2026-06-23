from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .common import EstateCommon


@tagged("post_install", "-at_install")
class TestEstateMakeOfferWizard(EstateCommon):
    """The TransientModel 'Make an Offer' dialog."""

    def test_wizard_creates_offer_on_property(self):
        prop = self._make_property()
        wizard = self.env["estate.make.offer.wizard"].create({
            "property_id": prop.id,
            "partner_id": self.buyer.id,
            "price": 97000,
            "validity": 14,
        })
        wizard.action_submit()
        self.assertEqual(len(prop.offer_ids), 1)
        offer = prop.offer_ids
        self.assertEqual(offer.price, 97000)
        self.assertEqual(offer.partner_id, self.buyer)
        self.assertEqual(prop.state, "offer_received")

    def test_wizard_rejects_non_positive_price(self):
        prop = self._make_property()
        wizard = self.env["estate.make.offer.wizard"].create({
            "property_id": prop.id,
            "partner_id": self.buyer.id,
            "price": 0,
        })
        with self.assertRaises(UserError):
            wizard.action_submit()
