from odoo import fields, models


class LibraryPublisher(models.Model):
    _name = "library.publisher"
    _description = "Library Publisher"
    _order = "name"

    name = fields.Char(required=True)

    phone = fields.Char()

    email = fields.Char()

    website = fields.Char()

    address = fields.Text()

    active = fields.Boolean(default=True)

    product_ids = fields.One2many(
        "product.template",
        "publisher_id",
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
            "domain": [("publisher_id", "=", self.id)],
            "context": {"default_is_library_book": True},
        }