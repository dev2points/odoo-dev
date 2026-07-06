from odoo import fields, models

# Class quản lý kệ sách trong thư viện
class LibraryShelf(models.Model):
    _name = "library.shelf"
    _description = "Library Shelf"
    _order = "code"

    code = fields.Char(required=True)

    name = fields.Char(required=True)

    floor = fields.Char()

    zone = fields.Char()

    description = fields.Text()

    active = fields.Boolean(default=True)

    lot_ids = fields.One2many(
        "stock.lot",
        "shelf_id",
    )

    copy_count = fields.Integer(
        compute="_compute_copy_count",
    )

    def _compute_copy_count(self):
        for record in self:
            record.copy_count = len(record.lot_ids)

    def action_view_copies(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Book Copies",
            "res_model": "stock.lot",
            "view_mode": "tree,form",
            "domain": [("shelf_id", "=", self.id)],
        }

    _sql_constraints = [
        (
            "shelf_code_unique",
            "unique(code)",
            "Shelf code must be unique.",
        )
    ]