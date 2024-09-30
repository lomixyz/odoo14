# -*- coding: utf-8 -*-
#############################################################################
#                                                                           #
#    iTech Co.                                                              #
#                                                                           #
#    Copyright (C) 2020-iTech(<https://www.iTech.com.eg>).                  #
#                                                                           #
#############################################################################

from odoo.exceptions import UserError
from odoo import models, fields, api, _
from odoo.http import request
import qrcode, base64
from io import BytesIO

class QRCodeAddon(models.Model):
    _inherit = 'account.move'

    def create_qr_code(self, data):
        qr = qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=20, border=4, )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_img = base64.b64encode(temp.getvalue())
        return qr_img

    qr_code_image = fields.Binary("QR Code", compute='_generate_qr_code')

    def _generate_qr_code(self):
        invoice_info= ''
        lang = self.env.user.lang
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&",lang)
        if (lang.startswith('en')):
            invoice_info = 'Partner Name : %s  \n VAT Number : %s \n invoice Date : %s \n Amount Total : %d \n Amount Un TAX : %d \n Amount TAX : %d '% \
            (self.partner_id.name , self.company_id.vat ,self.invoice_date ,self.amount_total ,\
            self.amount_untaxed ,self.amount_tax)
        if(lang.startswith('ar')):
            invoice_info = '%s : اسم المورد \n %s : رقم التسجيل الضريبى \n تاريخ الفاتورة : %s \n اجمالي الفاتورة مع ضريبة القيمة المضافة : %d \n اجمالي الفاتورة بدون ضريبة القيمة المضافة : %d \n اجمالي ضريبة القيمة المضافة : %d'% \
            (self.partner_id.name , self.company_id.vat ,self.invoice_date ,self.amount_total ,\
            self.amount_untaxed ,self.amount_tax)
        self.qr_code_image = self.create_qr_code(invoice_info)

