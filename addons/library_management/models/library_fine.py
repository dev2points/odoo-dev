from odoo import models, fields, api

class LibraryFine(models.Model):

    _name = "library.fine"
    _description = "Library Fine"

    borrow_id = fields.Many2one(
        "library.borrow"
    )

    member_id = fields.Many2one(
        "library.member"
    )

    amount = fields.Float()

    reason = fields.Selection([
        ("late","Late"),
        ("lost","Lost"),
        ("damage","Damage")
    ])

    paid = fields.Boolean()
