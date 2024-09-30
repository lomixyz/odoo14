# -*- coding: utf-8 -*-

# Part of GECOERP. See LICENSE file for full copyright and licensing details.

{
    'name': "Costos Actuales el lad Hojas de Costos",
    'price': 17000.00,
    'version': '3.1.14',
    'depends': [
        'gecoerp_job_costing_management',
    ],
    'category' : 'Services/Project',
    'license': 'Other proprietary',
    'currency': 'MXN',
    'summary': """Esta aplicación actualiza los gastos reales en la hojas de costos.""",
    'description': """
Esta aplicación actualiza los gastos reales en la hojas de costos.
""",
    'author': "MASTER CONSULTING RESOURCES & CO. S.C.",
    'website': "https://www.gecoerp.com",
    'support': 'contacto@gecoerp.com',
    'data':[
        'views/job_cost_line_view.xml',
        'report/job_costing_report.xml'
    ],
    'installable' : True,
    'application' : False,
    'auto_install' : False,
}