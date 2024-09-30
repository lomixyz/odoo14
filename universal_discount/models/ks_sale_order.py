# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class KsGlobalDiscountSales(models.Model):
    _inherit = "sale.order"

    ks_global_discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')],
                                               string='Universal Discount Type',
                                               readonly=True,
                                               states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                               default='amount')
    ks_global_discount_rate = fields.Float('Universal Discount',
                                           readonly=True,
                                           states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    ks_amount_discount = fields.Monetary(string='Universal Discount', readonly=True, compute='ks_calculate_discount', store=True,
                                         track_visibility='always')
    ks_enable_discount = fields.Boolean(compute='ks_verify_discount',related='company_id.ks_enable_discount',)

    ks_amount_discount_descount = fields.Monetary(string='Total Before Discount', readonly=True, compute='ks_calculate_discount', store=True,
                                         track_visibility='always')
    ks_product_discount = fields.Many2one('product.product', string="Discount Product", related='company_id.ks_product_discount', readonly=False)


    @api.depends('company_id.ks_enable_discount')
    def ks_verify_discount(self):
        for rec in self:
            rec.ks_enable_discount = rec.company_id.ks_enable_discount
            rec.ks_product_discount = rec.company_id.ks_product_discount

    def _prepare_invoice(self):
        res = super(KsGlobalDiscountSales, self)._prepare_invoice()
        for rec in self:
            res['ks_global_discount_rate'] = rec.ks_global_discount_rate
            res['ks_global_discount_type'] = rec.ks_global_discount_type
        return res

    @api.depends('order_line.price_total', 'ks_global_discount_rate', 'ks_global_discount_type')
    def ks_calculate_discount(self):
        for rec in self:
            already_exists = rec.order_line.filtered(lambda line: line.product_id == rec.ks_product_discount)
            if rec.ks_global_discount_type == "amount":
                rec.ks_amount_discount = rec.ks_global_discount_rate if rec.amount_untaxed > 0 else 0

            elif rec.ks_global_discount_type == "percent":
                
                total_amount =  rec.amount_untaxed + abs(already_exists.price_subtotal)
                if rec.ks_global_discount_rate != 0.0:
                    rec.ks_amount_discount = (total_amount) * rec.ks_global_discount_rate / 100
                else:
                    rec.ks_amount_discount = 0
            elif not rec.ks_global_discount_type:
                rec.ks_amount_discount = 0
                rec.ks_global_discount_rate = 0
            print("ks_product_discount",rec.ks_product_discount.name)
            
            tax = rec.ks_product_discount.taxes_id.filtered(lambda line: line.company_id == rec.company_id)
            print("already_exists",tax.ids)
            
            line = [(0,0,{'product_id':rec.ks_product_discount ,
                    'name':rec.ks_product_discount.name,
                    'price_unit':-1 * rec.ks_amount_discount,
                    'product_uom': rec.ks_product_discount.uom_id.id,
                    'tax_id':  [(6, 0, tax.ids)]
                    })]
            if rec.ks_global_discount_rate > 0 and not already_exists :
                rec.order_line = line
            else:
                print(already_exists.ids)
                already_exists.update({'price_unit':-1 * rec.ks_amount_discount})
            rec.ks_amount_discount_descount = rec.amount_untaxed + rec.ks_amount_discount
        return True


    @api.constrains('ks_global_discount_rate')
    def ks_check_discount_value(self):
        if self.ks_global_discount_type == "percent":
            if self.ks_global_discount_rate > 100 or self.ks_global_discount_rate < 0:
                raise ValidationError('You cannot enter percentage value greater than 100.')
        else:
            if self.ks_global_discount_rate < 0 or self.ks_global_discount_rate > self.amount_untaxed:
                raise ValidationError(
                    'You cannot enter discount amount greater than actual cost or value lower than 0.')


class KsSaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        invoice = super(KsSaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        if invoice:
            invoice['ks_global_discount_rate'] = order.ks_global_discount_rate
            invoice['ks_global_discount_type'] = order.ks_global_discount_type
        return invoice
