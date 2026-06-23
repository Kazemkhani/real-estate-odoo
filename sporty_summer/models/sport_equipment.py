from odoo import api, fields, models


class SportEquipment(models.Model):
    """A type of loanable equipment (rackets, balls, nets...) with live stock
    tracking driven by the outstanding loans."""

    _name = "sport.equipment"
    _description = "Sport Equipment"
    _order = "name"

    name = fields.Char(required=True)
    code = fields.Char()
    sport_type_id = fields.Many2one("sport.type", string="Sport")
    total_quantity = fields.Integer(string="Total Stock", default=1, required=True)
    loaned_quantity = fields.Integer(compute="_compute_quantities", store=True)
    available_quantity = fields.Integer(compute="_compute_quantities", store=True)
    lost_quantity = fields.Integer(compute="_compute_quantities", store=True)

    loan_ids = fields.One2many("sport.equipment.loan", "equipment_id", string="Loans")

    _check_total_quantity = models.Constraint(
        "CHECK(total_quantity >= 0)",
        "Total stock cannot be negative.",
    )

    @api.depends("loan_ids.state", "loan_ids.quantity", "total_quantity")
    def _compute_quantities(self):
        for equipment in self:
            out = sum(equipment.loan_ids.filtered(lambda loan_record: loan_record.state == "loaned").mapped("quantity"))
            lost = sum(
                equipment.loan_ids.filtered(lambda loan_record: loan_record.state in ("lost", "damaged")).mapped("quantity")
            )
            equipment.loaned_quantity = out
            equipment.lost_quantity = lost
            # Lost/damaged items leave circulation, so they reduce what's on hand.
            equipment.available_quantity = equipment.total_quantity - out - lost
