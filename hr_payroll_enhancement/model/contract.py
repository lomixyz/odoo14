# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class HrContract(models.Model):
    _inherit = 'hr.contract'
    
    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure', company_dependent=True)
    journal_id = fields.Many2one('account.journal', 'Salary Journal', company_dependent=True)