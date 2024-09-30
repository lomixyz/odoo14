# -*- coding: utf-8 -*-
{
'name': 'Tax Report',
'summary': 'Tax Report, Print Tax Excel Report, Tax PDF Report, Financial Tax PDF '
           'Report, Odoo Tax Report, VAT, Value Added Tax, Accounting, Reporting, '
           'Financial, Excel Format, Journal Audit Report, Journal Items, Balance Sheet, '
           'Ledger',
'version': '14.1.0.0.4',
'category': 'Accounting',
'website': 'https://www.open-inside.com',
'description': '''
		Tax Report		 
    ''',
'images': ['static/description/cover.png'],
'author': 'Openinside',
'license': 'OPL-1',
'price': 99.0,
'currency': 'USD',
'installable': True,
'depends': ['account', 'oi_excel_export', 'oi_base'],
'data': ['views/action.xml',
          'views/menu.xml',
          'views/tax_report_wizard.xml',
          'security/ir.model.access.csv'],
'qweb': [],
'odoo-apps': True,
'application': False
}