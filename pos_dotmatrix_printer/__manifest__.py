# -*- coding: utf-8 -*-

{
    'name': 'Pos Dot Matrix Printer',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'ErpMstar Solutions',
    'summary': 'Allows you to print receipt from dot matrix printer.',
    'description': "Allows you to print receipt from dot matrix printer.",
    'depends': ['point_of_sale'],
    'data': [
        'views/views.xml',
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
