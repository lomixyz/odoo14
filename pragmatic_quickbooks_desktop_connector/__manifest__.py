{
    'name': 'Odoo QuickBooks Desktop (QBD) Connector',
    'version': '14.0.0.7',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': 'www.pragtech.co.in',
    'category': 'Sales, Invoice',
    'summary': 'Synchronise data between Odoo and Quickbooks Desktop. Odoo Quickbooks Desktop Connector Odoo Quickbooks Desktop connector Quickbooks Odoo Quickbooks Odoo connector odoo quickbooks integration',
    'description': """
QuickBooks Desktop Odoo (QBD) Connector
=======================================
This connector will help user to import/export following objects in quickbooks.
    * Accounts
    * Customer
    * Product
    * Bill of Material
    * Sales Order
    * Invoices.
<keywords>
Odoo Quickbooks Desktop Connector
Odoo Quickbooks
Odoo Quickbooks Desktop 
Quickbooks
Quickbooks desktop
Quickbooks desktop connector
Quickbooks Odoo
Quickbooks Odoo connector
odoo quickbooks integration
    """,
    'depends': ['base', 'mrp', 'contacts', 'sale_management', 'base_setup', 'account', 'stock', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_company_views.xml',
        'views/ir_sequence.xml',
        'views/account_view.xml',
        'views/res_partner_view.xml',
        'views/product_view.xml',
        'views/sale_order_view.xml',
        'views/qbd_payment_method_view.xml',
        'views/qbd_tax_code_view.xml',
        'views/invoice.xml',
        'views/purchase_view.xml',
        'views/qbd_logger.xml',
        'views/serveractions.xml',
        'views/schedular.xml',
        'wizards/message_view.xml',
    ],
    'images': ['images/animated-quickbook-desktop.gif'],
    'live_test_url': 'http://www.pragtech.co.in/company/proposal-form.html?id=103&name=quickbook-connector',
    'price': 499,
    'currency': 'EUR',
    'license': 'OPL-1',
    'auto_install': False,
    'application': False,
    'installable': True,
}
