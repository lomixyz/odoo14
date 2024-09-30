# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
import xlwt
import base64
import pytz, tempfile
import io
from io import StringIO
from io import BytesIO
from functools import reduce
from odoo import models, fields, api, _
from odoo.tools.misc import xlwt
from datetime import date, datetime, timedelta
import json
from odoo.exceptions import ValidationError
from datetime import datetime


class InvoiceDetail(models.TransientModel):
    _name = 'invoice.detail.wizard'
    _description = 'All report'

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    select_state = fields.Selection([
        ('all', 'All'),
        ('posted', 'Posted'),
    ], string='Status', default='all')
    invoices_channel_ids = fields.Many2many('crm.team', string='Sales Channel')
    company_ids = fields.Many2many('res.company', string='Companies')
    file_name = fields.Char('Excel File', readonly=True)
    data = fields.Binary(string="File")

    def generate_pdf_report(self):
        start_date = self.start_date
        end_date = self.end_date
        if end_date < start_date:
            raise ValidationError('Enter End Date greater then Start Date')
        companies = self.company_ids.ids
        if len(companies) > 0:
            selected_companies = companies
        else:
            selected_companies = self.env.user.company_ids.ids
        channel = self.invoices_channel_ids.ids
        if len(channel) > 0:
            selected_channel = channel
        else:
            channel_all = self.env['crm.team'].search([]).ids
            selected_channel = channel_all
        final_data = {}
        state = []
        if self.select_state == 'all':
            state.extend(['draft', 'posted', 'cancel'])
        elif self.select_state == 'posted':
            state.extend(['posted'])
        elif self.select_state == False:
            state.extend(['draft', 'posted', 'cancel'])
        status = ('state', 'in', state)
        invoice_ids = self.env['account.move'].search([('invoice_date', '>=', start_date),
                                                  ('invoice_date', '<=', end_date),
                                                  ('company_id', 'in', selected_companies),
                                                  ('team_id', 'in', selected_channel), status
                                                  ])
        count_total = 0
        list1 = []
        total_payment = {'Bank': 0, 'Cash': 0}
        all_tax = {}
        for product in invoice_ids:
            invoice_payments = self.env['account.move'].search(
                [('id', 'in', product.line_ids.ids)])
            for line in product.invoice_line_ids:
                list1.append([line.product_id.name, line.quantity, line.price_unit])
                count_total += line.quantity * line.price_unit

                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.tax_ids.compute_all(price, line.move_id.currency_id,
                                                line.quantity, product=line.product_id,
                                                partner=line.move_id.partner_shipping_id)
            

                for tax in taxes.get('taxes', []):
                    if tax.get('name') not in all_tax:
                        all_tax.update({tax.get('name'): tax.get('amount', 0)})
                    else:
                        all_tax[tax.get('name')] += tax.get('amount', 0)

            
                for invoice in invoice_ids:
                    if invoice.invoice_payments_widget != 'false':
                        bank_amount = 0
                        cash_amount = 0
                        res = json.loads(invoice.invoice_payments_widget)
                    
                        for i in res['content']:
                            if i['journal_name'] == 'Bank':
                                bank_amount += i['amount']
                            if i['journal_name'] == 'Cash':
                                cash_amount += i['amount']
                        total_payment['Bank'] += bank_amount
                        total_payment['Cash'] += cash_amount


        if self.select_state == False:
            final_data.update({'date': [self.start_date, self.end_date, self.company_record(),
                                        self.select_state, self.channel_record()],
                               'invoice_data': list1, 'payments': total_payment, 'taxes': all_tax})
        else:
            final_data.update({'date': [self.start_date, self.end_date, self.company_record(),
                                        self.select_state.capitalize(), self.channel_record()],
                               'invoice_data': list1, 'payments': total_payment, 'taxes': all_tax})
         
        return self.env.ref(
            'bi_all_in_one_invoice_reports.action_invoice_details_report').report_action(self,
                                                                                   data=final_data)

    def company_record(self):
        comp_name = []
        for comp in self.company_ids:
            comp_name.append(comp.name)
        listtostr = ', '.join([str(elem) for elem in comp_name])
        return listtostr

    def channel_record(self):
        channel_name = []
        for channel in self.invoices_channel_ids:
            channel_name.append(channel.name)
        listtostr = ', '.join([str(elem) for elem in channel_name])
        return listtostr

    def generate_xls_report(self):
        workbook = xlwt.Workbook()
        stylePC = xlwt.XFStyle()
        worksheet = workbook.add_sheet('Sale Detail Report')
        bold = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour gray25;")
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        stylePC.alignment = alignment
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        alignment_num = xlwt.Alignment()
        alignment_num.horz = xlwt.Alignment.HORZ_RIGHT
        horz_style = xlwt.XFStyle()
        horz_style.alignment = alignment_num
        align_num = xlwt.Alignment()
        align_num.horz = xlwt.Alignment.HORZ_RIGHT
        horz_style_pc = xlwt.XFStyle
        horz_style_pc.alignment = alignment_num
        style1 = horz_style
        font = xlwt.Font()
        font1 = xlwt.Font()
        borders = xlwt.Borders()
        borders.bottom = xlwt.Borders.THIN
        font.bold = True
        font1.bold = True
        font.height = 400
        stylePC.font = font
        style1.font = font1
        stylePC.alignment = alignment
        pattern = xlwt.Pattern()
        pattern1 = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern1.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour = xlwt.Style.colour_map['gray25']
        pattern1.pattern_fore_colour = xlwt.Style.colour_map['gray25']
        stylePC.pattern = pattern
        style1.pattern = pattern
        style_header = xlwt.easyxf(
            "font:height 300; font: name Liberation Sans, bold on,color black; align: vert centre, horiz center;pattern: pattern solid, pattern_fore_colour gray25;")
        style_line_heading = xlwt.easyxf(
            "font: name Liberation Sans, bold on;align: horiz centre; pattern: pattern solid, pattern_fore_colour gray25;")
        style_line_heading_left = xlwt.easyxf(
            "font: name Liberation Sans, bold on;align: horiz left; pattern: pattern solid, pattern_fore_colour gray25;")

        worksheet.write_merge(0, 1, 0, 2, 'Sale Detail Report', style=stylePC)
        worksheet.col(2).width = 5600
        worksheet.write_merge(2, 2, 0, 2, 'Companies: ' + str(self.company_record()), style=xlwt.easyxf(
            "font: name Liberation Sans, bold on; align: horiz center;"))
        worksheet.write(3, 0, 'Start Date: ' + str(self.start_date.strftime('%d-%m-%Y')),
                        style=xlwt.easyxf(
                            "font: name Liberation Sans, bold on;"))
        worksheet.write(3, 2, 'End Date: ' + str(
            self.end_date.strftime('%d-%m-%Y')), style=xlwt.easyxf(
            "font: name Liberation Sans, bold on; align: horiz left;"))
        if self.select_state == False:
            worksheet.write(4, 0, 'Status: ', style=xlwt.easyxf(
                "font: name Liberation Sans, bold on;"))
        else:
            worksheet.write(4, 0, 'Status: ' + str(self.select_state).capitalize(), style=xlwt.easyxf(
                "font: name Liberation Sans, bold on;"))
        worksheet.write(4, 2, 'Sales Channel: ' + str(self.channel_record()), style=xlwt.easyxf(
            "font: name Liberation Sans, bold on; align: horiz left;"))

        row = 7
        worksheet.write_merge(6, 6, 0, 2, 'Products', style=style_line_heading)
        list1 = ['Product', 'Quantity', 'Price Unit']
        worksheet.col(0).width = 5000
        worksheet.write(row, 0, list1[0], style=style_line_heading_left)
        worksheet.col(1).width = 5000
        worksheet.write(row, 1, list1[1], style1)
        worksheet.col(2).width = 5000
        worksheet.write(row, 2, list1[2], style1)

        row += 1
        invoice_records = self.generate_pdf_report()
        if invoice_records['context'].get('report_action')==None:
            invoice_datas = invoice_records['data']['invoice_data']
        else:
            invoice_datas = invoice_records['context']['report_action']['data']['invoice_data']
        count_total = 0
        for product in invoice_datas:
            worksheet.write(row, 0, product[0])
            worksheet.write(row, 1, product[1])
            worksheet.write(row, 2, product[2])
            count_total += product[1] * product[2]
            row = row + 1
        row += 1
        list2 = ['Name', 'Total']
        worksheet.write_merge(row, row, 0, 2, 'Payments', style=style_line_heading)
        row += 1
        worksheet.col(0).width = 5000
        worksheet.write(row, 0, list2[0], style=style_line_heading_left)
        worksheet.col(1).width = 5000
        worksheet.write(row, 1, '', style1)
        worksheet.col(2).width = 5000
        worksheet.write(row, 2, list2[1], style1)
        row += 1
        if invoice_records['context'].get('report_action')==None:
            payment_record = invoice_records['data']['payments']
        else:
            payment_record = invoice_records['context']['report_action']['data']['payments']
        for pay in payment_record.items():
            worksheet.write(row, 0, pay[0])
            worksheet.write(row, 2, pay[1])
            row = row + 1
        row += 1
        worksheet.write_merge(row, row, 0, 2, 'Taxes', style=style_line_heading)
        row += 1
        worksheet.col(0).width = 5000
        worksheet.write(row, 0, list2[0], style=style_line_heading_left)
        worksheet.col(1).width = 5000
        worksheet.write(row, 1, '', style1)
        worksheet.col(2).width = 5000
        worksheet.write(row, 2, list2[1], style1)
        row += 1
        if invoice_records['context'].get('report_action')==None:
            tax_data = invoice_records['data']['taxes']
        else:
            tax_data = invoice_records['context']['report_action']['data']['taxes']
        for data in tax_data.items():
            worksheet.write(row, 0, data[0])
            worksheet.write(row, 2, data[1])
            row = row + 1
        row += 2
        file_data = BytesIO()
        workbook.save(file_data)
        self.write({
            'data': base64.encodestring(file_data.getvalue()),
            'file_name': 'Invoice Details Report.xls'
        })
        action = {
            'type': 'ir.actions.act_url',
            'name': 'contract',
            'url': '/web/content/invoice.detail.wizard/%s/data/Invoice Details Report.xls?download=true' % (
                self.id),
            'target': 'self',
        }
        return action
