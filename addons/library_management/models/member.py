from odoo import fields, models, api


class LibraryMember(models.Model):
    _name = "library.member"
    _description = "Library Member"
    _order = "name"

    name = fields.Char(required=True)
    phone = fields.Char()
    email = fields.Char()
    active = fields.Boolean(default=True)

    def name_get(self):

        result = []

        for record in self:

            display = record.name

            if record.phone:
                display += f" - {record.phone}"

            if record.email:
                display += f" - {record.email}"


            result.append(
                (record.id, display)
            )

        return result
    
    @api.depends('name', 'phone', 'email')
    def _compute_display_name(self):
        super()._compute_display_name()
        for record in self:
            if record.phone:
                record.display_name = f"{record.name} - {record.phone}"
            elif record.email:
                record.display_name = f"{record.name} - {record.email}"
            else:
                record.display_name = record.name
