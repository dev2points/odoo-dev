from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Subject(models.Model):
    _name = 'student.subject'
    _description = 'Subject'

    name = fields.Char(string='Subject Name', required=True)
    code = fields.Char(string='Subject Code', required=True, unique=True)
    number_credits = fields.Integer(string='Number of Credits', required=True)
    description = fields.Text(string='Description')
    enrollment_ids = fields.One2many('student.enrollment', 'subject_id', string='Enrollments')
    teacher_id = fields.Many2one('department.teacher', string='Teacher')
    