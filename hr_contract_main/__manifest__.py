# -*- coding: utf-8 -*-
{
    'name': "Appness HR : Contract Main",
    'summary': """Contract Main""",
    'description': """Contract Main""",
    'author': "Appness Technology",
    'website': "http://www.appness.net",
    'category': 'HR',
    'version': '14.0.1',
    'sequence': 2,
    # any module necessary for this one to work correctly
    'depends': ['hr_contract','hr_contract_benefit'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_config_setting.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}