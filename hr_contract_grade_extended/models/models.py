# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import except_orm, Warning, RedirectWarning, UserError, ValidationError

class Contract(models.Model):
    _inherit = 'hr.contract'
            
    wage = fields.Monetary(string='Gross', readonly=False, compute=False , required=False)
    
    @api.onchange('grade_id')
    def get_benifits(self):
        for rec in self:
            rec.wage = rec.grade_id.wage
            rec.basic_percentage = rec.grade_id.basic_percentage
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
                
    @api.onchange('basic','grade_line_id')
    def get_amount_perecentage(self):
        for rec in self:
            for line in rec.grade_line_id:
                if line.type == 'percentage':
                    line.amount = ((line.percentage)/100) * rec.basic
                else:
                    pass
    
    @api.depends('wage','basic_percentage')
    def get_basic(self):
        for rec in self:
            rec.basic = ( ( rec.basic_percentage/100 ) * rec.wage )
      
    
    @api.depends('basic_percentage','basic','grade_id','grade_line_id','grade_line_id.amount')
    def get_total_allowance(self):
        for rec in self:
            total = 0.0
            if rec.grade_id and rec.grade_line_id:
                for line in rec.grade_line_id:
                    # if line.type == 'fixed':
                    total += line.amount
                    # elif line.type == 'percentage':
                        # total += ((line.amount)/100) * rec.basic
            rec.total_allowance = total
                    
    total_allowance  = fields.Float(string='Total Allowance' , compute="get_total_allowance")
    grade_id = fields.Many2one('hr.grade.configuration', string="Grade", required=True, readony=True)
    grade_line_id = fields.One2many(comodel_name='hr.grade.line', inverse_name='contract_id', string='Benefits')
    basic = fields.Float(string='Basic Salary', compute="get_basic", store=True,)
    basic_percentage = fields.Float(string='Basic %')
    
    
class HRGradeConfiguration(models.Model):
    _inherit = 'hr.grade.configuration'
    
    @api.depends('wage','basic_percentage')
    def get_basic(self):
        for rec in self:
            rec.basic = ( ( rec.basic_percentage/100 ) * rec.wage )
    
    wage  = fields.Float(string='Gross')
    basic = fields.Float(string='Basic Salary', compute="get_basic", store=True,)
    basic_percentage = fields.Float(string='Basic %')