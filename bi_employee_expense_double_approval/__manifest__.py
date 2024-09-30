# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'HR Employee Expense Double Approval in Odoo',
    'version': '14.0.0.1',
    'category': 'Human Resources',
    'summary': 'Human Resource Employee Expense Double Approval Request Employee Expense approval mail notification hr expense approval expense second approval employee expense approve expense triple approval hr expense approval process employee expense validation process',
    'description': """This app allows your employees to create a request for expenses. This app will work with multi currency.
	
	    employee Expense Double Approval Request in odoo,
        employee Expense Request in odoo,
        Expenses/Expense Request in odoo,
        Expense request send with mail in odoo,
        Expense request approval with mail in odoo,
        Expenses/Expense Request to Approve,
        Expenses/Expense Request to Pay,
        employee Expense Multiple Request,
        Expense Request Approve by Expense Manager,
        Integrated with Expense and Accounting Entry,
        Print Advance Expense in odoo,
	
	
	 """,
    
	
	
	'author': 'BrowseInfo',
    "price": 10,
    "currency": 'EUR',
    'website': 'https://www.browseinfo.in',
    'depends': ['base','account','hr_expense','hr'],
    'data': ['views/second_approve.xml',
            'views/mail_template.xml',],
    'installable': True,
    'auto_install': False,
    'application': True,
    'live_test_url': 'https://youtu.be/ZsWrg9qwPt8',
    "images":['static/description/Banner.png'],
}
