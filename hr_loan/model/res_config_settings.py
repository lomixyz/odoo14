# -*- coding: utf-8 -*-

from odoo import fields, models,api,_


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    loan_account_type = fields.Selection([('once','One Account For All Employees'),
                                          ('multiple','Account Per Employee')], string='Accounting Policy', related='company_id.loan_account_type', readonly=False)
    
    loan_account_id = fields.Many2one('account.account','Loan Account', related='company_id.loan_account_id', readonly=False)
    reference_employee_in_journal_entries = fields.Boolean(string="Reference Employee In Journal Entries",related='company_id.reference_employee_in_journal_entries',default=True, readonly=True)
    loan_user_notify = fields.Many2many('res.users',string='Users To Notify',related='company_id.loan_user_notify', readonly=False)
    
    @api.onchange('loan_account_type')
    def change_accounting_poilicy(self):
        res = {}
        if self.env['hr.loan'].search([('state','=','approved')]):
            res = {'warning': {
                'title': _('Warning'),
                'message': _('If you changed Loan Accounting Policy, This change may lead to unwanted results.')
                }}
            return res

    
class Company(models.Model):
    _inherit = 'res.company'
    
    loan_account_type = fields.Selection([('once','One Account For All Employees'),
                                          ('multiple','Account Per Employee')], string='Accounting Policy')
    
    loan_account_id = fields.Many2one('account.account','Loan Account')
    reference_employee_in_journal_entries = fields.Boolean(string="Reference Employee In Journal Entries", default=True)
    loan_user_notify = fields.Many2many('res.users',string='Users To Notify')