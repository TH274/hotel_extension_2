{
    'name': 'Hotel Extension 2',
    'version': '1.0',
    'license': 'LGPL-3',
    'summary': 'Module for adding more requied model',
    'description': 'This module helps in managing the sales operations of a hotel.',
    'author': 'Your Name',
    'category': 'Sales',
    'depends': ['base', 'sale', 'hotel_management'],
    'data': [
        "security/ir.model.access.csv",
        'views/room_inherit_views.xml',
        'views/customer_inherit_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}