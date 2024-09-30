# -*- coding: utf-8 -*-ls.
{
    'name': "custom maintenance",
    'summary': "custom maintenance",
    'description': """
custom maintenance

    """,
    'category': '',
    'version': '1.0',
    'depends': ['maintenance', 'hr_maintenance', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/wiz.xml',
        'views/view.xml',
    ],
    'application': True,
}
