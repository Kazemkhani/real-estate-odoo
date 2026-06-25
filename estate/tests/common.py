from odoo.tests.common import TransactionCase


class EstateCommon(TransactionCase):
    """Shared fixtures for the estate test suite.

    Built once per test class (setUpClass) so the individual tests stay short
    and read like a specification of the module's behaviour.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.property_type = cls.env["estate.property.type"].create({"name": "House"})
        cls.buyer = cls.env["res.partner"].create({"name": "Alice Buyer"})
        cls.other_buyer = cls.env["res.partner"].create({"name": "Bob Buyer"})

    def _make_property(self, **overrides):
        vals = {
            "name": "Test Property",
            "expected_price": 100000.0,
            "property_type_id": self.property_type.id,
            "living_area": 100,
        }
        vals.update(overrides)
        return self.env["estate.property"].create(vals)

    def _make_offer(self, prop, partner=None, price=95000.0, validity=7):
        return self.env["estate.property.offer"].create({
            "property_id": prop.id,
            "partner_id": (partner or self.buyer).id,
            "price": price,
            "validity": validity,
        })
