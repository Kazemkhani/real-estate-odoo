from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SportEquipmentLoan(models.Model):
    """Equipment issued to a customer, tracked through return / loss / damage so
    the facility always knows what is out and what it is owed for."""

    _name = "sport.equipment.loan"
    _description = "Equipment Loan"
    _order = "loan_date desc, id desc"

    name = fields.Char(string="Reference", required=True, copy=False, readonly=True, default="New")
    equipment_id = fields.Many2one("sport.equipment", string="Equipment", required=True)
    sport_type_id = fields.Many2one(related="equipment_id.sport_type_id", store=True, readonly=True)
    customer_id = fields.Many2one("res.partner", string="Customer", required=True)
    booking_id = fields.Many2one("sport.booking", string="Related Booking", ondelete="set null")
    quantity = fields.Integer(default=1, required=True)
    loan_date = fields.Datetime(default=lambda self: fields.Datetime.now())
    return_date = fields.Datetime(readonly=True)
    state = fields.Selection(
        selection=[
            ("loaned", "On Loan"),
            ("returned", "Returned"),
            ("lost", "Lost"),
            ("damaged", "Damaged"),
        ],
        default="loaned",
        required=True,
        copy=False,
    )
    penalty_amount = fields.Monetary(string="Penalty / Charge")
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)
    notes = fields.Text()

    _check_quantity = models.Constraint(
        "CHECK(quantity > 0)",
        "A loan must be for at least one item.",
    )

    @api.constrains("quantity", "equipment_id", "state")
    def _check_stock(self):
        """Never issue more than what is physically available. available_quantity
        already accounts for this loan, so a negative value means over-issuing."""
        for loan in self:
            if loan.state == "loaned" and loan.equipment_id.available_quantity < 0:
                raise ValidationError(
                    "Not enough '%s' in stock to loan out %d unit(s)."
                    % (loan.equipment_id.name, loan.quantity)
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals["name"] == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("sport.equipment.loan") or "New"
        return super().create(vals_list)

    def action_return(self):
        self.write({"state": "returned", "return_date": fields.Datetime.now()})
        return True

    def action_mark_lost(self):
        self.write({"state": "lost"})
        return True

    def action_mark_damaged(self):
        self.write({"state": "damaged"})
        return True
