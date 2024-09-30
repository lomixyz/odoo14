# -*- coding: utf-8 -*-
import time
from odoo import models, api, fields
from odoo.exceptions import UserError


class HrLoanAcc(models.Model):
    _inherit = 'hr.loan'

    employee_account_id = fields.Many2one('account.account', string="Loan Account")
    treasury_account_id = fields.Many2one('account.account', string="Treasury Account")
    journal_id = fields.Many2one('account.journal', string="Journal")
    entry_count = fields.Integer(string="Entry Count", compute='compute_entery_count')
    move_id = fields.Many2one('account.move', string="Entry Journal", readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('hr_approve', 'HR Manager Approve'),
        ('finance_approve', 'Finance Manager Approve'),
        ('approve', 'Approved'),
        ('paid', 'Paid'),
        ('refuse', 'Refused'),
    ], string="State", default='draft', track_visibility='onchange', copy=False)

    def compute_entery_count(self):
        count = 0
        entry_count = self.env['account.move.line'].search_count([('loan_id', '=', self.id)])
        self.entry_count = entry_count

    def action_create_entries(self):
        """This create account move for request.
            """
        if not self.employee_account_id or not self.treasury_account_id or not self.journal_id:
            raise UserError("You must enter employee account & Treasury account and journal to create journal entries ")
        else:
            timenow = time.strftime('%Y-%m-%d')
            for loan in self:
                amount = loan.loan_amount
                loan_name = loan.employee_id.name
                reference = loan.name
                journal_id = loan.journal_id.id
                debit_account_id = loan.employee_account_id.id
                credit_account_id = loan.treasury_account_id.id

                Move = self.env['account.move']
                MoveLine = self.env['account.move.line'].with_context(check_move_validity=False)
                vals = {
                    'narration': loan_name,
                    'ref': reference,
                    'journal_id': journal_id,
                    'date': timenow,

                }
                move_id = Move.create(vals)

                debit_vals = {
                    'name': loan_name,
                    'account_id': debit_account_id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                    'loan_id': loan.id,
                    'move_id': move_id.id,
                }
                credit_vals = {
                    'name': loan_name,
                    'account_id': credit_account_id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                    'loan_id': loan.id,
                    'move_id': move_id.id,
                }

                MoveLine.create(debit_vals)
                MoveLine.create(credit_vals)

                self.write({'move_id': move_id.id})
                move_id.post()
            self.write({'state': 'paid'})
        return True

    def action_approve(self):
        for rec in self:
            finance_users = []
            finance_users = rec.env.ref('account.group_account_user').users
            for finance_user in finance_users:
                rec.activity_unlink(['hr_loan_base.mail_loan_request'])
                rec.activity_schedule('hr_loan_base.mail_loan_request', user_id=finance_user.id)
            rec.state = 'finance_approve'
        return

    def finance_action_approve(self):
        for rec in self:
            rec.state = 'approve'
            rec.activity_unlink(['hr_loan_base.mail_loan_request'])
        return True

    def finance_action_refuse(self):
        for rec in self:
            rec.activity_unlink(['hr_loan_base.mail_loan_request'])
            rec.state = 'refuse'
