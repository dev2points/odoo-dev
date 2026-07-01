from odoo import api, fields, models


class LibraryBook(models.Model):
    _name = "library.book"
    _description = "Library Book Copy"
    _order = "code, name"

    code = fields.Char(required=True, copy=False)
    name = fields.Char(string="Title", required=True)
    title = fields.Char(related="name", string="Title", readonly=False)
    isbn = fields.Char(string="ISBN")
    author_id = fields.Many2one("library.author", string="Author")
    category_id = fields.Many2one("library.category", string="Category")
    publisher = fields.Char()
    publish_year = fields.Integer()
    language = fields.Char()
    edition = fields.Char()
    description = fields.Text()
    cover_image = fields.Binary(string="Cover Image", attachment=True)
    shelf_location = fields.Char()
    price = fields.Float()
    state = fields.Selection(
        [
            ("available", "Available"),
            ("borrowed", "Borrowed"),
            ("lost", "Lost"),
            ("damaged", "Damaged"),
        ],
        default="available",
        required=True,
    )
    active = fields.Boolean(default=True)
    borrow_line_ids = fields.One2many("library.borrow.line", "book_id", string="Borrow History")
    borrow_count = fields.Integer(compute="_compute_borrow_count", string="Borrow Count")

    _sql_constraints = [
        ("code_unique", "unique(code)", "The book code must be unique."),
    ]

    @api.depends("borrow_line_ids")
    def _compute_borrow_count(self):
        for book in self:
            book.borrow_count = len(book.borrow_line_ids)

    @api.model
    def get_book_dashboard_data(self):
        Book = self.with_context(active_test=False)
        category_groups = Book.read_group(
            domain=[],
            fields=["category_id"],
            groupby=["category_id"],
            lazy=False,
        )
        return {
            "total_books": Book.search_count([]),
            "available_books": Book.search_count([("state", "=", "available")]),
            "borrowed_books": Book.search_count([("state", "=", "borrowed")]),
            "lost_books": Book.search_count([("state", "=", "lost")]),
            "damaged_books": Book.search_count([("state", "=", "damaged")]),
            "category_data": [
                {
                    "name": group["category_id"][1] if group.get("category_id") else "Uncategorized",
                    "count": group["__count"],
                }
                for group in category_groups
            ],
        }

    @api.model
    def get_dashboard_stats(self):
        return self.get_book_dashboard_data()
