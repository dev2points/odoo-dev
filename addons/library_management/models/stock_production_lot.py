from odoo import api, fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.lot"

    product_tmpl_id = fields.Many2one(
        "product.template",
        string="Book",
        related="product_id.product_tmpl_id",
        store=True,
        index=True,
        readonly=True,
    )

    internal_code = fields.Char(
        string="Internal Code",
        copy=False,
    )

    shelf_id = fields.Many2one(
        "library.shelf",
        string="Shelf",
    )

    borrow_line_ids = fields.One2many(
        "library.borrow.line",
        "lot_id",
        string="Borrow History",
    )

    note = fields.Text(string="Notes")

    condition = fields.Selection(
        [
            ("new", "New"),
            ("good", "Good"),
            ("damaged", "Damaged"),
            ("lost", "Lost"),
        ],
        string="Condition",
        default="good",
        required=True,
    )

    state = fields.Selection(
        [
            ("available", "Available"),
            ("borrowed", "Borrowed"),
            ("damaged", "Damaged"),
            ("lost", "Lost"),
        ],
        compute="_compute_library_state",
        string="Status",
        store=True,
    )

    borrow_count = fields.Integer(
        compute="_compute_borrow_count",
        string="Borrow Count",
    )

    current_borrow_id = fields.Many2one(
        "library.borrow",
        compute="_compute_current_borrow",
        string="Current Borrow",
    )

    _sql_constraints = [
        (
            "library_copy_internal_code_unique",
            "unique(internal_code)",
            "Internal code must be unique.",
        ),
    ]

    @api.depends("condition", "borrow_line_ids.state")
    def _compute_library_state(self):
        for lot in self:
            if lot.condition in ("lost", "damaged"):
                lot.state = lot.condition
            elif any(line.state == "borrowed" for line in lot.borrow_line_ids):
                lot.state = "borrowed"
            else:
                lot.state = "available"

    @api.depends("borrow_line_ids.state")
    def _compute_current_borrow(self):
        for lot in self:
            current_line = lot.borrow_line_ids.filtered(lambda line: line.state == "borrowed")[:1]
            lot.current_borrow_id = current_line.borrow_id

    @api.depends("borrow_line_ids")
    def _compute_borrow_count(self):
        for lot in self:
            lot.borrow_count = len(lot.borrow_line_ids)

    def action_view_borrow_history(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Borrow History",
            "res_model": "library.borrow.line",
            "view_mode": "tree,form",
            "domain": [("lot_id", "=", self.id)],
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                vals["name"] = self.env["ir.sequence"].next_by_code("library.book.copy")
        return super().create(vals_list)
