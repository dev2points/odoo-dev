from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_library_book = fields.Boolean(
        string="Library Book",
        default=False,
    )

    isbn = fields.Char(
        string="ISBN",
        copy=False,
    )

    author_id = fields.Many2one(
        "library.author",
        string="Author",
        ondelete="restrict",
    )

    category_id = fields.Many2one(
        "library.category",
        string="Category",
        ondelete="restrict",
    )

    publisher_id = fields.Many2one(
        "library.publisher",
        string="Publisher",
        ondelete="restrict",
    )

    publish_year = fields.Integer(string="Publish Year")
    language = fields.Char(string="Language")
    edition = fields.Char(string="Edition")
    description_library = fields.Html(string="Library Description")
    cover_image = fields.Image(string="Cover Image")

    rental_price_per_day = fields.Float(
        string="Rental Price / Day",
        digits="Product Price",
        default=0.0,
    )

    detailed_type = fields.Selection(default="product")
    list_price = fields.Float(default=0.0)
    standard_price = fields.Float(default=0.0)

    copy_ids = fields.One2many(
        "stock.lot",
        "product_tmpl_id",
        string="Book Copies",
    )

    copy_count = fields.Integer(
        compute="_compute_copy_stats",
        string="Total Copies",
    )

    available_copy_count = fields.Integer(
        compute="_compute_copy_stats",
        string="Available Copies",
    )

    borrowed_copy_count = fields.Integer(
        compute="_compute_copy_stats",
        string="Borrowed Copies",
    )

    damaged_copy_count = fields.Integer(
        compute="_compute_copy_stats",
        string="Damaged Copies",
    )

    lost_copy_count = fields.Integer(
        compute="_compute_copy_stats",
        string="Lost Copies",
    )

    borrow_count = fields.Integer(
        compute="_compute_copy_stats",
        string="Borrow Count",
    )

    _sql_constraints = [
        (
            "library_book_isbn_unique",
            "unique(isbn)",
            "ISBN must be unique.",
        ),
    ]

    @api.depends("copy_ids", "copy_ids.state", "copy_ids.borrow_count")
    def _compute_copy_stats(self):
        for book in self:
            copies = book.copy_ids
            book.copy_count = len(copies)
            book.available_copy_count = len(copies.filtered(lambda copy: copy.state == "available"))
            book.borrowed_copy_count = len(copies.filtered(lambda copy: copy.state == "borrowed"))
            book.damaged_copy_count = len(copies.filtered(lambda copy: copy.state == "damaged"))
            book.lost_copy_count = len(copies.filtered(lambda copy: copy.state == "lost"))
            book.borrow_count = sum(copies.mapped("borrow_count"))

    def action_view_copies(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Book Copies",
            "res_model": "stock.lot",
            "view_mode": "kanban,tree,form",
            "domain": [("product_tmpl_id", "=", self.id)],
            "context": {
                "default_product_tmpl_id": self.id,
                "default_product_id": self.product_variant_id.id,
            },
        }

    def action_book_special(self):
        return True
