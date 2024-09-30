# -*- coding: utf-8 -*-

from odoo import models, fields, api


class RecieptVoucher(models.TransientModel):
    _name = 'reciept.voucher'
 
    amount = fields.Float('Amount',required=True)
    date = fields.Date('Date',required=True)
    note = fields.Char('Notes',required=True)
    
    def create_payment(self):
        loan_id = self.env['hr.loan'].browse(self._context.get('active_id',False))
        payment_vals = {'communication':self.note,
                        'amount':self.amount,
                        'payment_date':self.date,
                        'payment_type':'inbound',
                        'loan_id':loan_id.id,
                        'state':'draft',
                        'payment_method_id':1,
                        'journal_id': loan_id.payment_method.id,
                        'partner_type':'customer'}
        
        if loan_id.company_id.reference_employee_in_journal_entries and not loan_id.employee_id.user_id:
            raise UserError(_("Please make sure the employee profile is linked it's user!"))
        elif loan_id.company_id.reference_employee_in_journal_entries:
            payment_vals.update({'partner_id':loan_id.employee_id.user_id.partner_id.id,
                                 })
        payment_id = self.env['account.payment'].create(payment_vals)
    
