from odoo import api, fields, models

# Defaults — also used as fallbacks when a parameter has never been set, which
# keeps behaviour stable and matches the original case-study figures.
DEFAULT_FAMILY_DISCOUNT = 5.0
DEFAULT_GROUP_DISCOUNT = 10.0
DEFAULT_GROUP_THRESHOLD = 10
DEFAULT_COMMISSION = 15.0


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    tourism_family_discount = fields.Float(
        string="Family Discount (%)",
        config_parameter="dubai_tourism.family_discount",
        default=DEFAULT_FAMILY_DISCOUNT,
        help="Discount applied when a booking includes at least one child.",
    )
    tourism_group_discount = fields.Float(
        string="Group Discount (%)",
        config_parameter="dubai_tourism.group_discount",
        default=DEFAULT_GROUP_DISCOUNT,
        help="Discount applied once a booking reaches the group threshold.",
    )
    tourism_group_threshold = fields.Integer(
        string="Group Threshold (travellers)",
        config_parameter="dubai_tourism.group_threshold",
        default=DEFAULT_GROUP_THRESHOLD,
        help="Number of travellers from which a booking counts as a group.",
    )
    tourism_default_commission = fields.Float(
        string="Default Transport Commission (%)",
        config_parameter="dubai_tourism.default_commission",
        default=DEFAULT_COMMISSION,
        help="Default commission applied to third-party transport assignments.",
    )
    tourism_auto_email = fields.Boolean(
        string="Send Booking Emails",
        config_parameter="dubai_tourism.auto_email",
        help="Automatically email the customer on confirmation and payment.",
    )
    tourism_auto_cancel_days = fields.Integer(
        string="Auto-cancel Unpaid After (days)",
        config_parameter="dubai_tourism.auto_cancel_days",
        default=0,
        help="If positive, the scheduled action cancels bookings still unpaid this "
             "many days after departure. 0 disables auto-cancellation.",
    )
