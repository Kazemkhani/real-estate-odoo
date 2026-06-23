from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class SportClassRegistration(models.Model):
    """A customer's seat in a coaching class. Capacity is enforced on a strict
    first-come, first-served basis and a seat is only secured once paid."""

    _name = "sport.class.registration"
    _description = "Class Registration"
    _order = "registration_date, id"

    name = fields.Char(string="Reference", required=True, copy=False, readonly=True, default="New")
    class_id = fields.Many2one("sport.coaching.class", string="Class", required=True, ondelete="cascade")
    sport_type_id = fields.Many2one(related="class_id.sport_type_id", store=True, readonly=True)
    customer_id = fields.Many2one("res.partner", string="Customer", required=True)
    registration_date = fields.Datetime(default=lambda self: fields.Datetime.now())
    price = fields.Float(related="class_id.price", readonly=True)
    currency_id = fields.Many2one(related="class_id.currency_id", readonly=True)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("paid", "Paid"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        copy=False,
    )

    _unique_customer_per_class = models.Constraint(
        "UNIQUE(class_id, customer_id)",
        "This customer is already registered for that class.",
    )

    @api.constrains("class_id", "state")
    def _check_capacity(self):
        """First-come, first-served: a confirmed/paid registration must never push
        the class beyond its seat capacity."""
        for reg in self:
            if reg.state in ("confirmed", "paid"):
                cls = reg.class_id
                taken = len(cls.registration_ids.filtered(lambda r: r.state in ("confirmed", "paid")))
                if taken > cls.capacity:
                    raise ValidationError(
                        "Class '%s' is full (%d/%d seats). Registration cannot be confirmed."
                        % (cls.name, taken, cls.capacity)
                    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals["name"] == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("sport.class.registration") or "New"
        return super().create(vals_list)

    def action_confirm(self):
        self.write({"state": "confirmed"})
        return True

    def action_mark_paid(self):
        for reg in self:
            if reg.state == "cancelled":
                raise UserError("A cancelled registration cannot be paid.")
            reg.state = "paid"
        return True

    def action_cancel(self):
        self.write({"state": "cancelled"})
        return True
