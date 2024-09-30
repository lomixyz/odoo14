# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    'name': 'Odoo Fleet Tracking',
    "version": "14.0.1.0.0",
    'summary': 'GPS Tracking for your fleet',
    'author': "Greensboro Web Services",
    'maintainer': 'Tech Support <techsupport@greensborowebservices.com>',
    'category': 'Industries',
    'description': """
Traccar GPS tracking integration with the Fleet Management module.
==================================================================

Track your vehicles with the free and open source Traccar solution.
""",
    'depends': [
        'web_google_maps',
        'fleet'
    ],
    "external_dependencies": {
        "python": ['bokeh==0.13.0'],
    },
    'website': '',
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/templates.xml',
        'views/res_config.xml',
        'views/fleet_vehicle_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'price': 300,
    'currency': 'EUR',
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
}
