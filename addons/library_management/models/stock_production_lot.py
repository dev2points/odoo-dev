from odoo import api, fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.lot"

    shelf_id = fields.Many2one(
        "library.shelf"
    )

    borrow_line_ids = fields.One2many(
        "library.borrow.line",
        "lot_id",
    )

    note = fields.Text()

    condition = fields.Selection(
        [
            ("new", "New"),
            ("good", "Good"),
            ("damaged", "Damaged"),
            ("lost", "Lost"),
        ],
        default="good",
    )

    borrow_count = fields.Integer(
        compute="_compute_borrow_count",
    )

    def _compute_borrow_count(self):
        for lot in self:
            lot.borrow_count = len(lot.borrow_line_ids)

    def action_view_borrow_history(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Borrow History",
            "res_model": "library.borrow.line",
            "view_mode": "tree,form",
            "domain": [("lot_id", "=", self.id)],
        }

    @api.model
    def create(self, vals):

        if not vals.get("name"):

            vals["name"] = self.env[
                "ir.sequence"
            ].next_by_code(
                "library.book.copy"
            )

        return super().create(vals)