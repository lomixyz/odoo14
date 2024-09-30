# -*- coding: utf-8 -*-
{
    'name': 'All in One Invoice Reports Odoo',
    'version': '14.0.0.2',
    'category': 'Accounting',
    'summary': 'All invoice reports All account reports invoice day book report invoice payment report product invoice summary report invoice details report invoice excel report invoice xls report invoice category report all in one invoice reports invoice day wise reports',
    'description' :"""
        All in One Invoice reports odoo app helps users to print invoice day wise reports, payment report for invoice, product sales summary reports, invoice report by sales person report, highest selling products report, top customer product report, invoice day book report with particular date range for particular company in XLS and PDF format. Users can also print excel reports for single or multiple invoices.
    """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.com',
    "price": 75,
    "currency": 'EUR',
    'depends': ['base', 'account','sale_management', 'stock'],
    'data': [
        'security/sample_security.xml',
        'security/ir.model.access.csv',


        'wizard/day_wise_product_invoice_view.xml',
        'wizard/invoice_book_day_report_view.xml',
        'wizard/invoice_summary_view.xml',
        'wizard/sale_person_view.xml',
        'wizard/invoice_payment_view.xml',
        'wizard/top_customers_views.xml',
        'wizard/update_selling_product_view.xml',
        'wizard/invoice_excel_report_view.xml',
         'wizard/invoice_summary_report_view.xml',


        'report/all_in_one_report.xml',
        'report/day_wise_report_card.xml',
        'report/invoice_book_day_report_template.xml',
        'report/invoice_summary_report_card.xml',
        'report/invoice_person_report_card.xml',
        'report/invoice_payment_report_card.xml',
        'report/top_customer_report_card.xml',
        'report/top_selling_product_card.xml',
        'report/invoice_order_category_report_template.xml',
        'report/invoice_summary_report_template.xml',

    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/FV1b-ilVlCw',
    "images":['static/description/Banner.gif'],
}
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

