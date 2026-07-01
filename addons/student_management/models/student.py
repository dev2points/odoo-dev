from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Student(models.Model):
    _name = 'student.student'
    _description = 'Student'
    _active_name = 'active'

    _sql_constraints = [
        ('student_id_unique', 'unique(student_id)', 'Student ID must be unique'),
        ('email_valid_check', 'CHECK(email IS NULL OR email LIKE \'%@%\')', 'Invalid email address'),
    ]

    student_id = fields.Char(string='Student ID', required=True, unique=True)
    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name')
    name = fields.Char(string='Full Name', compute="_compute_full_name", store=True)
    age = fields.Integer(string='Age', required=False, store=False)
    email = fields.Char(string='Email')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ])
    gpa = fields.Float(string='GPA', compute='_compute_gpa', required=False, store=True)
    active = fields.Boolean(string='Active', default=True)
    birthday = fields.Date(string='Birthday')
    department_id = fields.Many2one('department.department', string='Department', ondelete='set null')
    status = fields.Selection([ ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ], string = 'Status' )
    grade_ids = fields.One2many('student.enrollment', 'student_id', string='Grades')


    @api.depends('first_name', 'last_name')
    def _compute_full_name(self):
        for rec in self:
            rec.name = f"{rec.first_name} {rec.last_name}" if rec.last_name else rec.first_name
            
    @api.onchange('birthday')
    def _onchange_birthday(self):
        for rec in self:
            if rec.birthday:
                age = fields.Date.today().year - rec.birthday.year
                rec.age = age

    @api.constrains('birthday')
    def _check_birthday(self):
        for rec in self:
            if rec.birthday and rec.birthday > fields.Date.today():
                raise ValidationError(
                    "Birthday cannot be in the future"
                )

    @api.constrains('email')
    def _check_email(self):
        for rec in self:
            if rec.email and '@' not in rec.email:
                raise ValidationError(
                    "Invalid email address"
                )

    # @api.constrains('gpa')
    # def _check_gpa(self):
    #     for rec in self:
    #         if rec.gpa < 0 or rec.gpa > 4:
    #             raise ValidationError(
    #                 "GPA must be between 0 and 4"
    #             )
            
    @api.depends('grade_ids.grade', 'grade_ids.subject_id.number_credits')
    def _compute_gpa(self):
        for rec in self:
            total_credits = 0
            total_points = 0.0
            for enrollment in rec.grade_ids:
                subject = enrollment.subject_id
                credits = subject.number_credits if subject else 0
                # Convert grade from 10-point scale to 4.0 scale
                g10 = enrollment.grade or 0.0
                if g10 >= 9.0:
                    g4 = 4.0
                elif g10 >= 8.5:
                    g4 = 3.7
                elif g10 >= 8.0:
                    g4 = 3.5
                elif g10 >= 7.0:
                    g4 = 3.0
                elif g10 >= 6.0:
                    g4 = 2.5
                elif g10 >= 5.0:
                    g4 = 2.0
                elif g10 >= 4.5:
                    g4 = 1.5
                elif g10 >= 4.0:
                    g4 = 1.0
                else:
                    g4 = 0.0

                total_credits += credits
                total_points += g4 * credits
            rec.gpa = (total_points / total_credits) if total_credits > 0 else 0.0
            
