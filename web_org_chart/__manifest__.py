# See LICENSE file for full copyright and licensing details.
{
    'name': 'Appness HR: Organizational Chart',
    'summary': """Hierarchical Structure of Companies Employee""",
    'description': """Hierarchical Structure of Companies Employee
                Generate organization chart
                Odoo chart view
                Odoo tree structure graph
                Employee hierarchy chart
                Employee structure
                Employee level and grade
    """,
    'version': '14.0.1',
    'category': 'Extra Tools',
    'author': 'Appness Technology',
    'website': 'https://www.appness.net',
    'depends': ['hr'],
    'data': [
        "views/templates.xml",
        "views/web_org_chart.xml",
    ],
    'qweb': ['/static/src/xml/*.xml'],
    'images': ['static/description/Web_OrgChart.png'],
    'installable': True,
}
