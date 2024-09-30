# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Google Meet Connector',
    'version': '1.0',
    'summary': 'Google Meet Connector for Online Meeting and Conference with Google Meet',
    'sequence': 30,
    'description': """ Google Meet Connector for Online Meeting and Conference with Google Meet """,
    'category': 'Extra Tools',
    'author': 'Aurayan Consulting Services',
    'website': '',
    'depends': [
        'google_calendar'
    ],
    'data': [
        'views/calendar_views.xml',
    ],
    'images': [
        'static/description/main_screen.png'
    ],
    'price': 59.0,
    'currency': 'EUR',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}
