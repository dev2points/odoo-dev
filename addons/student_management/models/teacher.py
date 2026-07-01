from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Teacher(models.Model):
    _name='department.teacher'
    _description='Teacher'

    teacher_id=fields.Char(string='Teacher ID', required=True, unique=True)
    name=fields.Char(string='Name', required=True)
    email=fields.Char(string='Email', required=True, unique=True)
    phone=fields.Char(string='Phone')
    hire_date=fields.Date(string='Hire Date')
    active=fields.Boolean(string='Active', default=True)
    subject_ids=fields.One2many('student.subject', 'teacher_id', string='Subjects Taught')


    @api.constrains('email')
    def _check_email(self):
        for rec in self:
            if rec.email and '@' not in rec.email:
                raise ValidationError(
                    "Invalid email address"
                )