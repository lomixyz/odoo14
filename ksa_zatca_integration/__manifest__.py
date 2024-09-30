# -*- coding: utf-8 -*-
{
    'name': "KSA Zatca Phase-2",
    'summary': """
        Phase-2 of ZATCA e-Invoicing(Fatoorah): Integration Phase, its include solution for KSA business""",
    'description': """
        Phase-2 of ZATCA e-Invoicing(Fatoorah): Integration Phase, its include solution for KSA business
    """,
    'live_test_url': 'https://youtu.be/_M3PtOBzeC4',
    "author": "Alhaditech",
    "website": "www.alhaditech.com",
    'license': 'AGPL-3',
    'images': ['static/description/cover.png'],
    'category': 'Invoicing',
    'version': '14.7.0',
    # dashboard missing.
    'price': 890, 'currency': 'USD',
    # 'depends': ['account', 'sale', 'l10n_sa', 'purchase', 'account_invoicing'],
        'depends': ['account', 'sale', 'l10n_sa', 'purchase', 'account_debit_note', 'account_edi_ubl_cii'],
    'external_dependencies': {
        'python': ['cryptography', 'lxml', 'qrcode', ]
        # 'python': [ 'fonttools', 'cryptography', 'lxml', 'qrcode', ]
    },
    'data': [
        # 'views/update.xml',
        'security/groups.xml',
        'data/data.xml',
        'views/account_invoice.xml',
        'views/res_partner.xml',
        'views/res_company.xml',
        'views/account_tax.xml',
        'views/product_template.xml',
        'views/product_product.xml',
        'reports/account_invoice.xml',
        'reports/facturx_templates.xml',
        'reports/e_invoicing_b2b.xml',
        'reports/e_invoicing_b2c.xml',
        'reports/report.xml',
    ],
}
