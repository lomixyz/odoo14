# -*- coding: utf-8 -*-

# from umalqurra.hijri_date import HijriDate
from hijri_converter import convert
from num2words import num2words

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'sale order term and condition customize'

    note = fields.Html(string="Terms & Conditions", readonly=False)
    use_terms = fields.Boolean(
        string='Default Terms & Conditions',
        config_parameter='sale_order_term_and_condition.use_terms')

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('sale_order_term_and_condition.note', self.note)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['note'] = self.env['ir.config_parameter'].sudo().get_param('sale_order_term_and_condition.note')
        return res


class SaleOrderCustom(models.Model):
    _inherit = 'sale.order'
    _description = 'sale order new custom tab'

    def get_note(self):
        note = self.env['ir.config_parameter'].sudo().get_param('sale_order_term_and_condition.note') or False
        return note

    sale_order = fields.Many2many('res.config.settings', string="sale_order")
    notes = fields.Html(string='Term And Conditions', default=get_note)
    # um = HijriDate(1989, 1, 10, gr=True)

    hijiri_date = fields.Char(compute='get_date', readonly=True)

    date_new = fields.Char(compute='get_date', readonly=True)

    date_day = fields.Char(compute='get_date', readonly=True)

    @api.depends('order_line.pickup_date')
    def get_date(self):
        for rental in self.order_line:
            if rental.is_rental :
                to_date = rental.pickup_date.date()
        
        print("*************************")
        self.date_new = to_date
        war1 = convert.Gregorian.fromdate(to_date).to_hijri()
        self.hijiri_date = str(war1)

        if to_date.weekday() == 0:
            self.date_day = "الاثنين"
        elif to_date.weekday() == 1:
            self.date_day = "الثلاثاء"
        elif to_date.weekday() == 2:
            self.date_day = "الأربعاء"
        elif to_date.weekday() == 3:
            self.date_day = "الخميس"
        elif to_date.weekday() == 4:
            self.date_day = "الجمعة"
        if to_date.weekday() == 5:
            self.date_day = "السبت"
        if to_date.weekday() == 6:
            self.date_day = "الأحد"


class InvoiceText(models.Model):
    _inherit = "account.move"

    text_amount = fields.Char(string="Total In Words", required=False, compute="amount_to_words")

    @api.depends('amount_total')
    def amount_to_words(self):
        if self.company_id.text_amount_language_currency:
            self.text_amount = num2words(self.amount_total, to='currency',
                                         lang=self.company_id.text_amount_language_currency)
