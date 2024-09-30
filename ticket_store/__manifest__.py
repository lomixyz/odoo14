# -*- coding: utf-8 -*-
{
    'name': "Ticket Store",

    'summary': """ """,

    'description': """ """,

    'author': "Way IST",
    'website': "http://www.w-ist.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mail', 'portal', 'purchase', 'sale', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/views.xml',
        'views/inherit_view.xml',
    ],

}
