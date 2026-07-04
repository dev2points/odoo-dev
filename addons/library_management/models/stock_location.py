from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    is_library = fields.Boolean(
        string="Library Location",
        default=False,
    )