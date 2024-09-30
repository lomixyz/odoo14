# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api,_
from xlwt.Style import easyfont
from odoo.exceptions import UserError
from datetime import timedelta

class StockValuation(models.Model):
    _name = 'sh.stock.valuation'
    _description = 'Stock Valuation'
    
    default_code=fields.Char(string="Default Code")
    product_id = fields.Many2one(string='Product Name',comodel_name='product.product')
    categ_id = fields.Many2one(string='Category',comodel_name='product.category')
    sh_open_stock=fields.Float(string="Open Stock")
    sh_sale_qty=fields.Float(string="Sales")
    sh_purchase_qty=fields.Float(string="Purchase")
    sh_adjustment_qty=fields.Float(string="Adjustment")
    sh_transfer_qty=fields.Float(string="Transfer")
    sh_close_stock=fields.Float(string="Close Stock")
    sh_costing=fields.Float(string="Costing")
    sh_valuation=fields.Float(string="Valuation")
    