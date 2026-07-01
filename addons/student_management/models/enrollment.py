from odoo import models, fields, api
from odoo.exceptions import ValidationError
class Enrollment(models.Model):
    _name = 'student.enrollment'
    _description = 'Enrollment'

    student_id = fields.Many2one('student.student', string='Student', required=True, ondelete='cascade')
    subject_id = fields.Many2one('student.subject', string='Subject', required=True)
    grade = fields.Float(string='Grade', digits=(10, 2))
    enrollment_date = fields.Date(string='Enrollment Date', default=fields.Date.today, required=True)
    