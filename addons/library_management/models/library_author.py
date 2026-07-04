from odoo import fields, models


class LibraryAuthor(models.Model):
    _name = "library.author"
    _description = "Library Author"
    _order = "name"

    name = fields.Char(required=True)

    code = fields.Char(copy=False)

    biography = fields.Text()

    birth_date = fields.Date()

    death_date = fields.Date()

    country = fields.Char()

    active = fields.Boolean(default=True)

    product_ids = fields.One2many(
        "product.template",
        "author_id",
    )

    book_count = fields.Integer(
        compute="_compute_book_count",
    )

    def _compute_book_count(self):
        for record in self:
            record.book_count = len(record.product_ids)

    def action_view_books(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Books",
            "res_model": "product.template",
            "view_mode": "tree,form",
            "domain": [("author_id", "=", self.id)],
            "context": {"default_is_library_book": True},
        }

    _sql_constraints = [
        (
            "author_name_unique",
            "unique(name)",
            "Author already exists.",
        )
    ]