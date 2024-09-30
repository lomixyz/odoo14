# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
import xlwt
import base64
import pytz, tempfile
from io import BytesIO
from odoo import models, fields, api, _
from odoo.tools.misc import xlwt
from datetime import date, datetime, timedelta
from datetime import datetime
from odoo.exceptions import ValidationError


class InvoicePerson(models.TransientModel):
    _name = 'invoice.person.wizard'
    _description = 'All report'

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    select_state = fields.Selection([
        ('all', 'All'),
        ('draft', 'Draft'),
        ('posted', 'Posted'),
    ], string='Status', default='all')
    user_id = fields.Many2one('res.users', string='User id', default=lambda self: self.env.user)
    account_move = fields.Many2many('account.move')
    company_ids = fields.Many2many('res.company', string='Companies')
    user_ids = fields.Many2many('res.users', string='User')
    file_name = fields.Char('Excel File', readonly=True)
    data = fields.Binary(string="File")

    def invoice_record_data(self):
        companies = self.company_ids.ids
        if len(companies) > 0:
            selected_companies = companies
        else:
            selected_companies = self.env.user.company_ids.ids
        data_all = {}
        list1 = []
        if self.select_state == 'all':
            list1.extend(['draft', 'posted', 'cancel'])
        elif self.select_state == 'draft':
            list1.extend(['draft'])
        elif self.select_state == 'posted':
            list1.extend(['posted'])
        elif self.select_state == False:
            list1.extend(['draft', 'posted', 'cancel'])
        status = ('state', 'in', list1)
        if len(self.user_ids.ids) == 0:
            self.user_ids = self.user_id
        for user in self.user_ids:

            account_move = self.env['account.move'].search([('invoice_date', '>=', self.start_date),
                                                         ('invoice_date', '<=', self.end_date),
                                                         ('company_id', 'in', selected_companies),
                                                         ('user_id', '=', user.id),('move_type', '=', 'out_invoice'), status])
            list2 = []
            total = [0.0, 0.0, 0.0, 0.0]
            for move in account_move.filtered(lambda x : x.invoice_user_id == user):
                pyt_list = []
                invoice = move
                invoice_due = 0
                invoice_total = 0
                paid_amount = 0
                for count in invoice:
                    invoice_total += count.amount_total
                    invoice_due += count.amount_residual
                    paid_amount += (count.amount_total-count.amount_residual)
                list2.append(
                    [move.name, str(move.invoice_date.strftime('%d/%m/%Y')), move.partner_id.name, move.amount_total,
                    invoice_total, invoice_due,invoice_total-invoice_due])
            for total_count in list2:
                total[0] += total_count[3]
                total[1] += total_count[4]
                total[2] += total_count[5]
                total[3] += total_count[6]
            data_all.update({user.name: {'lines': list2, 'total': total}
                             })
        return data_all

    def status_record(self):
        if self.select_state==False:
            return self.select_state
        else:
            return self.select_state.title()

    def invoice_person_pdf_report(self):
        if self.end_date < self.start_date:
            raise ValidationError('Enter End Date greater then Start Date')
        datas = {
            'ids': self._ids,
            'model': 'invoice.person.wizard',
            'form': self.read()[0],
            'invoice_details': self.invoice_record_data()
        }
        return self.env.ref('bi_all_in_one_invoice_reports.action_invoice_person_report').report_action(self.id, data=datas)

    def company_record(self):
        comp_name = []
        for comp in self.company_ids:
            comp_name.append(comp.name)
        listtostr = ', '.join([str(elem) for elem in comp_name])
        return listtostr

    def invoice_person_xls_report(self):
        if self.end_date < self.start_date:
            raise ValidationError('Enter End Date greater then Start Date')

        workbook = xlwt.Workbook()
        stylePC = xlwt.XFStyle()
        worksheet = workbook.add_sheet('User Wise Invoice Detail Report')
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
        horz_style_pc = xlwt.XFStyle()
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

        worksheet.write_merge(0, 1, 0, 6, 'Invoice Report By Sale Person', style=stylePC)
        worksheet.col(2).width = 5600
        worksheet.write_merge(2, 2, 0, 6, 'Companies: '+str(self.company_record()), style=xlwt.easyxf(
            "font: name Liberation Sans, bold on; align: horiz center;"))

        worksheet.write(3, 0, 'Start Date: '+str(self.start_date.strftime('%d/%m/%Y')), style=xlwt.easyxf(
            "font: name Liberation Sans, bold on;"))
        worksheet.write(3, 6, 'End Date: '+str(
            self.end_date.strftime('%d-%m-%Y')), style=xlwt.easyxf(
            "font: name Liberation Sans, bold on; align: horiz left;"))
        if self.select_state==False:
            worksheet.write(4, 0, 'Status: ', style=xlwt.easyxf(
                "font: name Liberation Sans, bold on;align: horiz left;"))
        else:
            worksheet.write(4, 0, 'Status: '+self.status_record(), style=xlwt.easyxf(
                "font: name Liberation Sans, bold on;align: horiz left;"))
        invoice_records = self.invoice_record_data()
        row = 5
        for person in invoice_records:
            row += 1
            worksheet.write_merge(row, row, 0, 6, 'Sale Person:' + person,
                                  style=style_line_heading)
            list1 = ['Order Number', 'Order Date', 'Customer', 'Total', 'Amount Invoiced',
                     'Amount Due','Amount Paid']
            row += 2
            worksheet.col(0).width = 5000
            worksheet.write(row, 0, list1[0], style=style_line_heading_left)
            worksheet.col(1).width = 5000
            worksheet.write(row, 1, list1[1], style1)
            worksheet.col(2).width = 5000
            worksheet.write(row, 2, list1[2], style1)
            worksheet.col(3).width = 5000
            worksheet.write(row, 3, list1[3], style1)
            worksheet.col(4).width = 5000
            worksheet.write(row, 4, list1[4], style1)
            worksheet.col(5).width = 5000
            worksheet.write(row, 5, list1[6], style1)
            worksheet.col(6).width = 5000
            worksheet.write(row, 6, list1[5], style1)
            row = row + 1
            for order in invoice_records[person]['lines']:
                worksheet.write(row, 0, order[0])
                worksheet.write(row, 1, order[1])
                worksheet.write(row, 2, order[2])
                worksheet.write(row, 3, order[3])
                worksheet.write(row, 4, order[4])
                worksheet.write(row, 5, order[6])
                worksheet.write(row, 6, order[5])
                row += 1
            row += 1
            worksheet.write(row, 2, 'Total', style=xlwt.easyxf(
                "font: name Liberation Sans, bold on; align: horiz center;"))
            worksheet.write(row, 3, invoice_records[person]['total'][0], style=xlwt.easyxf(
                "font: name Liberation Sans; align: horiz right;"))
            worksheet.write(row, 4, invoice_records[person]['total'][1], style=xlwt.easyxf(
                "font: name Liberation Sans; align: horiz right;"))
            worksheet.write(row, 5, invoice_records[person]['total'][3], style=xlwt.easyxf(
                "font: name Liberation Sans; align: horiz right;"))
            worksheet.write(row, 6, invoice_records[person]['total'][2], style=xlwt.easyxf(
                "font: name Liberation Sans; align: horiz right;"))
            row = row + 1
        file_data = BytesIO()
        workbook.save(file_data)
        self.write({
            'data': base64.encodestring(file_data.getvalue()),
            'file_name': 'Invoice Report By Sale person.xls'
        })

        action = {
            'type': 'ir.actions.act_url',
            'name': 'contract',
            'url': '/web/content/invoice.person.wizard/%s/data/Invoice Report By Sale person.xls?download=true' % (self.id),
            'target': 'self',
        }
        return action
