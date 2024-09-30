# -*- coding: utf-8 -*-
{
    'name': "Rustom Rent",

    'summary': """
        THIS MODULE CHECK DATE RENT STATR DATE AND END DATE IS A RENGING OR NOR A RENTING""",

    'description': """
        Long description of module's purpose
    """,

    'author': "WAY-IST BY TEAM WAY",
    'website': "http://www.W-IST.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_renting'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
