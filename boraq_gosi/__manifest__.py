{
    'name': "WAY HR GOSI",
    'version': '14.0',
    'summary': """GOSI Contribution for Saudi Government""",
    'description': """GOSI Contribution for Saudi Government From Employee and Company""",
    'category': 'Human Resources',
    'author': 'WAY For IST',
    'company': 'WAY For IST',
    'maintainer': 'WAY For IST',
    'website': "https://w-ist.com",
    'depends': ['hr_payroll'],
    'data': [
        'views/gosi_view.xml',
        'views/sequence.xml',
        'data/rule.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    "images": ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'price': 180,
    "currency":  "EUR",
}
