# -*- coding: utf-8 -*-
{
    'name': "KSA Zatca Phase-2 Total Discount",
    'summary': """
        Phase-2 of ZATCA e-Invoicing(Fatoorah): Integration Phase, its include solution for KSA business""",
    'description': """
        Phase-2 of ZATCA e-Invoicing(Fatoorah): Integration Phase, its include solution for KSA business
    """,
    'live_test_url': 'https://youtu.be/cM1n_t_FnKQ',
    "author": "Alhaditech",
    "website": "www.alhaditech.com",
    'license': 'OPL-1',
     'images': ['static/description/cover.png'],
    'category': 'Invoicing',
    'version': '14.6.0',
    'price': 890, 'currency': 'USD',
    'depends': ['account', 'sale', 'l10n_sa_invoice', 'purchase', 'account_debit_note', 'account_edi_facturx','ksa_zatca_integration'],
    'external_dependencies': {
        'python': ['cryptography', 'lxml', 'qrcode', 'fonttools']
    },
    'data': [
        "views/account_move.xml",
    ],
}
