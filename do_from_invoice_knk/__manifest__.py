# -*- coding: utf-8 -*-
###############################################################################
# Author      : Kanak Infosystems LLP. (<https://www.kanakinfosystems.com/>)
# Copyright(c): 2012-Present Kanak Infosystems LLP.
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.kanakinfosystems.com/license>
###############################################################################

{
    'name': 'Create Delivery Order From  Customer Invoice',
    'summary': 'Create Delivery Order From Customer Invoice module is used to create picking from invoice when invoice is in draft state.| Delivey Order | Invoicing | Customer Invoice | Delivery Orders | Create Picking | Outgoing Shipments | Return Picking | Incoming Delivery order | Update Invoice Line |',
    'version': '1.0',
    'license': 'OPL-1',
    'description': """
Create Delivery Order From Customer Invoice module is used to create picking from invoice when invoice is in draft state.
====================
This module allows to create picking from invoice.
.""",
    'category': 'Accounting/Accounting',
    'depends': ['stock_account'],
    'author': 'Kanak Infosystems LLP.',
    'images': ['static/description/banner.gif'],
    'website': 'https://www.kanakinfosystems.com',
    'data': [
        'security/ir.model.access.csv',
        'views/account_move.xml',
        'views/stock_view.xml',
        'wizard/return_invoice_qty.xml',
    ],
    'price': 40,
    'currency': 'EUR',
    'auto_install': False,
    'application': False,
    'installable': True,
    'live_test_url': 'https://www.youtube.com/watch?v=rlhtcx088pQ',
}
