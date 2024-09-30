# -*- coding: utf-8 -*-
{
    'name': "Account Custody",

    'summary': """
        Financial Custodies""",

    'description': """
    """,

    'author': "way",
    'website': "http://www.w-ist.com",

    'category': 'Accounting & Finance',
    'version': '14.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'account', 'hr'],

    # always loaded
    'data': [
        'data/custody_data.xml',
        'security/account_security.xml',
        'security/ir.model.access.csv',
        'wizards/custody_line_wizard.xml',
        'views/views.xml',
        'views/report_custody.xml',
        # 'views/custody_detail_report.xml',
        'reports/custody_information.xml',

        'wizards/custody_report_wizard.xml',

    ]
}
