# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################
{
    'name': "Payslip Batch Report",
    'category': 'Payroll',
    'version': '13.0.1.0',
    'author': 'Equick ERP',
    'description': """
        This Module allows to print Payslip Batch PDF & Excel Report.
        * Allows user to print Payslip Batch PDF & Excel report.
        * User can see the salary computation group by the Salary rule Category & Salary Rules.
    """,
    'summary': """ This Module allows to print Payroll PDF & Excel Report. payslip report | employee payslip report | payslip batch report | batch report | batch payslip report. """,
    'depends': ['base', 'hr_payroll_community'],
    'price': 25,
    'currency': 'EUR',
    'license': 'OPL-1',
    'website': "",
    'data': [
        'wizard/wizard_batch_payslip_report.xml',
        'report/report_batch_payslip_template.xml',
        'report/report.xml'
    ],
    'demo': [],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: