from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class KsGlobalDiscountInvoice(models.Model):
    # _inherit = "account.invoice"
    """ changing the model to account.move """
    _inherit = "account.move"

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
    ks_enable_discount = fields.Boolean(related='company_id.ks_enable_discount')

    ks_amount_discount_descount = fields.Monetary(string='Total Before Discount', readonly=True, compute='ks_calculate_discount', store=True,
                                         track_visibility='always')
    ks_product_discount = fields.Many2one('product.product', string="Discount Product", related='company_id.ks_product_discount', readonly=False)

    @api.depends('company_id.ks_enable_discount')
    def ks_verify_discount(self):
        for rec in self:
            rec.ks_enable_discount = rec.company_id.ks_enable_discount
            rec.ks_product_discount = rec.company_id.ks_product_discount

    @api.depends('invoice_line_ids.price_subtotal', 'ks_global_discount_rate', 'ks_global_discount_type')
    def ks_calculate_discount(self):
        for rec in self:
            if  rec.company_id.ks_enable_discount :
                already_exists = rec.invoice_line_ids.filtered(lambda line: line.product_id == rec.ks_product_discount)
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
               
                tax = rec.ks_product_discount.taxes_id.filtered(lambda line: line.company_id == rec.company_id)
                
                line = [(0,0,{'product_id':rec.ks_product_discount ,
                        'name':rec.ks_product_discount.name,
                        'price_unit':-1 * rec.ks_amount_discount,
                        'account_id' :rec._get_computed_Proaccount(),
                        'currency_id':self.company_id.currency_id,
                        'price_subtotal': (-1 * rec.ks_amount_discount),
                        'product_uom_id': rec.ks_product_discount.uom_id.id,
                        'tax_ids':  [(6, 0, tax.ids)]
                        })]
                if rec.ks_global_discount_rate > 0 and not already_exists :
                    rec.invoice_line_ids = line
                else:
                    already_exists.update({'price_unit':-1 * rec.ks_amount_discount,'price_subtotal': (-1 * rec.ks_amount_discount),})
                rec.ks_amount_discount_descount = rec.amount_untaxed + rec.ks_amount_discount
                
                rec.total_discount_amount += rec.ks_amount_discount
                print("total_discount_amount",rec.total_discount_amount)
                for line in rec.invoice_line_ids:
                    line._onchange_mark_recompute_taxes()
                rec._compute_amount()
                rec._get_discount_amount()
                rec._onchange_currency()
                rec._onchange_invoice_line_ids()
                rec._compute_amount()
                rec._recompute_tax_lines(True)
                rec.total_discount_amount =rec.total_discount_amount + rec.ks_amount_discount
        return True

    @api.depends('line_ids.price_unit', 'line_ids.discount','line_ids.quantity')
    def _get_discount_amount(self):
        for rec in self:
            rec.total_discount_amount = sum(rec.line_ids.mapped('discount_amount')) + rec.ks_amount_discount
    def _get_computed_Proaccount(self):
        self.ensure_one()
        self = self.with_company(self.journal_id.company_id)

        if not self.ks_product_discount:
            return

        fiscal_position = self.fiscal_position_id
        accounts = self.ks_product_discount.product_tmpl_id.get_product_accounts(fiscal_pos=fiscal_position)
        if self.is_sale_document(include_receipts=True):
            # Out invoice.
            return accounts['income'] or self.account_id
        elif self.is_purchase_document(include_receipts=True):
            # In invoice.
            return accounts['expense'] or self.account_id

    @api.constrains('ks_global_discount_rate')
    def ks_check_discount_value(self):
        if self.ks_global_discount_type == "percent":
            if self.ks_global_discount_rate > 100 or self.ks_global_discount_rate < 0:
                raise ValidationError('You cannot enter percentage value greater than 100.')
        else:
            if self.ks_global_discount_rate < 0 or self.amount_untaxed < 0:
                raise ValidationError(
                    'You cannot enter discount amount greater than actual cost or value lower than 0.')

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        ks_res = super(KsGlobalDiscountInvoice, self)._prepare_refund(invoice, date_invoice=None, date=None,
                                                                      description=None, journal_id=None)
        ks_res['ks_global_discount_rate'] = self.ks_global_discount_rate
        ks_res['ks_global_discount_type'] = self.ks_global_discount_type
        return ks_res
