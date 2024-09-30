# -*- coding: utf-8 -*-
{
    'name': "Payroll Payment",
    'description': """
        Allows you to create payments from within the payroll batch.
    """,
    'author': "Appness Technology Co.Ltd.",
    'website': "http://www.app-ness.com",
    'category': 'hr',
    'version': '13.1.0.1',
    'price': 19,
    'currency': 'USD',
    'depends': ['hr_payroll_account'],
    'data': [
        'wizard/hr_payroll_register_payment.xml',
        'wizard/hr_payroll_batchwise_register_payment.xml',
        'views/hr_payslip_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'images': [
        'static/description/payroll_payment.png',
    ]
}