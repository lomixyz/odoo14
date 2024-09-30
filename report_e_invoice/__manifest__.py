# Copyright 2021 Khabir
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Report E Invoice',
    'description': """
        E-Invoice Report""",
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Expert Co. Ltd.',
    'website': 'http://www.exp-sa.com',
    'depends': ['account', 'sale', 'purchase', 'point_of_sale'],
    'data': [
        'views/res_partner.xml',
        'report/assets.xml',
        'views/templates.xml',
        'report/e_invoice.xml'
    ],
    'qweb': [
        'static/src/xml/pos_receipt.xml',
    ],
    'demo': [
    ],
}
