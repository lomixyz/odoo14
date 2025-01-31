# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from werkzeug import url_encode

_logger = logging.getLogger(__name__)


class HrPayslipBatchwiseRegisterPaymentWizard(models.TransientModel):

    _name = "hr.payslip.batchwise.register.payment.wizard"
    _description = "Batch Wise Register Payment wizard"

    batch_id = fields.Many2one('hr.payslip.run','Batch Name', default= lambda self: self.get_default_batch())
    journal_id = fields.Many2one('account.journal', string='Payment Method', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True, required=True)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Type', required=True)
    amount = fields.Monetary(string='Payment Amount')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True)
    communication = fields.Char(string='Memo')
    hide_payment_method = fields.Boolean(compute='_compute_hide_payment_method',
        help="Technical field used to hide the payment method if the selected journal has only one available which is 'manual'")

    def get_default_batch(self):
        active_id = self.env.context.get('active_ids', []) or []
        record = self.env['hr.payslip.run'].browse(active_id)
        return record

    @api.depends('journal_id')
    def _compute_hide_payment_method(self):
        for record in self:
            if not record.journal_id:
                record.hide_payment_method = True
                return
            journal_payment_methods = record.journal_id.outbound_payment_method_ids
            record.hide_payment_method = len(journal_payment_methods) == 1 and journal_payment_methods[0].code == 'manual'

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            return {'domain': {'payment_method_id': [('payment_type', '=', 'outbound'), ('id', 'in', payment_methods.ids)]}}
        return {}

    def post_payment(self):
        self.ensure_one()
        payment_mode = self.company_id.payslip_payment_mode
        batch_id = self.batch_id

        move_id = batch_id.slip_ids.mapped('move_id')

        if self.amount > batch_id.remaining_amount:
            raise ValidationError(_("Amount must be less or equals to remaining amount."))

        if not move_id or not move_id.state == 'posted':
            raise ValidationError(_("Please make sure that the related journal entry is created and posted."))

        to_pay = batch_id.slip_ids.filtered(lambda p: p.state == 'done')

        if payment_mode == 'group':
            payment_values = {
                'payslip_run_id': batch_id.id,
                'partner_type': 'supplier',
                'payment_type': 'outbound',
                'partner_id': batch_id.company_id.partner_id.id,
                'journal_id': self.journal_id.id,
                'company_id': self.company_id.id,
                'payment_method_id': self.payment_method_id.id,
                'amount': self.amount,
                'currency_id': self.currency_id.id,
                'payment_date': self.payment_date,
                'communication': self.communication,
                'writeoff_label': 'Payslip Batch Payment'
            }

            # Create payment and post it
            payment = self.env['account.payment'].create(payment_values)
            payment.post()

            # Log the payment in the chatter
            body = (_(
                "A payment of %s %s with the reference <a href='/mail/view?%s'>%s</a> related to this batch %s has been made.") % (
                    payment.amount, payment.currency_id.symbol,
                    url_encode({'model': 'account.payment', 'res_id': payment.id}), payment.name, batch_id.name))
            batch_id.message_post(body=body)

            # Reconcile the payment and the move_id, i.e. lookup on the payable account move lines
            account_move_lines_to_reconcile = self.env['account.move.line']
            for line in payment.move_line_ids + move_id.line_ids:
                if line.account_id.internal_type == 'payable':
                    account_move_lines_to_reconcile |= line

            account_move_lines_to_reconcile.reconcile()

            to_pay.set_to_paid()

        else:
            for payslip in to_pay:

                payment_values = {
                    'payslip_run_id': batch_id.id,
                    'partner_type': 'supplier',
                    'payment_type': 'outbound',
                    'partner_id': payslip.employee_id.address_home_id.id,
                    'journal_id': self.journal_id.id,
                    'company_id': self.company_id.id,
                    'payment_method_id': self.payment_method_id.id,
                    'amount': payslip.net_amount,
                    'currency_id': self.currency_id.id,
                    'payment_date': self.payment_date,
                    'communication': self.communication,
                    'writeoff_label': 'Payslip Payment'
                }

                # Create payment and post it
                payment = self.env['account.payment'].create(payment_values)
                payment.post()
                # for move in payment.move_line_ids:
                #     move.name = +
                # Log the payment in the chatter
                body = (_("A payment of %s %s with the reference <a href='/mail/view?%s'>%s</a> related to your expense %s has been made.") % (payment.amount, payment.currency_id.symbol, url_encode({'model': 'account.payment', 'res_id': payment.id}), payment.name, payslip.name))
                payslip.message_post(body=body)

                # Reconcile the payment and the expense, i.e. lookup on the payable account move lines
                account_move_lines_to_reconcile = self.env['account.move.line']
                for line in payment.move_line_ids + payslip.move_id.line_ids:
                    if line.account_id.internal_type == 'payable':
                        account_move_lines_to_reconcile |= line
                account_move_lines_to_reconcile.reconcile()

                payslip.set_to_paid()

        return {'type': 'ir.actions.act_window_close'}