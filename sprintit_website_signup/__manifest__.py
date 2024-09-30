# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO Open Source Management Solution
#
#    ODOO Addon module by Sprintit Ltd
#    Copyright (C) 2021 Sprintit Ltd (<http://sprintit.fi>).
#
##############################################################################
{
    'name': "Website Portal Login",
    'version': '13.0.0.1',
    'summary': '''This module enables approving the users signed up from the Portal and manages signup requests from website.
                signup approve signup verify signup approval.''',
    'category': 'Extra Tools',
    'license': 'LGPL-3',
    'author': 'SprintIT',
    'maintainer': 'SprintIT',
    'website': 'http://www.sprintit.fi',
    'depends': ['website', 'auth_signup'],
    'data': [
        'security/security.xml',
        'data/signup_template_data.xml',
        'data/mail_channel_data.xml',
        'views/template.xml',
        'views/res_config_settings.xml',
        'views/res_users.xml',
    ],
    'images': ['static/description/cover.jpg',],
    'installable': True,
    'application': False,
    'auto_install': False,
}
