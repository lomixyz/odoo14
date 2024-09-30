# -*- coding: utf-8 -*-
{          
    'name': "Appness HR: Payroll Bank Report",
    'summary': """This report for payroll bank report""",
    'description': """This report for payroll bank report""",
    'author' : 'Appness Technology',
    'website': 'https://www.appness.net',
    'category': 'report',
    'version' : '14.0.1',
    'sequence': 26,
    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_employee_main','hr_payroll'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'security/record_rule.xml',
        'views/views.xml',
        'wizard/bank_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}