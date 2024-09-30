# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json


class ReportInvoiceZakatAndTaxAuthority(models.AbstractModel):
    _name = 'report.qr_code_invoice_app.report_invoice_zakat_tax_authority'
    _description = 'Account report According To Zakat And Tax Authority'

    @api.model
    def get_paid_id(self, obj):
        amount = 0.0  
        payment = obj.invoice_payments_widget
        payment_ids = []
        payment_dic = {}
        if not payment == 'false':
            payment_dic = json.loads(payment) 
            payment_dic = payment_dic.get('content')
        return payment_dic
    
    @api.model
    def _get_report_values(self, docids, data=None):
        # with_context(lang=o.partner_id.lang)
        docs = self.env['account.move'].browse(docids)
        if not docs.company_id.vat:
            raise UserError(_('Please Set VAT Number In Company Profile'))
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': self.env['account.move'].browse(docids),
            'report_type': data.get('report_type') if data else '',
            'user_lang':self.env.user.lang,
            'get_paid_id':self.get_paid_id,
        }
