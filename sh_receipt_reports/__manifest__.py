# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name" : "All in one Receipt Reports - Sales, Purchase, Accounting, Inventory | Sale Orer Receipt Report | Purchase Order Receipt Report | Invoice Receipt Report | Inventory Receipt Report",
    "author" : "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",        
    "category": "Extra Tools",
    "summary": "print sales report,purchase order report, sale order report odoo, print invoice report module, print request for quotation report, account report, warehouse receipt report odoo",
    "description": """Currenlty in odoo we can't print reports in receipt printer, This module useful to print reports as receipt. 
So you can now easily print many odoo standard reports in receipt printer. You don't need to switch to other printer.
print sales receipt report app, print purchase order report, print sale order report odoo, print invoice report module, print receipt report odoo""",      
    "version":"12.0.1",
    "depends" : [
            "sale_management",
            "sale",     
            "account",
            "qr_code_invoice_app"
        ],
    "application" : True,
    "data" : [
        
            "data/report_paperformat.xml",
            "report/external_layout_template.xml",
            
            "report/sale_receipt_template.xml",
            "report/sale_report.xml",
            
            "report/invoice_receipt_template.xml",
            "report/invoice_report.xml",                                                                                                                                                 
            ],                       
    "images": ["static/description/background.png",],              
    "auto_install":False,
    "installable" : True,
    "price": 50,
    "currency": "EUR"   
}




