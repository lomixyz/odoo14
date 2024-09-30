# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'K.S.A. - Point of Sale Retail QR Code',
    'author': 'WAY',
    'category': 'Accounting/Localizations/Point of Sale',
    'description': """
K.S.A. POS Localization
=======================================================
    """,
    'license': 'LGPL-3',
    'depends': ['l10n_gcc_pos', 'l10n_sa_invoice','l10n_sa_pos' ,'pos_retail'],
    'data': [
        'pos.xml',
    ],
    'qweb': [
        'static/src/xml/OrderReceipt.xml',
        
    ],
    'auto_install': False,
}
