# -*- coding: utf-8 -*-

from odoo import fields, models,tools,api

class pos_config(models.Model):
    _inherit = 'pos.config' 

    allow_dotmatrix_printer = fields.Boolean(string="Allow DotMatrix Printer",default=True)
    dotmatrix_printers_ip = fields.Char(string="DotMatrix Printer IP address",default="http://0.0.0.0:8100")
    receipt_printing_state = fields.Selection(selection=[('auto', 'Automatically After Validate'),('manually', 'Manually By Button'),('both', 'Both')], string='Receipt Printing State', default='auto')
    show_dotmatrix_receipt = fields.Boolean(string="Show DotMatrix Receipt",default=True)
    headnote = fields.Text(string="Header Note")
    footnote = fields.Text(string="Foot Note")


