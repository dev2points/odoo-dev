from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Department(models.Model):
    _name = 'department.department'
    _description = 'Department'
    
    name = fields.Char(string='Name', required=True)

    student_ids = fields.One2many('student.student', 'department_id', string='Students')
    student_count = fields.Integer(compute="_compute_student_count", string='Student Count')

    def _compute_student_count(self):
        for dept in self:
            dept.student_count = len(dept.student_ids)

    