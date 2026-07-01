{
    'name': 'Estate Management',
    'version': '1.0',
    'category': 'Real Estate',
    'summary': 'Manage properties, clients, and sales in the real estate industry.',
    'description': """
        This module provides features for managing properties, clients, and sales in the real estate industry.
        It allows you to track property listings, client information, and sales transactions efficiently.
    """,
    'author': 'Phuong',

    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',

        'views/estate_property_views.xml',
    ],
    'installable': True,
    'application': True,
}