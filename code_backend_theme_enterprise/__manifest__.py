# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2021-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

{
    "name": "Backend Theme Enterprise",
    "description": """Custom backend theme for Odoo 14, Backend Theme, Theme""",
    "summary": "Custom Theme V14 is an attractive theme for backend",
    "category": "Themes/Backend",
    "version": "14.0.1.0.1",
    'author': 'PSS Ltd.',
    'company': 'PSS Ltd.',
    'maintainer': 'PSS Ltd.',
    'website': "https://www.exp-sa.com",
    "depends": ['base', 'web_enterprise', 'web'],
    "data": [
        'views/assets.xml',
        'views/icons.xml',
    ],
    "qweb": [
        'static/src/xml/styles.xml',
        'static/src/xml/top_bar.xml',
        'static/src/xml/sidebar.xml',
        'static/src/xml/base.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
