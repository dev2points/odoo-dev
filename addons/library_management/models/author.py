from odoo import fields, models


class LibraryAuthor(models.Model):
    _name = "library.author"
    _description = "Library Author"
    _order = "name"

    name = fields.Char(required=True)
    description = fields.Text()
