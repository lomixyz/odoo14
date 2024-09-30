# -*- coding: utf-8 -*-
import datetime
from openerp import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning, UserError
from dateutil import relativedelta
from datetime import datetime as dt
import odoo.addons.decimal_precision as dp
from datetime import datetime, timedelta


class HRGradeLine(models.Model):
    _name='hr.grade.line'
    _description = 'Grade Line'
    
    
    name  = fields.Char(string='Name' , required=True, )
    type  = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage','Percentage (Basic)'),
    ], string='Type', required=True, default='fixed')
    percentage = fields.Float(string='Percentage (%)')
    amount = fields.Float(string='Amount')
    code  = fields.Char(string='Salary Rule Code', required=True, )
    grade_id = fields.Many2one('hr.grade.configuration', string="Grade")
    contract_id  = fields.Many2one(comodel_name='hr.contract', string='Contract')
    benifit_id = fields.Many2one('hr.grade.benefits', string="Benifit")
    
class HRGradeConfiguration(models.Model):
    _name='hr.grade.configuration'
    _description = 'Grade'


    def get_benifits(self):
        for rec in self:
            # rec.grade_line_id.unlink()
            for line in self.env['hr.grade.benefits'].search([('id','not in', rec.grade_line_id.mapped('benifit_id').ids)]):
                self.env['hr.grade.line'].create({
                    'name': line.name,
                    'type': line.type,
                    'code': line.code,
                    'percentage': line.percentage,
                    'amount': line.amount,
                    'grade_id': rec.id,
                    'benifit_id': line.id
                })
            rec.get_amount_perecentage()


    @api.onchange('basic','grade_line_id')
    def get_amount_perecentage(self):
        for rec in self:
            for line in rec.grade_line_id:
                if line.type == 'percentage':
                    line.amount = ((line.percentage)/100) * rec.basic
                else:
                    pass
        

    @api.constrains('sequence')
    def _check_sequence(self):
        ids = self.env['hr.grade.configuration'].search([('id','!=',self.id),('sequence','=',self.sequence)])
        if len(ids)>0:
            raise UserError(_('Sequence Should Be Unique!'))

    name = fields.Char(string="Grade",required=True)
    sequence  = fields.Integer(string='Sequence',required=True , copy=False)
    grade_line_id = fields.One2many(comodel_name='hr.grade.line', inverse_name='grade_id', string='Benefits')
    basic = fields.Float(string='Basic')
    job_ids  = fields.Many2many(comodel_name='hr.job', string='Job Positions')
    
    

class Contract(models.Model):
    _inherit = 'hr.contract'

    basic = fields.Float(string='Basic Salary')
    emp_code = fields.Char(string='Employee Code', compute='_compute_emp_code',store=True)

    total_allowance = fields.Float(string='Total Allowance', compute="get_total_allowance")
    grade_id = fields.Many2one('hr.grade.configuration', string="Grade", required=True, readony=True)
    grade_line_id = fields.One2many(comodel_name='hr.grade.line', inverse_name='contract_id', string='Old Benefits')
    wage = fields.Monetary(string='Gross', compute="get_gross", store=True, required=False)
    

    @api.depends('employee_id')
    def _compute_emp_code(self):
        for rec in self:
            rec.emp_code = rec.employee_id.emp_code

    @api.constrains('grade_id.job_ids','grade_id','job_id')
    def _check_job_positions(self):
        if self.grade_id and self.grade_id.job_ids:
            if self.job_id not in self.grade_id.job_ids:
                raise UserError(_("Employee Job Position is not Allowed To Take This Grade"))

    @api.depends('basic','total_allowance')
    def get_gross(self):
        for rec in self:
            rec.wage =  rec.total_allowance + rec.basic
      
            
    @api.onchange('grade_id')
    def get_benifits(self):
        for rec in self:
            rec.basic = rec.grade_id.basic
            # rec.basic_percentage = rec.grade_id.basic_percentage
            lines = [(5, 0, 0)]
            for line in self.grade_id.grade_line_id:
                vals = {
                    'name': line.name,
                    'type': line.type,
                    'code': line.code,
                    'percentage': line.percentage,
                    'amount': line.amount,
                    'contract_id':rec.id
                }
                lines.append((0, 0, vals))
            rec.grade_line_id = lines

    @api.onchange('basic', 'grade_line_id')
    def get_amount_perecentage(self):
        for rec in self:
            for line in rec.grade_line_id:
                if line.type == 'percentage':
                    line.amount = ((line.percentage) / 100) * rec.basic
                else:
                    pass
    
    
    @api.depends('grade_id','grade_line_id','grade_line_id.amount')
    def get_total_allowance(self):
        for rec in self:
            total = 0.0
            if rec.grade_id and rec.grade_line_id:
                for line in rec.grade_line_id:
                    # if line.type == 'fixed':
                    total += line.amount
                    # elif line.type == 'percentage':
                    #     total += ((line.amount)/100) * rec.basic
            rec.total_allowance = total 
                    




    
            
        