# -*- coding: utf-8 -*-
import base64
from io import BytesIO

import qrcode
from num2words import num2words

from odoo import models, fields, api, _
from odoo.exceptions import UserError


# class custom_invoice(models.Model):
#     _name = 'custom_invoice.custom_invoice'


class InvoiceText(models.Model):
    _inherit = "account.move"

    text_amount = fields.Char(string="Total In Words", required=False, compute="amount_to_words")

    qr_image = fields.Binary("QR Code", compute='_generate_qr_code')

    def _generate_qr_code(self):
        if self.move_type in ['out_invoice', 'in_refund']:
            partner_name = self.company_id.partner_id.name
        if self.move_type in ['in_invoice', 'out_refund']:
            partner_name = self.partner_id.name
        partner_name = str(_('اسم المورد: \t \t ' + partner_name))
        if self.move_type in ['out_invoice', 'in_refund']:
            if not self.company_id.partner_id.vat:
                raise UserError(_('Please define the Company Tax ID'))
            else:
                partner_vat = self.company_id.partner_id.vat
        if self.move_type in ['in_invoice', 'out_refund']:
            if not self.partner_id.vat:
                raise UserError(_('Please define the Partner Tax ID'))
            else:
                partner_vat = self.partner_id.vat
        partner_vat = str(_('رقم تسجيل ضريبة: \t \t ' + partner_vat))

        currency_total = ''.join([self.currency_id.name, str(self.amount_total)])
        total = str(_('إجمالي الفاتورة:  \t \t ' + currency_total))
        currency_tax = ''.join([self.currency_id.name, str(self.amount_tax)])
        tax = str(_('إجمالي ضريبة القيمة المضافة:  \t \t ' + currency_tax))
        date_invoice = self.invoice_date.strftime("%Y/%m/%d, %H:%M:%S")
        date = str(_('الطابع الزمني للفاتورة:  \t \t ' + date_invoice))
        lf = '\n\n'
        ibanqr = lf.join([partner_name, partner_vat, date, total, tax])
        print('////////////////////////////////', ibanqr)
        self.qr_image = generate_qr_code(ibanqr)

        @api.depends('amount_total')
        def amount_to_words(self):
            if self.company_id.text_amount_language_currency:
                self.text_amount = num2words(self.amount_total, to='currency',
                                             lang=self.company_id.text_amount_language_currency)


def generate_qr_code(value):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=20,
        border=4,
    )
    qr.add_data(value)
    qr.make(fit=True)
    img = qr.make_image()
    temp = BytesIO()
    img.save(temp, format="PNG")
    qr_img = base64.b64encode(temp.getvalue())
    return qr_img


class registry(models.TransientModel):
    _inherit = 'base.document.layout'

    company_registry = fields.Char(related='company_id.company_registry', readonly=True)


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    iban_num = fields.Char('IBAN Number')
