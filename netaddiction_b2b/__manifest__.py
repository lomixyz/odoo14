# Copyright 2019-TODAY Openforce Srls Unipersonale (www.openforce.it)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    'name': 'Netaddiction B2B',
    'version': '14.0.1.3.4',
    'category': 'Sale',
    'author': 'Openforce',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'sale',
        'sale_management',
        'product',
        'stock',
        'netaddiction_products',
        'pricelist_dynamic_domain',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/config_views.xml',
        'views/product_views.xml',
        'views/partner_views.xml',
        'views/order_views.xml',
        'views/pricelist_views.xml',
        'views/picking_views.xml',
        'data/cron.xml',
    ],
}
