from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    borrow_line_id = fields.Many2one(
        "library.borrow.line",
    )