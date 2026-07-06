from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

# Class quản lý yêu cầu mượn sách trong thư viện
class LibraryBorrow(models.Model):
    _name = "library.borrow"
    _description = "Library Borrow"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    # ==========================================================
    # Basic Information
    # ==========================================================

    name = fields.Char(
        string="Borrow Number",
        required=True,
        copy=False,
        readonly=True,
        default="New",
        tracking=True,
    )

    member_id = fields.Many2one(
        "library.member",
        string="Member",
        required=True,
        tracking=True,
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        readonly=True,
    )

    borrow_date = fields.Date(
        string="Borrow Date",
        default=fields.Date.context_today,
        required=True,
        tracking=True,
    )

    due_date = fields.Date(
        string="Due Date",
        required=True,
        tracking=True,
    )

    return_date = fields.Date(
        string="Return Date",
        readonly=True,
        tracking=True,
    )

    note = fields.Text(
        string="Notes",
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    # ==========================================================
    # Lines
    # ==========================================================

    line_ids = fields.One2many(
        "library.borrow.line",
        "borrow_id",
        string="Books",
        copy=True,
    )

    # ==========================================================
    # Picking
    # ==========================================================

    picking_out_id = fields.Many2one(
        "stock.picking",
        string="Borrow Picking",
        readonly=True,
        copy=False,
    )

    picking_in_id = fields.Many2one(
        "stock.picking",
        string="Return Picking",
        readonly=True,
        copy=False,
    )

    picking_state = fields.Selection(
        related="picking_out_id.state",
        string="Picking Status",
        store=True,
        readonly=True,
    )

    move_count = fields.Integer(
        compute="_compute_move_count",
        string="Transfers",
    )

    # ==========================================================
    # State
    # ==========================================================

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("borrowed", "Borrowed"),
            ("returned", "Returned"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    # ==========================================================
    # SQL Constraints
    # ==========================================================

    _sql_constraints = [
        (
            "borrow_name_unique",
            "unique(name)",
            "Borrow number must be unique.",
        ),
    ]

    # ==========================================================
    # Compute
    # ==========================================================

    @api.depends("picking_out_id.move_ids")
    def _compute_move_count(self):
        for borrow in self:
            borrow.move_count = len(borrow.picking_out_id.move_ids)

    # ==========================================================
    # Create
    # ==========================================================

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:

            if vals.get("name", "New") == "New":

                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "library.borrow"
                )

        return super().create(vals_list)
    
        # ==========================================================
    # Helper Methods
    # ==========================================================

    def _get_library_location(self):
        """Library Stock Location"""
        return self.env.ref(
            "library_management.stock_location_library"
        )

    def _get_member_location(self):
        """Borrowed Books Location"""
        return self.env.ref(
            "library_management.stock_location_member"
        )

    def _get_out_picking_type(self):
        """Library Borrow Picking Type"""
        return self.env.ref(
            "library_management.library_picking_type_out"
        )

    # ==========================================================
    # Validation
    # ==========================================================

    def _check_before_confirm(self):

        self.ensure_one()

        if not self.member_id:
            raise ValidationError(
                _("Please select a member.")
            )

        if not self.line_ids:
            raise ValidationError(
                _("Please add at least one book.")
            )

        product_ids = []

        for line in self.line_ids:

            if not line.product_id:
                raise ValidationError(
                    _("Product is required.")
                )

            if not line.lot_id:
                raise ValidationError(
                    _("Book Copy is required.")
                )

            if line.quantity <= 0:
                raise ValidationError(
                    _("Quantity must be greater than zero.")
                )

            if line.product_id.id in product_ids:
                raise ValidationError(
                    _("Duplicate book is not allowed.")
                )

            product_ids.append(line.product_id.id)

            if line.lot_id.product_id != line.product_id:
                raise ValidationError(
                    _(
                        "Book Copy '%s' does not belong to '%s'."
                    )
                    % (
                        line.lot_id.name,
                        line.product_id.display_name,
                    )
                )

    # ==========================================================
    # Picking
    # ==========================================================

    def _create_out_picking(self):

        self.ensure_one()

        picking = self.env["stock.picking"].create({

            "partner_id": False,

            "origin": self.name,

            "borrow_id": self.id,

            "company_id": self.company_id.id,

            "picking_type_id": self._get_out_picking_type().id,

            "location_id": self._get_library_location().id,

            "location_dest_id": self._get_member_location().id,

        })

        return picking

    # ==========================================================
    # Stock Move
    # ==========================================================

    def _create_stock_moves(self, picking):

        Move = self.env["stock.move"]

        for line in self.line_ids:

            Move.create({

                "name": line.product_id.display_name,

                "company_id": self.company_id.id,

                "product_id": line.product_id.id,

                "product_uom_qty": line.quantity,

                "product_uom": line.product_id.uom_id.id,

                "location_id": picking.location_id.id,

                "location_dest_id": picking.location_dest_id.id,

                "picking_id": picking.id,

                "borrow_line_id": line.id,

            })
        # ==========================================================
    # Actions
    # ==========================================================

    def action_confirm(self):

        for borrow in self:

            if borrow.state != "draft":
                continue

            borrow._check_before_confirm()

            picking = borrow._create_out_picking()

            borrow._create_stock_moves(picking)

            borrow.picking_out_id = picking.id

            borrow.state = "confirmed"

        return True

    def action_borrow(self):

        for borrow in self:

            if borrow.state != "confirmed":
                raise UserError(
                    _("Only confirmed borrow orders can be borrowed.")
                )

            picking = borrow.picking_out_id

            if not picking:
                raise UserError(
                    _("No stock picking found.")
                )

            # Confirm stock moves
            if picking.state == "draft":
                picking.action_confirm()

            # Reserve stock
            if picking.state in ("confirmed", "waiting", "assigned"):
                picking.action_assign()

            # Việc gán serial number và validate
            # sẽ được thực hiện ở Phần 4

            borrow.state = "borrowed"

        return True

    def action_return(self):

        for borrow in self:

            if borrow.state != "borrowed":
                raise UserError(
                    _("Only borrowed books can be returned.")
                )

            borrow.return_date = fields.Date.context_today(self)

            # Return Picking sẽ tạo ở Part 4

            borrow.state = "returned"

        return True

    def action_cancel(self):

        for borrow in self:

            if borrow.state == "returned":
                raise UserError(
                    _("Returned borrow cannot be cancelled.")
                )

            if (
                borrow.picking_out_id
                and borrow.picking_out_id.state not in ("cancel", "done")
            ):
                borrow.picking_out_id.action_cancel()

            borrow.state = "cancel"

        return True

    @api.model
    def get_library_dashboard_data(self):
        today = fields.Date.to_date(fields.Date.context_today(self))
        week_start = today - relativedelta(days=today.weekday())

        book_lots = self.env["stock.lot"].search([])
        borrow_records = self.search([])
        member_records = self.env["library.member"].search([])

        borrowed_lots = book_lots.filtered(
            lambda lot: any(line.borrow_id.state == "borrowed" for line in lot.borrow_line_ids)
        )
        lost_lots = book_lots.filtered(lambda lot: lot.condition == "lost")
        damaged_lots = book_lots.filtered(lambda lot: lot.condition == "damaged")

        def _chart_data(series):
            max_count = max((count for _, count in series), default=0)
            return [
                {
                    "label": label,
                    "count": count,
                    "percent": round((count / max_count) * 100) if max_count else 0,
                }
                for label, count in series
            ]

        weekly_series = []
        for offset in range(6, -1, -1):
            current_day = today - relativedelta(days=offset)
            count = len(
                borrow_records.filtered(
                    lambda record, day=current_day: record.borrow_date
                    and fields.Date.to_date(record.borrow_date) == day
                )
            )
            weekly_series.append((current_day.strftime("%a"), count))

        monthly_series = []
        for offset in range(5, -1, -1):
            month_marker = today - relativedelta(months=offset)
            month_start = month_marker.replace(day=1)
            next_month = month_start + relativedelta(months=1)
            count = len(
                borrow_records.filtered(
                    lambda record, start=month_start, end=next_month: record.borrow_date
                    and start <= fields.Date.to_date(record.borrow_date) < end
                )
            )
            monthly_series.append((month_start.strftime("%b %Y"), count))

        return {
            "books": {
                "total": len(book_lots),
                "available": max(len(book_lots) - len(borrowed_lots) - len(lost_lots) - len(damaged_lots), 0),
                "borrowed": len(borrowed_lots),
                "lost": len(lost_lots),
                "damaged": len(damaged_lots),
            },
            "members": {
                "total": len(member_records),
                "active": len(member_records.filtered("active")),
                "archived": len(member_records.filtered(lambda member: not member.active)),
                "currently_borrowing": len(
                    member_records.filtered(
                        lambda member: any(borrow.state == "borrowed" for borrow in member.borrow_ids)
                    )
                ),
            },
            "borrows": {
                "total": len(borrow_records),
                "draft": len(borrow_records.filtered(lambda record: record.state == "draft")),
                "approved": len(borrow_records.filtered(lambda record: record.state == "confirmed")),
                "borrowed": len(borrow_records.filtered(lambda record: record.state == "borrowed")),
                "returned": len(borrow_records.filtered(lambda record: record.state == "returned")),
                "this_week": len(
                    borrow_records.filtered(
                        lambda record: record.borrow_date
                        and fields.Date.to_date(record.borrow_date) >= week_start
                    )
                ),
                "this_month": len(
                    borrow_records.filtered(
                        lambda record: record.borrow_date
                        and fields.Date.to_date(record.borrow_date).year == today.year
                        and fields.Date.to_date(record.borrow_date).month == today.month
                    )
                ),
                "weekly_data": _chart_data(weekly_series),
                "monthly_data": _chart_data(monthly_series),
            },
        }

    def action_set_to_draft(self):

        for borrow in self:

            if borrow.state != "cancel":
                continue

            borrow.state = "draft"

        return True
    
        # ==========================================================
    # Return Picking
    # ==========================================================

    def _create_return_picking(self):

        self.ensure_one()

        picking_type = self._get_out_picking_type()

        picking = self.env["stock.picking"].create({

            "origin": self.name + " / RETURN",

            "borrow_id": self.id,

            "company_id": self.company_id.id,

            "picking_type_id": picking_type.id,

            "location_id": self._get_member_location().id,

            "location_dest_id": self._get_library_location().id,

        })

        Move = self.env["stock.move"]

        for line in self.line_ids:

            Move.create({

                "name": line.product_id.display_name,

                "company_id": self.company_id.id,

                "product_id": line.product_id.id,

                "product_uom_qty": line.quantity,

                "product_uom": line.product_id.uom_id.id,

                "location_id": picking.location_id.id,

                "location_dest_id": picking.location_dest_id.id,

                "picking_id": picking.id,

            })

        return picking

    # ==========================================================
    # Borrow
    # ==========================================================

    def action_borrow(self):

        for borrow in self:

            if borrow.state != "confirmed":
                raise UserError(_("Borrow must be confirmed first."))

            picking = borrow.picking_out_id

            if picking.state == "draft":
                picking.action_confirm()

            picking.action_assign()

            for line in borrow.line_ids:

                move = picking.move_ids.filtered(
                    lambda m: m.borrow_line_id == line
                )

                if not move:
                    continue

                for move_line in move.move_line_ids:

                    move_line.lot_id = line.lot_id
                    move_line.qty_done = line.quantity

            picking.button_validate()

            borrow.state = "borrowed"

        return True

    # ==========================================================
    # Return
    # ==========================================================

    def action_return(self):

        for borrow in self:

            if borrow.state != "borrowed":
                raise UserError(_("Books are not borrowed."))

            picking = borrow._create_return_picking()

            picking.action_confirm()

            picking.action_assign()

            for line in borrow.line_ids:

                move = picking.move_ids.filtered(
                    lambda m: m.product_id == line.product_id
                )

                for move_line in move.move_line_ids:

                    move_line.lot_id = line.lot_id
                    move_line.qty_done = line.quantity

            picking.button_validate()

            borrow.picking_in_id = picking

            borrow.return_date = fields.Date.context_today(self)

            borrow.state = "returned"

        return True

    # ==========================================================
    # Smart Button
    # ==========================================================

    def action_view_picking(self):

        self.ensure_one()

        picking = self.picking_out_id or self.picking_in_id

        if not picking:
            return False

        return {

            "type": "ir.actions.act_window",

            "name": _("Transfer"),

            "res_model": "stock.picking",

            "view_mode": "form",

            "res_id": picking.id,

            "target": "current",

        }

    # ==========================================================
    # Delete
    # ==========================================================

    def unlink(self):

        for borrow in self:

            if borrow.state != "draft":
                raise UserError(
                    _("Only draft borrow records can be deleted.")
                )

        return super().unlink()