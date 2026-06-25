from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class SportBooking(models.Model):
    """A court reservation — the operational core of Sporty Summer DXB.

    Enforces the three rules management asked for:
      * no double-booking of a court (overlapping confirmed slots are rejected),
      * the participant count never exceeds the sport's per-session limit,
      * a session can only be played once it has been paid for.
    """

    _name = "sport.booking"
    _description = "Court Booking"
    _order = "start_datetime desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Reference", required=True, copy=False, readonly=True, default="New")
    court_id = fields.Many2one("sport.court", string="Court", required=True, tracking=True)
    sport_type_id = fields.Many2one(related="court_id.sport_type_id", string="Sport", store=True, readonly=True)
    max_participants = fields.Integer(related="sport_type_id.max_participants", readonly=True)
    customer_id = fields.Many2one("res.partner", string="Customer", required=True, tracking=True)

    start_datetime = fields.Datetime(string="Start", required=True, tracking=True)
    end_datetime = fields.Datetime(string="End", required=True, tracking=True)
    duration = fields.Float(string="Duration (h)", compute="_compute_duration", store=True)
    participant_count = fields.Integer(string="Participants", default=1, required=True, tracking=True)

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("paid", "Paid"),
            ("done", "Played"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        copy=False,
        tracking=True,
    )

    # --- Pricing (with loyalty discount) ---
    currency_id = fields.Many2one(related="court_id.currency_id", store=True, readonly=True)
    unit_price = fields.Float(related="court_id.hourly_price", string="Price / Hour", readonly=True)
    loyalty_discount = fields.Float(
        related="customer_id.loyalty_discount", string="Loyalty Discount (%)", readonly=True
    )
    amount_untaxed = fields.Monetary(string="Subtotal", compute="_compute_amounts", store=True)
    discount_amount = fields.Monetary(string="Discount", compute="_compute_amounts", store=True)
    amount_total = fields.Monetary(string="Total", compute="_compute_amounts", store=True)

    equipment_loan_ids = fields.One2many("sport.equipment.loan", "booking_id", string="Equipment Loans")

    _check_participant_count = models.Constraint(
        "CHECK(participant_count > 0)",
        "A booking must have at least one participant.",
    )

    # --- Computes ----------------------------------------------------------
    @api.depends("start_datetime", "end_datetime")
    def _compute_duration(self):
        for booking in self:
            if booking.start_datetime and booking.end_datetime and booking.end_datetime > booking.start_datetime:
                delta = booking.end_datetime - booking.start_datetime
                booking.duration = delta.total_seconds() / 3600.0
            else:
                booking.duration = 0.0

    @api.depends("duration", "court_id.hourly_price", "customer_id.loyalty_discount")
    def _compute_amounts(self):
        for booking in self:
            base = booking.duration * booking.court_id.hourly_price
            discount = base * (booking.customer_id.loyalty_discount or 0.0) / 100.0
            booking.amount_untaxed = base
            booking.discount_amount = discount
            booking.amount_total = base - discount

    # --- Onchange (UX helper: default the end time from the sport duration) --
    @api.onchange("court_id", "start_datetime")
    def _onchange_default_end(self):
        if self.court_id and self.start_datetime and not self.end_datetime:
            hours = self.court_id.sport_type_id.default_duration or 1.0
            self.end_datetime = self.start_datetime + timedelta(hours=hours)

    # --- Constraints (the business rules) ----------------------------------
    @api.constrains("start_datetime", "end_datetime")
    def _check_dates(self):
        for booking in self:
            if booking.start_datetime and booking.end_datetime and booking.end_datetime <= booking.start_datetime:
                raise ValidationError("The end time must be after the start time.")

    @api.constrains("participant_count", "sport_type_id")
    def _check_participant_limit(self):
        for booking in self:
            limit = booking.sport_type_id.max_participants
            if limit and booking.participant_count > limit:
                raise ValidationError(
                    "%s allows at most %d participants per session, but %d were requested."
                    % (booking.sport_type_id.name, limit, booking.participant_count)
                )

    @api.constrains("court_id", "start_datetime", "end_datetime", "state")
    def _check_no_overlap(self):
        """Reject any live booking that overlaps another on the same court.

        Two intervals overlap when each starts before the other ends. Draft and
        cancelled bookings are ignored so quotes don't block the calendar."""
        for booking in self:
            if booking.state in ("draft", "cancelled"):
                continue
            if not (booking.court_id and booking.start_datetime and booking.end_datetime):
                continue
            clash = self.search_count([
                ("id", "!=", booking.id),
                ("court_id", "=", booking.court_id.id),
                ("state", "not in", ("draft", "cancelled")),
                ("start_datetime", "<", booking.end_datetime),
                ("end_datetime", ">", booking.start_datetime),
            ])
            if clash:
                raise ValidationError(
                    "%s is already booked during this time slot. Please pick another slot or court."
                    % booking.court_id.name
                )

    # --- Sequence on create ------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals["name"] == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("sport.booking") or "New"
        return super().create(vals_list)

    # --- State actions -----------------------------------------------------
    def action_confirm(self):
        for booking in self:
            if booking.state != "draft":
                raise UserError("Only draft bookings can be confirmed.")
            booking.state = "confirmed"
        return True

    def action_mark_paid(self):
        for booking in self:
            if booking.state not in ("confirmed", "draft"):
                raise UserError("Only an open booking can be marked as paid.")
            booking.state = "paid"
        return True

    def action_play(self):
        # Payment gate: a session can only take place once it has been paid for.
        for booking in self:
            if booking.state != "paid":
                raise UserError(
                    "Booking %s must be paid before the session can take place." % booking.name
                )
            booking.state = "done"
        return True

    def action_cancel(self):
        for booking in self:
            if booking.state == "done":
                raise UserError("A played session cannot be cancelled.")
            booking.state = "cancelled"
        return True

    def action_reset_to_draft(self):
        self.write({"state": "draft"})
        return True
