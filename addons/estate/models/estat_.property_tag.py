from odoo import fields, models, api
from odoo.exceptions import ValidationError

class PropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Property Tag'

    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color')

    @api.constrains('name')
    def _check_name_unique(self):
        for record in self:
            existing_tags = self.search([('name', '=', record.name), ('id', '!=', record.id)])
            if existing_tags:
                raise ValidationError("The property tag name must be unique.")