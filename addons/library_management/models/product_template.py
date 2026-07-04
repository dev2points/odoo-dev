from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_library_book = fields.Boolean(
        string="Library Book",
        default=False,
    )

    isbn = fields.Char()

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

    publish_year = fields.Integer()

    language = fields.Char()

    edition = fields.Char()

    description_library = fields.Html()

    cover_image = fields.Image()


    copy_count = fields.Integer(
        compute="_compute_copy_stats",
    )

    available_copy_count = fields.Integer(
        compute="_compute_copy_stats",
    )

    borrow_count = fields.Integer(
        compute="_compute_copy_stats",
    )

    lot_ids = fields.One2many(
    "stock.lot",
    "product_id",
    string="Book Copies",
    )

    @api.depends("lot_ids")
    def _compute_copy_stats(self):

        for record in self:

            record.copy_count = len(record.lot_ids)

            record.available_copy_count = len(
                record.lot_ids.filtered("available")
            )

            record.borrow_count = sum(
                record.lot_ids.mapped("borrow_count")
            )

    def action_view_copies(self):

        self.ensure_one()

        return {

            "type": "ir.actions.act_window",

            "res_model": "stock.lot",

            "view_mode": "tree,form",

            "domain": [
                ("product_id", "=", self.product_variant_id.id)
            ],

        }
    
    def action_book_special(self):
        """Xử lý một hành động đặc biệt khi bấm nút trên giao diện Sách"""
        # Tạm thời để tạo hiệu ứng không làm gì hoặc trả về thông báo
        return True