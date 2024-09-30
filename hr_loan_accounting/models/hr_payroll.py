from odoo import models, fields, api, tools, _
from odoo.exceptions import except_orm, Warning, RedirectWarning, UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.osv import osv


class hr_payslip(models.Model):
   _inherit = 'hr.payslip'


   def get_loan(self):
      for rec in self:
         array = []
         loan_ids = self.env['hr.loan.line'].search([
               ('employee_id', '=', rec.employee_id.id),
               ('paid', '=', False), ('active', '=', True),
               ('state', '=', 'paid'),
               ('paid_date', '>=', rec.date_from),
               ('paid_date', '<=', rec.date_to),
         ])
         for loan in loan_ids:
               array.append(loan.id)
         rec.loan_ids = array
         return array