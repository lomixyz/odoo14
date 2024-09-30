# -*- coding: utf-8 -*-
{
    'name': "custom_invoice",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'stock', 'l10n_sa_invoice'],

    # always loaded
    'data': [
        'views/custom_invoice_report.xml',
        'views/custom_sale_order_report.xml',
        'views/delivery_note.xml',
        'views/custom_purchase_report.xml',
        'views/views.xml',
        'views/custom_footer.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
