# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol. (<https://www.droggol.com/>)

from odoo import api, fields, models


class DrProductTabs(models.Model):
    _name = 'dr.product.tabs'
    _description = 'Product Tabs'
    _order = 'sequence,id'

    name = fields.Char(string='Title', required=True, translate=True)
    icon = fields.Char(default='list')
    content = fields.Html()
    sequence = fields.Integer(string='Sequence')
    product_id = fields.Many2one('product.template')
    tag_id = fields.Many2one('dr.product.tags')
