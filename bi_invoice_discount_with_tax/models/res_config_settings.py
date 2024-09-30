# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import UserError, ValidationError



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tax_discount_policy = fields.Selection([('tax', 'Tax Amount'), ('untax', 'Untax Amount')],string='Discount Applies On',default='tax',
        default_model='sale.order')
    sale_account_id = fields.Many2one('account.account', 'Sale Discount Account',domain=[('user_type_id.name','=','Expenses'), ('discount_account','=',True)])
    purchase_account_id = fields.Many2one('account.account', 'Purchase Discount Account',domain=[('user_type_id.name','=','Income'), ('discount_account','=',True)])

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        tax_discount_policy = ICPSudo.get_param('bi_invoice_discount_with_tax.tax_discount_policy')
        sale_account_id = ICPSudo.get_param('bi_invoice_discount_with_tax.sale_account_id')
        purchase_account_id = ICPSudo.get_param('bi_invoice_discount_with_tax.purchase_account_id')
        res.update(tax_discount_policy=tax_discount_policy,sale_account_id=int(sale_account_id),purchase_account_id=int(purchase_account_id),)
        return res

    def set_values(self):

        super(ResConfigSettings, self).set_values()
        for rec in self:
            ICPSudo = rec.env['ir.config_parameter'].sudo()
            ICPSudo.set_param('bi_invoice_discount_with_tax.sale_account_id',rec.sale_account_id.id)
            ICPSudo.set_param('bi_invoice_discount_with_tax.purchase_account_id',rec.purchase_account_id.id)
            ICPSudo.set_param('bi_invoice_discount_with_tax.tax_discount_policy',str(rec.tax_discount_policy))





