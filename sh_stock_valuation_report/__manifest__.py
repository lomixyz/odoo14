# -*- coding: UTF-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Inventory Valuation Report",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Warehouse",
    "license": "OPL-1",
    "summary": "Warehouse Valuation Reports Real Time Stock Valuation Reports Real Time Inventory Valuation Reports Real-Time Stock Valuation Reports Real-Time Inventory Valuation Reports In PDF Valuation Reports In XLSX Valuation Reports In Excel Valuation Reports Odoo Multi Company Wise Valuation Reports Multi Company Wise Stock Valuation Reports Multi Company Wise Inventory Valuation Reports Past Date Stock With Valuation Report Print product inventory Valuation Report Stock Inventory Real Time Report Periodically Stock valuation Report stock report inventory report Real Time Valuation Report Real Time Stock Report Product Stock Valuation Filter by Date Report Remaining Inventory Valuation Report Inventory Valuation Through PDF Inventory Valuation Through Excel Inventory Valuation Through XLSX Inventory Valuation Between Particular Dates View Inventory Valuation Reports FIFO product inventory Valuation Report real time inventory analysis report real time stock analysis report warehouse analysis report stock card stock ledger stock ledger excel report inventory report Detailed inventory valuation report Stock Reports Inventory Reports",
    "description": """Using this stock valuation report module, you can simplify inventory management. This report shows the inventory valuation as selected time and date with the warehouse and company. Reports can be generated based on categories and products. You can choose PDF or XLS formats for analysis.""",
    "version": "14.0.1",
    "depends": [
        "sale_management",
        "purchase",
        "stock",
        'sh_backend_base',
    ],
    "application": True,
    "data": [
        'security/sh_stock_valuation_groups.xml', 
        'security/ir.model.access.csv',
        'wizard/sh_stock_valuation_wizard_views.xml', 
        'report/sh_stock_valuation_report_template.xml',
        'views/sh_stock_valuation_views.xml', 
    ],
    "images": [
        "static/description/background.png",
    ],
    "auto_install": False,
    "installable": True,
    "price": 42.8,
    "currency": "EUR"
}
