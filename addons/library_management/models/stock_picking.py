from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    borrow_id = fields.Many2one(
        "library.borrow",
        readonly=True,
    )