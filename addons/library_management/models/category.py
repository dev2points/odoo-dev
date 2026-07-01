from odoo import fields, models


class LibraryCategory(models.Model):
    _name = "library.category"
    _description = "Library Category"
    _order = "name"

    name = fields.Char(required=True)
