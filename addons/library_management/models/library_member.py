from odoo import api, fields, models


class LibraryMember(models.Model):
    _name = "library.member"
    _description = "Library Member"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"

    code = fields.Char(
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: self.env["ir.sequence"].next_by_code("library.member"),
        tracking=True,
    )

    name = fields.Char(
        required=True,
        tracking=True,
    )

    image_1920 = fields.Image()

    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ]
    )

    birthday = fields.Date()

    phone = fields.Char()

    mobile = fields.Char()

    email = fields.Char()

    address = fields.Char()

    register_date = fields.Date(
        default=fields.Date.today,
    )

    active = fields.Boolean(default=True)

    borrow_ids = fields.One2many(
        "library.borrow",
        "member_id",
    )

    borrow_count = fields.Integer(
        compute="_compute_statistics",store=True
    )

    borrowing_count = fields.Integer(
        compute="_compute_statistics",store=True
    )

    returned_count = fields.Integer(
        compute="_compute_statistics",store=True
    )

    overdue_count = fields.Integer(
        compute="_compute_statistics", store=True
    )

    @api.depends("borrow_ids.state", "borrow_ids.due_date", "borrow_ids.return_date")
    def _compute_statistics(self):
        today = fields.Date.to_date(fields.Date.context_today(self))

        for member in self:

            member.borrow_count = len(member.borrow_ids)

            member.borrowing_count = len(
                member.borrow_ids.filtered(
                    lambda b: b.state == "borrowed"
                )
            )

            member.returned_count = len(
                member.borrow_ids.filtered(
                    lambda b: b.state == "returned"
                )
            )

            member.overdue_count = len(
                member.borrow_ids.filtered(
                    lambda b: b.state == "borrowed"
                    and b.due_date
                    and fields.Date.to_date(b.due_date) < today
                )
            )

    def action_view_borrows(self):

        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Borrow History",
            "res_model": "library.borrow",
            "view_mode": "tree,form",
            "domain": [
                ("member_id", "=", self.id)
            ],
        }

    def name_get(self):

        result = []

        for member in self:

            name = f"[{member.code}] {member.name}"

            if member.phone:
                name += f" - {member.phone}"

            elif member.email:
                name += f" - {member.email}"

            result.append((member.id, name))

        return result