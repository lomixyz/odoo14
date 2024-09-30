# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class Payslip(models.Model):
    _name = "hr.payslip"
    _inherit = ['hr.payslip','mail.thread']

    state = fields.Selection(selection_add=[('paid', 'Paid')])
    net_amount = fields.Float(string='Net Amount', compute="_get_net_amount", store=True)
    payment_id = fields.Many2one('account.payment', string="Payment", readonly=True)

    @api.depends('line_ids')
    def _get_net_amount(self):
        for record in self:
            record.net_amount = record.line_ids.filtered(lambda l: l.code == 'NET').amount

    def set_to_paid(self):
        for payslip in self:
            payslip.state = 'paid'
            if payslip.payslip_run_id:
                if all(payslip.state == 'paid' for payslip in payslip.payslip_run_id.slip_ids):
                    payslip.payslip_run_id.write({'state': 'paid'})

    def action_payment(self):
        if not all(payslip.state == 'done' for payslip in self):
            raise UserError(_('All payslips must be in done stage.'))

        return {
            'name': _('Register Payment'),
            'res_model': 'hr.payslip.register.payment.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref(
                'app_hr_payroll_payment.hr_payslip_sheet_register_payment_view_form').id,
            'context': self.env.context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }


class PayslipRun(models.Model):
    _name = "hr.payslip.run"
    _inherit = ['hr.payslip.run', 'mail.thread', 'mail.activity.mixin']

    state = fields.Selection(selection_add=[('paid', 'Paid')])
    net_amount = fields.Float(string="Total Amount", compute="compute_totals", store=True)
    remaining_amount = fields.Float(string="To Pay Amount", compute="compute_totals", store=True)
    payment_ids = fields.One2many('account.payment', 'payslip_run_id', string='Payments')
    payment_count = fields.Integer(compute='get_payment_count')

    @api.depends('slip_ids.state')
    def compute_totals(self):
        for record in self:
            net_amount = sum(slip.net_amount for slip in record.slip_ids)
            remaining_amount = sum(slip.net_amount for slip in record.slip_ids.filtered(lambda p: p.state == 'done'))
            record.update({
                'net_amount': net_amount,
                'remaining_amount': remaining_amount
            })

    def get_payment_count(self):
        for record in self:
            record.payment_count = len(record.payment_ids)

    def action_view_payments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payments',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'domain': [('payslip_run_id', '=', self.id)],
            'context': "{'create':False}"
        }
