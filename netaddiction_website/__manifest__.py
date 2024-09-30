{
    "name": "Netaddiction Website",
    "summary": """
        Netaddiction Website
    """,
    "author": "Netaddiction",
    "category": "Custom Development",
    "version": "14.0.1.7.0",
    "description": """
        This module will enhance the odoo features
    """,
    "depends": ["website_sale", "fb_pixel", "facebook_ads_feeds"],
    "data": [
        "data/cron.xml",
        "views/web/product.xml",
        "views/web/homepage.xml",
        "views/web/lego_shop.xml",
        "views/web/warner_shop.xml",
        "views/web/harry_potter_shop.xml",
        "views/web/offer_shop.xml",
    ],
    "installable": True,
    "application": False,
}
