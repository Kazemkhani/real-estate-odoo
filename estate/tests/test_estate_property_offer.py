from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .common import EstateCommon


@tagged("post_install", "-at_install")
class TestEstatePropertyOffer(EstateCommon):
    """Offer negotiation flow, deadline maths and the expiry cron."""

    def test_creating_offer_moves_property_to_offer_received(self):
        prop = self._make_property()
        self.assertEqual(prop.state, "new")
        self._make_offer(prop)
        self.assertEqual(prop.state, "offer_received")

    def test_accept_offer_locks_price_buyer_and_state(self):
        prop = self._make_property()
        offer = self._make_offer(prop, price=95000)
        offer.accept_offer()
        self.assertEqual(offer.state, "accepted")
        self.assertEqual(prop.state, "offer_accepted")
        self.assertEqual(prop.selling_price, 95000)
        self.assertEqual(prop.buyer_id, self.buyer)

    def test_accepting_one_offer_auto_refuses_the_others(self):
        prop = self._make_property()
        low = self._make_offer(prop, partner=self.other_buyer, price=91000)
        high = self._make_offer(prop, partner=self.buyer, price=96000)
        high.accept_offer()
        self.assertEqual(high.state, "accepted")
        self.assertEqual(low.state, "refused", "Competing offers must be auto-refused on accept")

    def test_cannot_accept_a_refused_offer(self):
        prop = self._make_property()
        offer = self._make_offer(prop)
        offer.refuse_offer()
        with self.assertRaises(UserError):
            offer.accept_offer()

    def test_cannot_accept_two_offers_on_same_property(self):
        prop = self._make_property()
        first = self._make_offer(prop, partner=self.buyer, price=95000)
        second = self._make_offer(prop, partner=self.other_buyer, price=96000)
        first.accept_offer()
        with self.assertRaises(UserError):
            second.accept_offer()

    # --- Deadline compute / inverse ---------------------------------------
    def test_deadline_computed_from_validity(self):
        prop = self._make_property()
        offer = self._make_offer(prop, validity=10)
        base = fields.Date.to_date(offer.create_date)
        self.assertEqual(offer.date_deadline, base + relativedelta(days=10))

    def test_setting_deadline_inverts_to_validity(self):
        prop = self._make_property()
        offer = self._make_offer(prop, validity=7)
        base = fields.Date.to_date(offer.create_date)
        offer.date_deadline = base + relativedelta(days=20)
        self.assertEqual(offer.validity, 20)

    # --- Scheduled expiry (regression guard for the stored-field fix) ------
    def test_cron_expires_only_pending_past_offers(self):
        prop = self._make_property()
        # Pending offer already past its deadline (validity in the past).
        expired = self._make_offer(prop, partner=self.buyer, price=92000, validity=-1)
        # Pending offer still in the future.
        live = self._make_offer(prop, partner=self.other_buyer, price=93000, validity=10)

        # This search()-based cron only works because date_deadline is stored.
        self.env["estate.property.offer"]._cron_expire_offers()

        self.assertEqual(expired.state, "refused", "Past pending offer should be expired")
        self.assertFalse(live.state, "Future pending offer must be left untouched")
