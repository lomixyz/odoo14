# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

{
    'name': 'Tap Payment Gateway',
    'category': 'Accounting/Accounting',
    'version': '2.2',
    'summary': '''
Tap Payment Gateway module is used in payment method to simplifies online payment.
KNET | MADA | BENEFIT | Oman Net | Apple Pay | Visa | Mastercard | meeza | Amex
Refund | Subscription | Save Card | Use save card to pay
    ''',
    'description': """Tap Payment Gateway module is used in payment method to simplifies online payment.""",
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://www.kanakinfosystems.com',
    'depends': ['payment'],
    'images': ['static/description/banner.jpg'],
    'data': [
        'views/tap.xml',
        'views/tap_view.xml',
        'data/tap_data.xml',
        'data/cron_data.xml'
    ],
    'license': 'OPL-1',
    'sequence': 1,
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 50,
    'currency': 'EUR',
    'live_test_url': 'https://www.youtube.com/watch?v=a6Ftng-0Rtg',
    'post_init_hook': 'create_missing_journal_for_acquirers',
    'uninstall_hook': 'uninstall_hook',
}
