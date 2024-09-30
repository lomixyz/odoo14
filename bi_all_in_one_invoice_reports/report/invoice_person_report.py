from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import datetime


class ReportInvoiceWizard(models.AbstractModel):
    _name = 'report.bi_all_in_one_invoice_reports.invoice_person_template'
    _description = 'All in one Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name(
            'bi_all_in_one_invoice_reports.invoice_person_template')
        record = {
            'doc_ids': self.env['invoice.person.wizard'].search([('id', 'in', list(data["ids"]))]),
            'doc_model': report.model,
            'docs': self,
            'data': data,
            }
        return record
