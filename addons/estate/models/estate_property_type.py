from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Type(models.Model):
    _name = 'estate.property.type'
    _description = 'Property Type'

    name = fields.Char(string='Name', required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id', string='Properties')

    @api.constrains('name')
    def _check_name_unique(self):
        for record in self:
            existing_types = self.search([('name', '=', record.name), ('id', '!=', record.id)])
            if existing_types:
                raise ValidationError("The property type name must be unique.")
