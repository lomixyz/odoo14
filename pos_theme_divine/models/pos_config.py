# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class PosConfig(models.Model):
    _inherit = "pos.config"

    enable_pos_theme = fields.Boolean(string="Enable Pos Theme",help="Enable Pos Theme", default=True)
    wk_max_order_shows = fields.Integer(string="Maximum Orders Allowed in Order Selector", default=3)
    drawer_closed = fields.Boolean(string="Keep Side Drawer Closed",help="Keep Side Drawer Closed", default=False)
    discount_ids = fields.Many2many('pos.custom.discount',string="Discounts")
    allow_custom_discount = fields.Boolean('Allow Customize Discount',default = True)
    allow_security_pin = fields.Boolean('Allow Security Pin',default = False)
    theme_color = fields.Selection([('#FC4078', 'French Rose'), 
									('#1CCEF4', 'Bright Sky Blue'),
									('#F15F6B', 'Light Carmine'),
									('#FE7D35', 'Mango Orange'),
									('#18DB70', 'Tealish Green'),
									('#755FFF', 'Light Slate Blue'),
									('#0FDDFF', 'Neon Blue'),
									('#9757D7', 'Lavender Indigo'),
									('#27C499', 'Greenish Teal'),
									('#FF592C', 'Portland Orange'),
									('#D3AC5F', 'Desert'),
									('#78A660', 'Dull Green'),
									('#FF1A27', 'Torch Red'),
									], string="Theme Color", default='#27C499')
    color_option_1 = fields.Char(string="Color Option 1", default="#FC4078")
    color_option_2 = fields.Char(string="Color Option 2", default="#1CCEF4")
    color_option_3 = fields.Char(string="Color Option 3", default="#F15F6B")
    color_option_4 = fields.Char(string="Color Option 4", default="#FE7D35")
    color_option_5 = fields.Char(string="Color Option 5", default="#18DB70")
    color_option_6 = fields.Char(string="Color Option 6", default="#755FFF")
    color_option_7 = fields.Char(string="Color Option 7", default="#0FDDFF")
    color_option_8 = fields.Char(string="Color Option 8", default="#9757D7")
    color_option_9 = fields.Char(string="Color Option 9", default="#27C499")
    color_option_10 = fields.Char(string="Color Option 10", default="#FF592C")
    color_option_11 = fields.Char(string="Color Option 11", default="#D3AC5F")
    color_option_12 = fields.Char(string="Color Option 12", default="#78A660")
    color_option_13 = fields.Char(string="Color Option 13", default="#FF1A27")
    product_background_color = fields.Selection([('white', 'White'), ('black', 'Black')], string="Product Background Color", default="black")

    @api.model
    def get_languages(self):
        res = {}
        languages = dict(self.env['res.lang'].get_installed())
        return languages

class POsCustomDiscount(models.Model):
	_name = "pos.custom.discount"

	name = fields.Char(string="Name" , required=1)
	discount_percent = fields.Float(string="Discount Percentage",required=1)
	description = fields.Text(string="Description" )
	available_in_pos = fields.Many2many('pos.config',string="Available In Pos")

	@api.constrains('discount_percent')
	def check_validation_discount_percent(self):
		"""This is to validate discount percentage
		"""
		if self.discount_percent <= 0 or self.discount_percent>100 :
			raise ValidationError("Discount percent must be between 0 and 100.")

class PosOrderLine(models.Model):
	_inherit = 'pos.order.line'
	custom_discount_reason = fields.Text('Discount Reason')

	@api.model
	def _order_line_fields(self, line, session_id=None):
		fields_return = super(PosOrderLine,self)._order_line_fields(line,session_id)
		fields_return[2].update({'custom_discount_reason':line[2].get('custom_discount_reason','')})
		return fields_return
