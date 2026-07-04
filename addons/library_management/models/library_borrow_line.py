from odoo import api, fields, models


class LibraryBorrowLine(models.Model):
    _name = "library.borrow.line"
    _description = "Library Borrow Line"

    borrow_id = fields.Many2one(
        "library.borrow",
        required=True,
        ondelete="cascade",
    )

    product_id = fields.Many2one(
        "product.product",
        required=True,
    )

    member_id = fields.Many2one(
        related="borrow_id.member_id",
        store=True,
        readonly=True,
    )

    borrow_date = fields.Date(
        related="borrow_id.borrow_date",
        store=True,
        readonly=True,
    )

    return_date = fields.Date(
        related="borrow_id.return_date",
        store=True,
        readonly=True,
    )

    lot_id = fields.Many2one(
        "stock.lot",
        required=True,
        domain="[('product_id', '=', product_id)]",
    )

    quantity = fields.Float(
        default=1.0,
        readonly=True,
    )

    note = fields.Char()

    state = fields.Selection(
        related="borrow_id.state",
        store=True,
    )