# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class HrPayslipStructure(models.Model):
    _inherit = 'hr.payroll.structure'
    
    @api.model
    def _get_parent(self):
        return False
    
    parent_id = fields.Many2one('hr.payroll.structure', string='Parent', default=_get_parent)
    input_line_type_ids = fields.Many2many('hr.payslip.input.type', string='Other Input Line')

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    
    company_id = fields.Many2one('res.company','Company',required=True, readonly=True,default=lambda self: self.env.user.company_id)
    
class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip', 'mail.thread']
    
    _order = 'id desc'
    
    input_line_ids = fields.One2many('hr.payslip.input', 'payslip_id', string='Payslip Inputs', readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    line_ids = fields.One2many('hr.payslip.line', 'slip_id', string='Payslip Lines', readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    
    state = fields.Selection(track_visibility='onchange')
    
    #===========================================================================
    # @api.multi
    # def action_payslip_done(self):
    #     return self.write({'state': 'done'})
    #===========================================================================
        
    def compute_sheet(self):
        res = super(HrPayslip, self).compute_sheet()
        for payslip in self:
            for l in payslip.line_ids:
                if l.code == 'NET':
                    l.write({'name': 'Net for '+ (payslip.employee_id.name)})
                     
                if l.total == 0:
                    l.unlink()
        return res
    
class HrPayslipRun(models.Model):
    _name = 'hr.payslip.run'
    _inherit = ['hr.payslip.run', 'mail.thread']
    
    _order = 'id desc'
    
    state = fields.Selection(track_visibility='onchange')
    