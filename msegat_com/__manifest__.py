# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Msegat SMS',
    'summary': 'Design and send SMS',
    'description': '',
    'version': '1.0',
    'category': 'Tools',
    'depends': [
        'base',
    ],
    'data': [
        'views/res_config_settings_views.xml',
        'views/views.xml',
        'security/ir.model.access.csv',
    ],
    'application': True,
}
