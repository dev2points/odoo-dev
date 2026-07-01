from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LibraryBorrow(models.Model):
    _name = "library.borrow"
    _description = "Library Borrowing Transaction"
    _order = "borrow_date desc, id desc"

    name = fields.Char(default="New", copy=False, readonly=True)
    member_id = fields.Many2one("library.member", string="Member", required=True)
    borrow_date = fields.Date(default=fields.Date.context_today, required=True)
    return_date = fields.Date()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("borrowed", "Borrowed"),
            ("returned", "Returned"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        group_expand="_group_expand_states",
    )
    line_ids = fields.One2many("library.borrow.line", "borrow_id", string="Books")
    book_count = fields.Integer(compute="_compute_book_count", string="Number of Books")

    @api.depends("line_ids")
    def _compute_book_count(self):
        for borrow in self:
            borrow.book_count = len(borrow.line_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("library.borrow") or _("New")
        return super().create(vals_list)

    @api.model
    def _group_expand_states(self, states, domain, order):
        return [key for key, _label in self._fields["state"].selection]

    def action_approve(self):
        for borrow in self:
            if not borrow.line_ids:
                raise UserError(_("Add at least one book before approving."))
            borrow.state = "approved"

    def action_borrow(self):
        for borrow in self:
            if borrow.state not in ("draft", "approved"):
                raise UserError(_("Only draft or approved borrowings can be borrowed."))
            unavailable = borrow.line_ids.filtered(lambda line: line.book_id.state != "available")
            if unavailable:
                names = ", ".join(unavailable.mapped("book_id.display_name"))
                raise UserError(_("These books are not available: %s") % names)
            borrow.line_ids.mapped("book_id").write({"state": "borrowed"})
            borrow.state = "borrowed"

    def action_return(self):
        for borrow in self:
            if borrow.state != "borrowed":
                raise UserError(_("Only borrowed transactions can be returned."))
            borrow.line_ids.mapped("book_id").filtered(lambda book: book.state == "borrowed").write(
                {"state": "available"}
            )
            borrow.return_date = fields.Date.context_today(self)
            borrow.state = "returned"

    def action_cancel(self):
        for borrow in self:
            if borrow.state == "borrowed":
                borrow.line_ids.mapped("book_id").filtered(lambda book: book.state == "borrowed").write(
                    {"state": "available"}
                )
            borrow.state = "cancelled"

    @api.model
    def get_library_dashboard_data(self):
        today = fields.Date.context_today(self)
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        month_start = today.replace(day=1)
        next_month_start = (
            month_start.replace(year=month_start.year + 1, month=1)
            if month_start.month == 12
            else month_start.replace(month=month_start.month + 1)
        )

        Book = self.env["library.book"]
        Member = self.env["library.member"]
        active_borrow_domain = [("state", "!=", "cancelled")]
        current_borrow_groups = self.read_group(
            [("state", "=", "borrowed"), ("member_id", "!=", False)],
            ["member_id"],
            ["member_id"],
            lazy=False,
        )

        return {
            "books": {
                "total": Book.with_context(active_test=False).search_count([]),
                "available": Book.search_count([("state", "=", "available")]),
                "borrowed": Book.search_count([("state", "=", "borrowed")]),
                "lost": Book.search_count([("state", "=", "lost")]),
                "damaged": Book.search_count([("state", "=", "damaged")]),
            },
            "members": {
                "total": Member.with_context(active_test=False).search_count([]),
                "active": Member.search_count([("active", "=", True)]),
                "archived": Member.with_context(active_test=False).search_count([("active", "=", False)]),
                "currently_borrowing": len(current_borrow_groups),
            },
            "borrows": {
                "total": self.search_count(active_borrow_domain),
                "draft": self.search_count([("state", "=", "draft")]),
                "approved": self.search_count([("state", "=", "approved")]),
                "borrowed": self.search_count([("state", "=", "borrowed")]),
                "returned": self.search_count([("state", "=", "returned")]),
                "cancelled": self.search_count([("state", "=", "cancelled")]),
                "this_week": self.search_count(
                    active_borrow_domain + [("borrow_date", ">=", week_start), ("borrow_date", "<=", week_end)]
                ),
                "this_month": self.search_count(
                    active_borrow_domain + [("borrow_date", ">=", month_start), ("borrow_date", "<", next_month_start)]
                ),
                "weekly_data": self._get_daily_borrow_data(week_start, 7, active_borrow_domain),
                "monthly_data": self._get_monthly_borrow_data(today, 6, active_borrow_domain),
            },
        }

    @api.model
    def _get_daily_borrow_data(self, start_date, days, base_domain):
        values = []
        max_count = 1
        for index in range(days):
            day = start_date + timedelta(days=index)
            count = self.search_count(base_domain + [("borrow_date", "=", day)])
            max_count = max(max_count, count)
            values.append({"label": day.strftime("%d/%m"), "count": count})
        for value in values:
            value["percent"] = int(value["count"] * 100 / max_count)
        return values

    @api.model
    def _get_monthly_borrow_data(self, today, months, base_domain):
        current_month = today.replace(day=1)
        month_starts = []
        year = current_month.year
        month = current_month.month
        for _index in range(months):
            month_starts.append(current_month.replace(year=year, month=month))
            month -= 1
            if month == 0:
                month = 12
                year -= 1
        month_starts.reverse()

        values = []
        max_count = 1
        for start_date in month_starts:
            end_date = (
                start_date.replace(year=start_date.year + 1, month=1)
                if start_date.month == 12
                else start_date.replace(month=start_date.month + 1)
            )
            count = self.search_count(
                base_domain + [("borrow_date", ">=", start_date), ("borrow_date", "<", end_date)]
            )
            max_count = max(max_count, count)
            values.append({"label": start_date.strftime("%m/%Y"), "count": count})
        for value in values:
            value["percent"] = int(value["count"] * 100 / max_count)
        return values


class LibraryBorrowLine(models.Model):
    _name = "library.borrow.line"
    _description = "Library Borrowing Line"

    borrow_id = fields.Many2one("library.borrow", required=True, ondelete="cascade")
    book_id = fields.Many2one(
        "library.book",
        string="Book",
        required=True,
        domain="[('state', '=', 'available')]",
    )

    _sql_constraints = [
        (
            "borrow_book_unique",
            "unique(borrow_id, book_id)",
            "A book can only be added once to the same borrowing transaction.",
        ),
    ]

    @api.constrains("book_id")
    def _check_book_available(self):
        for line in self:
            if line.borrow_id.state in ("draft", "approved") and line.book_id.state != "available":
                raise ValidationError(_("Only available books can be added to a borrowing transaction."))
