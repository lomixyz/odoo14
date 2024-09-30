from odoo import models, fields, api


class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    total_amount_commission = fields.Float(string="Total Commission Amount", compute='compute_total_commission')

    @api.depends('employee_id', 'date_from', 'date_to')
    def compute_total_commission(self):
        for rec in self:
            total = 0.00
            commission_ids = self.env['freight.commission'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('date', '>=', rec.date_from),
                ('date', '<=', rec.date_to),
            ])
            for com in commission_ids:
                total += com.amount
            rec.total_amount_commission = total
