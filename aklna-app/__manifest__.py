# -*- coding: utf-8 -*-
{
    'name': "Aklna App",

    'summary': """
        API For Aklna Mobile App""",

    'description': """
        API To Aklna Mobile App To Link With Odoo To Get , Read , Update , And Delete Data
    """,

    'author': "Ghanem Ibrahim",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
