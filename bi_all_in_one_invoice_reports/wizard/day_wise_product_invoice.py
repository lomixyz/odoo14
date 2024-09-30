# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
import xlwt
import base64
import pytz, tempfile
from io import BytesIO
from odoo import models, fields, api, _
from odoo.tools.misc import xlwt
from datetime import date, datetime, timedelta
from openpyxl import Workbook
from datetime import datetime
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp
import calendar


class DayWiseInvoiceReport(models.TransientModel):
    _name = 'invoice.report.wizard'
    _description = 'day wise invoice report'

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    company_ids = fields.Many2many('res.company', string='Companies')
    file_name = fields.Char('Excel File', readonly=True)
    data = fields.Binary(string="File")

    def create_report(self):
        start_date = self.start_date
        end_date = self.end_date
        if start_date > end_date:
            raise ValidationError(_("Please enter valid date range"))
        companies = self.company_ids.ids
        if len(companies) > 0:
            selected_companies = companies
        else:
            selected_companies = self.env.user.company_ids.ids
        account_move = self.env['account.move'].search([('invoice_date', '>=', start_date),
                                                    ('invoice_date', '<=', end_date),
                                                    ('company_id', 'in', selected_companies),
                                                    ])
        

        account_move = account_move.filtered(lambda s: s.state == "posted")
        data = {}
        for move in account_move:
            day = calendar.weekday(move.invoice_date.year, move.invoice_date.month,
                                   move.invoice_date.day)
            for line in move.invoice_line_ids:
                if line.product_id.name in data:
                    data[line.product_id.name][day] += int(line.quantity)
                    data[line.product_id.name][7] += int(line.quantity)
                else:
                    data[line.product_id.name] = [0, 0, 0, 0, 0, 0, 0, 0]
                    data[line.product_id.name][day] = int(line.quantity)
                    data[line.product_id.name][7] = int(line.quantity)

        day_total = [0, 0, 0, 0, 0, 0, 0]
        for i in range(0, 7):
            for product in data.keys():
                day_total[i] += data[product][i]

        data_all = {'data': [data, day_total, [start_date, end_date],self.company_record()], }
        record = self.env.ref('bi_all_in_one_invoice_reports.action_day_wise_invoice_report').report_action(self, data=data_all)
        return record

    def company_record(self):
        comp_name = []
        for comp in self.company_ids:
            comp_name.append(comp.name)
        listtostr = ', '.join([str(elem) for elem in comp_name])
        return listtostr

    def create_xls_report(self):
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Day Wise Invoice Report')
        worksheet.col(0).width = 8000
        style_header = xlwt.easyxf(
            "font:height 400; font: name Liberation Sans, bold on,color black; align: vert centre, horiz center;pattern: pattern solid, pattern_fore_colour gray25;")
        style_line_heading = xlwt.easyxf(
            "font: name Liberation Sans, bold on; pattern: pattern solid, pattern_fore_colour gray25;")
        style_bold = xlwt.easyxf(
            "font: name Liberation Sans, bold on; align: horiz right;")
        worksheet.write_merge(0, 1, 2, 8, 'Invoice Order - Product Sold DayWise', style=style_header)
        worksheet.write_merge(2, 2, 0, 8, 'Companies: '+str(self.company_record()), style=xlwt.easyxf(
            "font: name Liberation Sans, bold on; align: horiz center;"))
        worksheet.col(2).width = 5600
        row = 4
        list1 = ['Product Name', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                 'Saturday', 'Sunday', 'Total', 'Start Date', 'End Date']
        worksheet.col(0).width = 5000
        worksheet.write(row, 0, 'Start Date: '+str(self.start_date.strftime('%d-%m-%Y')), style=xlwt.easyxf(
            "font: name Liberation Sans, bold on;"))
        worksheet.col(6).width = 5000
        worksheet.write(row, 8, 'End Date: '+str(
            self.end_date.strftime('%d-%m-%Y')), style=xlwt.easyxf(
            "font: name Liberation Sans, bold on; align: horiz left;"))
        row += 2
        worksheet.col(0).width = 5000
        worksheet.write(row, 0, list1[0], style=style_line_heading)
        worksheet.col(1).width = 5000
        worksheet.write(row, 1, list1[1], style=style_line_heading)
        worksheet.col(2).width = 5000
        worksheet.write(row, 2, list1[2], style=style_line_heading)
        worksheet.col(3).width = 5000
        worksheet.write(row, 3, list1[3], style=style_line_heading)
        worksheet.col(4).width = 5000
        worksheet.write(row, 4, list1[4], style=style_line_heading)
        worksheet.col(5).width = 5000
        worksheet.write(row, 5, list1[5], style=style_line_heading)
        worksheet.col(6).width = 5000
        worksheet.write(row, 6, list1[6], style=style_line_heading)
        worksheet.col(7).width = 5000
        worksheet.write(row, 7, list1[7], style=style_line_heading)
        worksheet.col(8).width = 5000
        worksheet.write(row, 8, list1[8], style=style_line_heading)
        row = row + 1
        data = self.create_report()['data']
        for i in data.values():
            move = i[0]
            total = [0, 0, 0, 0, 0, 0, 0, 0]
            for product in move:
                worksheet.write(row, 0, product)
                worksheet.write(row, 1, move[product][0])
                total[0] += move[product][0]
                worksheet.write(row, 2, move[product][1])
                total[1] += move[product][1]
                worksheet.write(row, 3, move[product][2])
                total[2] += move[product][2]
                worksheet.write(row, 4, move[product][3])
                total[3] += move[product][3]
                worksheet.write(row, 5, move[product][4])
                total[4] += move[product][4]
                worksheet.write(row, 6, move[product][5])
                total[5] += move[product][5]
                worksheet.write(row, 7, move[product][6])
                total[6] += move[product][6]
                worksheet.write(row, 8, move[product][7])
                total[7] += move[product][7]
                row = row + 1
            row += 1
            worksheet.write(row, 0, 'Total', style=xlwt.easyxf(
                "font: name Liberation Sans, bold on; align: horiz center;"))
            worksheet.write(row, 1, total[0], style=style_bold)
            worksheet.write(row, 2, total[1], style=style_bold)
            worksheet.write(row, 3, total[2], style=style_bold)
            worksheet.write(row, 4, total[3], style=style_bold)
            worksheet.write(row, 5, total[4], style=style_bold)
            worksheet.write(row, 6, total[5], style=style_bold)
            worksheet.write(row, 7, total[6], style=style_bold)
            worksheet.write(row, 8, total[7], style=style_bold)
        tz = pytz.timezone('Asia/Kolkata')
        file_data = BytesIO()
        workbook.save(file_data)
        self.write({
            'data': base64.encodestring(file_data.getvalue()),
            'file_name': 'DayWise Invoice Report.xls'
        })
        action = {
            'type': 'ir.actions.act_url',
            'name': 'contract',
            'url': '/web/content/invoice.report.wizard/%s/data/DayWise Invoice Report.xls?download=true' % (self.id),
            'target': 'self',
        }
        return action
