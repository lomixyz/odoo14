from datetime import datetime
from odoo.tools import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT

from odoo import models, fields, api


class custodyViewReportWizard(models.TransientModel):
    _name = 'custom.custody.report.wizard'
    _description = "company Report"

    date_start = fields.Date(string="Start Date", required=True, default=fields.Date.today)
    date_end = fields.Date(string="End Date", required=True, default=fields.Date.today)
    employee_id = fields.Many2one('hr.employee')
    type = fields.Selection([
        ('all', 'All Employee'),
        ('specific', 'Employee')], default='all')

    def get_report(self):
        active_ids = self.env.context.get('active_ids', [])
        data = {
            'ids': active_ids,
            'model': 'account.custody',
            'form': self.read()[0]
        }

        return self.env.ref('account_custody.action_custom_report_custody').report_action(self, data=data)


class ReportCompanyView(models.AbstractModel):
    _name = 'report.account_custody.report_custody_view'

    @api.model
    def _get_report_values(self, docids, data=None):

        if not data.get('form'):
            raise UserError("Form content is missing, this report cannot be printed.")

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        type = data['form']['type']
        date_start_obj = datetime.strptime(date_start, DATE_FORMAT)
        date_end_obj = datetime.strptime(date_end, DATE_FORMAT)

        docs = []
        if type == 'all':
            #

            custody = self.env['account.custody'].search(
                ['&', ('date', '>=', date_start_obj), ('date', '<=', date_end_obj)])

            for cus in custody:
                amount_paid = sum(cus.line_ids.mapped('amount'))
                total = cus.amount - amount_paid

                docs.append({
                    'Name': cus.employee_id.name,
                    'Custody': cus.name,
                    'Description': cus.description,
                    'Amount': cus.amount,
                    'Entry Number': cus.move_id.name,
                    'Date': cus.date,
                    'Line Amount': amount_paid,
                    'Remaining': total,

                })

        else:
            employee_id = data['form']['employee_id'][0]

            custody = self.env['account.custody'].search(
                ['&', ('date', '>=', date_start_obj),
                 ('date', '<=', date_end_obj), ('employee_id', '=', employee_id)])
            for cus in custody:
                amount_paid = sum(cus.line_ids.mapped('amount'))
                total = cus.amount - amount_paid

                docs.append({
                    'Name': cus.employee_id.name,
                    'Custody': cus.name,
                    'Description': cus.description,
                    'Amount': cus.amount,
                    'Entry Number': cus.move_id.name,
                    'Date': cus.date,
                    'Line Amount': amount_paid,
                    'Remaining': total,

                })

        return {
            'doc_ids': 'docids',
            'doc_model': 'account.custody',
            'docs': docs,
            'data': data,
        }
