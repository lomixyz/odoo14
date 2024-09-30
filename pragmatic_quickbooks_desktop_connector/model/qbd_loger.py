from odoo import api, fields, models, _
import requests
import ast
from odoo.exceptions import UserError, ValidationError

class QBDLoger(models.Model):
    _name = 'qbd.loger'
    _description = 'QBD Logger'
    operation = fields.Char("Operation")
    odoo_id = fields.Char('Odoo ID')
    qbd_id = fields.Char('QBD ID')
    message = fields.Char('Message')
    # res_company_id = fields.Many2one('res.company')

class QBD_DuplicateLogger(models.Model):
    _name = 'qbd.duplicates.logger'
    _description = 'QBD Duplicates Logger'

    odoo_id = fields.Char('Odoo ID')
    name = fields.Char("Name")
    parent_dcode = fields.Char("Parent/Default Code")
    qbd_id = fields.Char("Quickbooks ID")
    type = fields.Selection([
        ('product', 'Product'),
        ('vendor', 'Vendor'),
        ('customer', 'Customer'),
        ], string='Type')
    message = fields.Char('Message')

class QBD_OrderInvoiceLogger(models.Model):
    _name = 'qbd.orderinvoice.logger'
    _description = 'QBD Order Invoice Logger'
    odoo_id = fields.Char('Odoo ID')
    name = fields.Char("Name")
    qbd_id = fields.Char("Quickbooks ID")
    type = fields.Selection([
        ('sale', 'Sales Order'),
        ('invoice', 'Invoices'),
        ], string='Type')
    message = fields.Char('Message')

class QBD_ConnectionLogger(models.Model):
    _name = 'qbd.connection.logger'
    _rec_name = 'message'
    _description = 'QBD Connection Logger'

    message = fields.Char('Message')
    type = fields.Char('Type')
    date = fields.Datetime('Date')
