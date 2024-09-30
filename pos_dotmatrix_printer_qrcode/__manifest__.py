# -*- coding: utf-8 -*-

{
    'name': 'Pos Dot Matrix Printer QR Code',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'WAY-IST BY ABOZAR',
    'summary': 'Allows you to print receipt from dot matrix printer.',
    'description': "Allows you to print receipt from dot matrix printer.",
    'depends': ['pos_dotmatrix_printer','l10n_sa_pos'],
    'data': [
        'views/templates.xml'
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'images': [
        'static/description/receipt.jpg',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 50,
    'currency': 'EUR',
}
