# -*- coding: utf-8 -*-
# Part of Softhealer Technologies

{
    "name": "Account Parent & Child Hierarchy | Chart Of Account Hierarchy | Folded Chart Of Account Hierarchy | Unfolded Chart Of Account Hierarchy",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Accounting",
    "summary": "Parent Account Child Account Add Parent Account Chart Of Account Hierarchy Based On Target Moves Chart Of Account Hierarchy By Account Based Chart Of Account Hierarchy Based On Account Multiple Chart Of Account Hierarchy Between Dates Odoo",
    "description": """This module helps to set the hierarchy of parent-child accounts in chart of accounts. You can set accounts in one hierarchy to manage multiple chart of accounts in one chart of account. You can see hierarchy in folded-unfolded view. You can generate chart of account hierarchy based on any dates,fold/unfold, account/account type & target moves.""",
    "version": "14.0.1",
    "depends": ["account_reports", "account"],
    "data": [
        
        'data/account_type_data.xml',
        'security/account_groups.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'wizard/account_hierarchy_wizard.xml',
        'views/account.xml',
        'views/res_config_settings.xml',
        'views/account_hierarchy_report.xml',
        'reports/account_report_coa.xml',
      
    ],

    'qweb': [
        "static/src/xml/*.xml",
    ],
         
    "auto_install":False,
    "installable": True,
    "application": True,
    "license": "OPL-1",
    "images": ["static/description/background.gif", ],
    "price": "20",
    "currency": "EUR" 
} 
