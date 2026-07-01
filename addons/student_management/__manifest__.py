{
    'name': 'Student Management',
    'version': '1.0',
    'category': 'Education',
    'summary': 'Manage students',
    'author': 'Phuong',

    'depends': ['base'],

    'data': [
        'security/ir.model.access.csv',
        'security/student_security.xml',
        'security/student_record_rules.xml',
        
        
        'views/student_views.xml',
        'views/department_views.xml',
        'views/subject_views.xml',
        'views/teacher_views.xml',
        
        # 'data/department_data.xml',
    ],

    'installable': True,
    'application': True,
}