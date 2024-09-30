# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Backend Base",
    
    "author": "Softhealer Technologies",
    
    "website": "https://www.softhealer.com",    
    
    "support": "support@softhealer.com",   

    "version": "14.0.3",
    
    "license": "OPL-1",
    
    "category": "Extra Tools",
    
    "summary": "Material Backend Theme Responsive Backend Theme Backmate Backend Theme Fully Functional Backend Theme Flexible Backend Theme Fast Backend Theme Lightweight Backend Theme Animated Backend Theme Modern Backend Theme Multipurpose Backend Theme Odoo Theme",
        
    "description": """Backend Base""",
     
    "depends": ['base_setup'],
        
    "data": [                 
        "security/ir.model.access.csv",
        "views/assets.xml",
        "views/res_config_setting.xml",
        "views/sh_user_push_notification_views.xml",
    ],
    "qweb":
    [
        "static/src/xml/notification_menu.xml",  
    ],
    "images": ["static/description/background.png", ],
    "installable": True,    
    "auto_install": False,    
    "application": True,         
}
