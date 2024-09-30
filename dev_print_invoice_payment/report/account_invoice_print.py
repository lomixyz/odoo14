# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Devintelle Software Solutions (<http://devintelle.com>).
#
##############################################################################
from odoo import api, models
import json

class account_invoice_print(models.AbstractModel):
    _name = 'report.dev_print_invoice_payment.print_invoice_report_id'

    @api.model
    def get_paid_amount(self, obj):
        amount=0.0  
        payment = obj.invoice_payments_widget
        payment_ids = []
        if not payment == 'false':
            payment_dic = json.loads(payment) 
            payment_dic = payment_dic.get('content')
            for payment in payment_dic:
                if payment.get('amount'):
                    amount+=int(payment.get('amount'))
            
        return amount

    @api.model
    def get_paid_id(self, obj):
        amount=0.0  
        payment = obj.invoice_payments_widget
        payment_ids = []
        payment_dic = {}
        if not payment == 'false':
            payment_dic = json.loads(payment) 
            payment_dic = payment_dic.get('content')
        return payment_dic
        
        
    

    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'account.move',
            'docs': docs,
            'get_paid_amount': self.get_paid_amount,
            'get_paid_id':self.get_paid_id,

        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
