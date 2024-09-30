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
import json
from odoo.exceptions import ValidationError





class InvoicePayment(models.TransientModel):
    _name = 'invoice.payment.wizard'
    _description = 'Payment Report for Invoice/Sales'

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    user_id = fields.Many2one('res.users', string='User id', default=lambda self: self.env.user)
    select_state = fields.Selection([
        ('all','All'),
        ('paid', 'Paid'),
    ], string='Status',default='all')
    company_ids = fields.Many2many('res.company', string='Companies')
    user_ids = fields.Many2many('res.users', string='User')
    file_name = fields.Char('Excel File', readonly=True)
    data = fields.Binary(string="File")
    is_manager = fields.Char(string="Manager", store=True)

    @api.model
    def default_get(self, fields):
        manager = self.env.user.has_group('account.group_account_manager')
        rec = super(InvoicePayment, self).default_get(fields)
        if self.user_ids not in rec:
            rec.update({
                'user_ids': [(6, 0, [self.env.user.id])],
                'is_manager': manager
            })
        return rec


    def invoice_payment_pdf_report(self):
        if self.end_date < self.start_date:
            raise ValidationError('Enter End Date greater then Start Date')
        companies = self.company_ids.ids
        if len(companies) > 0:
            selected_companies = companies
        else:
            selected_companies = self.env.user.company_ids.ids
        list1 = []
        if self.select_state == 'all':
            list1.extend(['draft','not_paid', 'paid', 'in_payment','partial'])
        elif self.select_state == 'paid':
            list1.extend(['paid'])
        elif self.select_state == False:
            list1.extend(['draft','not_paid', 'paid', 'in_payment','partial'])
        status = ('payment_state', 'in', list1)
        data_all = {}
        payment_total = {'Bank': 0, 'Cash': 0, 'Total': 0}
        if not self.user_ids:
            self.user_ids = self.user_id
            account_move = self.env['account.move'].search([('invoice_date', '>=', self.start_date), ('invoice_date', '<=', self.end_date),
                                                         ('company_id', 'in', selected_companies), status])
        else:
            account_move = self.env['account.move'].search([('invoice_date', '>=', self.start_date), ('invoice_date', '<=', self.end_date),
                                                         ('company_id', 'in', selected_companies),  ('invoice_user_id', 'in', self.user_ids.ids), status])

        for user in self.user_ids:
            data = []
            total_all = [0, 0, 0, 0]
            for move in account_move.filtered(lambda x : x.invoice_user_id == user):
                pyt_list = []
                invoice = move
                if invoice.invoice_payments_widget != 'false':
                    bank_amount = 0
                    cash_amount = 0
                    res = json.loads(invoice.invoice_payments_widget)
                    for i in res['content']:
                        if i['journal_name'] == 'Bank':
                            bank_amount += i['amount']
                        if i['journal_name'] == 'Cash':
                            cash_amount += i['amount']
                    if invoice.reversed_entry_id:
                        pyt_list.append(invoice.name)
                        pyt_list.append(invoice.invoice_date.strftime("%d/%m/%Y"))
                        pyt_list.append(user.name)
                        pyt_list.append(invoice.partner_id.name)
                        pyt_list.append(invoice.amount_residual)
                        pyt_list.append(-bank_amount)
                        pyt_list.append(-cash_amount)
                        pyt_list.append(-(bank_amount + cash_amount+invoice.amount_residual))
                        data.append(pyt_list)
                        total_all[0] -= bank_amount
                        total_all[1] -= cash_amount
                        total_all[3] += invoice.amount_residual
                    else:
                        pyt_list.append(invoice.name)
                        pyt_list.append(invoice.invoice_date.strftime("%d/%m/%Y"))
                        pyt_list.append(user.name)
                        pyt_list.append(invoice.partner_id.name)
                        pyt_list.append(invoice.amount_residual)
                        pyt_list.append(bank_amount)
                        pyt_list.append(cash_amount)
                        pyt_list.append(bank_amount + cash_amount+invoice.amount_residual)
                        data.append(pyt_list)
                        total_all[0] += bank_amount
                        total_all[1] += cash_amount
                        total_all[3] += invoice.amount_residual
                elif invoice.invoice_payments_widget == 'false':
                    bank_amount = 0
                    cash_amount = 0
                    if invoice.reversed_entry_id:
                        pyt_list.append(invoice.name)
                        pyt_list.append(invoice.invoice_date.strftime("%d/%m/%Y"))
                        pyt_list.append(user.name)
                        pyt_list.append(invoice.partner_id.name)
                        pyt_list.append(invoice.amount_residual)
                        pyt_list.append(-bank_amount)
                        pyt_list.append(-cash_amount)
                        pyt_list.append(bank_amount + cash_amount+invoice.amount_residual)
                        data.append(pyt_list)
                        total_all[0] -= bank_amount
                        total_all[1] -= cash_amount
                        total_all[3] += invoice.amount_residual
                    else:
                        pyt_list.append(invoice.name)
                        if invoice.invoice_date==False:
                            pyt_list.append(invoice.invoice_date)
                        else:
                            pyt_list.append(invoice.invoice_date.strftime("%d/%m/%Y"))
                        pyt_list.append(user.name)
                        pyt_list.append(invoice.partner_id.name)
                        pyt_list.append(invoice.amount_residual)
                        pyt_list.append(bank_amount)
                        pyt_list.append(cash_amount)
                        pyt_list.append(bank_amount + cash_amount+invoice.amount_residual)
                        data.append(pyt_list)
                        total_all[0] += bank_amount
                        total_all[1] += cash_amount
                        total_all[3] += invoice.amount_residual
            total_all[2] = total_all[0]+total_all[1]+total_all[3]

            data_all.update({user.name:[data,total_all]})
            payment_total['Bank'] += total_all[0]
            payment_total['Cash'] += total_all[1]
            payment_total['Total'] += total_all[0]+total_all[1]
        if self.select_state==False:
            data2 = {'data': [data_all, [self.start_date, self.end_date,payment_total],self.company_record(),self.select_state]}
        else:
            data2 = {'data': [data_all, [self.start_date, self.end_date,payment_total],self.company_record(),self.select_state.capitalize()]}
        data1 = self.env.ref(
            'bi_all_in_one_invoice_reports.action_invoice_payment_report').report_action(self, data=data2)
        return data1


    def company_record(self):
        comp_name = []
        for comp in self.company_ids:
            comp_name.append(comp.name)
        listtostr = ', '.join([str(elem) for elem in comp_name])
        return listtostr



    def invoice_payment_xls_report(self):


        if self.end_date < self.start_date:
            raise ValidationError('Enter End Date greater then Start Date')
        companies = self.company_ids.ids
        if len(companies) > 0:
            selected_companies = companies
        else:
            selected_companies = self.env.user.company_ids.ids
        list1 = []
        if self.select_state == 'all':
            list1.extend(['draft','not_paid', 'paid', 'in_payment','partial'])
        elif self.select_state == 'paid':
            list1.extend(['paid'])
        elif self.select_state == False:
            list1.extend(['draft','not_paid', 'paid', 'in_payment','partial'])
        status = ('payment_state', 'in', list1)
        data_all = {}
        payment_total = {'Bank': 0, 'Cash': 0, 'Total': 0}
        if not self.user_ids:
            self.user_ids = self.user_id
            account_move = self.env['account.move'].search([('invoice_date', '>=', self.start_date), ('invoice_date', '<=', self.end_date),
                                                         ('company_id', 'in', selected_companies), status])
        else:
            account_move = self.env['account.move'].search([('invoice_date', '>=', self.start_date), ('invoice_date', '<=', self.end_date),
                 ('company_id', 'in', selected_companies), ('invoice_user_id', 'in', self.user_ids.ids), status])
 



        if self.end_date < self.start_date:
            raise ValidationError('Enter End Date greater then Start Date')
        companies = self.company_ids.ids
        if len(companies) > 0:
            selected_companies = companies
        else:
            selected_companies = self.env.user.company_ids.ids
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Payment Report for Invoice/Sales')
        worksheet.col(0).width = 8000
        style_header = xlwt.easyxf(
            "font:height 400; font: name Liberation Sans, bold on,color black; align: vert centre, horiz center;pattern: pattern solid, pattern_fore_colour gray25;")
        style_line_heading = xlwt.easyxf(
            "font: name Liberation Sans, bold on; pattern: pattern solid, pattern_fore_colour gray25;")
        style_bold_white_left = xlwt.easyxf(
            "font: name Liberation Sans, bold on; align: horiz left;")
        style_bold_white_right = xlwt.easyxf(
            "font: name Liberation Sans, bold on; align: horiz right;")
        style_line_heading_center = xlwt.easyxf(
            "font: name Liberation Sans, bold on;align: horiz center; pattern: pattern solid, pattern_fore_colour gray25;")
        for_left_color = xlwt.easyxf("font: color red; align: horiz left")
        for_right_color = xlwt.easyxf("font: color red; align: horiz right")
        worksheet.write_merge(0, 1, 0, 7, 'Payment Report for Invoice/Sales', style=style_header)
        worksheet.write_merge(2, 2, 0, 7, 'Companies: '+str(self.company_record()), style=xlwt.easyxf(
            "font: name Liberation Sans, bold on; align: horiz center;"))
        worksheet.write(3, 0, 'Start Date: '+str(self.start_date.strftime('%d-%m-%Y')), style=xlwt.easyxf(
            "font: name Liberation Sans, bold on;"))
        worksheet.write(3, 7, 'End Date: '+str(
            self.end_date.strftime('%d-%m-%Y')), style=xlwt.easyxf(
            "font: name Liberation Sans, bold on; align: horiz left;"))
        if self.select_state==False:
            worksheet.write(4, 0, 'Status: ', style=xlwt.easyxf(
                "font: name Liberation Sans, bold on; align: horiz left;"))
        else:
            worksheet.write(4, 0, 'Status: '+str(self.select_state).capitalize(), style=xlwt.easyxf(
                "font: name Liberation Sans, bold on; align: horiz left;"))
        list2 = ['Invoice', 'Invoice Date', 'SalePerson', 'Customer', 'Bank', 'Cash','Amount Due',
                 'Total']
        row = 5
                                        
        for user in self.user_ids:
            row += 1
            worksheet.write_merge(row, row, 0, 7, 'Sale Person:' + str(user.name),
                                  style=style_line_heading_center)
            row += 2
            worksheet.col(0).width = 5000
            worksheet.write(row, 0, list2[0], style=style_line_heading)
            worksheet.col(1).width = 5000
            worksheet.write(row, 1, list2[1], style=style_line_heading)
            worksheet.col(2).width = 5000
            worksheet.write(row, 2, list2[2], style=style_line_heading)
            worksheet.col(3).width = 5000
            worksheet.write(row, 3, list2[3], style=style_line_heading)
            worksheet.col(4).width = 5000
            worksheet.write(row, 4, list2[4], style=style_line_heading)
            worksheet.col(5).width = 5000
            worksheet.write(row, 5, list2[5], style=style_line_heading)
            worksheet.col(6).width = 5000
            worksheet.write(row, 6, list2[6], style=style_line_heading)
            worksheet.col(7).width = 5000
            worksheet.write(row, 7, list2[7], style=style_line_heading)
            worksheet.col(7).width = 5000
            total_all = [0, 0, 0, 0]
            row += 1
    
          
            for invoice in account_move:
                bank_amount = 0
                cash_amount = 0
                
                if invoice.invoice_payments_widget!='false':
                   
                    res = json.loads(invoice.invoice_payments_widget)
                    for i in res['content']:
                        if i['journal_name'] == 'Bank':
                            bank_amount = i['amount']
                        if i['journal_name'] == 'Cash':
                            cash_amount = i['amount']
                        row += 1
                        worksheet.write(row, 0, invoice.name,style=for_left_color)
                        worksheet.write(row, 1, invoice.invoice_date.strftime("%d/%m/%Y"),style=for_left_color)
                        worksheet.write(row, 2, user.name,style=for_left_color)
                        worksheet.write(row, 3, invoice.partner_id.name,style=for_left_color)
                        worksheet.write(row, 4, bank_amount,style=for_right_color)
                        worksheet.write(row, 5, cash_amount,style=for_right_color)
                        worksheet.write(row, 6, invoice.amount_residual,style=for_right_color)
                        worksheet.write(row, 7, (bank_amount + cash_amount+invoice.amount_residual),style=for_right_color)
                        total_all[0] += bank_amount
                        total_all[1] += cash_amount
                        total_all[3] += invoice.amount_residual
                   
                elif invoice.invoice_payments_widget == 'false':
                    cash_amount = 0
                    bank_amount = 0
                    
                    if invoice.reversed_entry_id.state=='paid' and invoice.name!='/':
                        row += 1
                        worksheet.write(row, 0, invoice.name,style=for_left_color)
                        worksheet.write(row, 1, invoice.invoice_date.strftime("%d/%m/%Y"),style=for_left_color)
                        worksheet.write(row, 2, user.name,style=for_left_color)
                        worksheet.write(row, 3, invoice.partner_id.name,style=for_left_color)
                        worksheet.write(row, 4, bank_amount,style=for_right_color)
                        worksheet.write(row, 5, cash_amount,style=for_right_color)
                        worksheet.write(row, 6, invoice.amount_residual,style=for_right_color)
                        worksheet.write(row, 7, (bank_amount + cash_amount+invoice.amount_residual),style=for_right_color)
                        total_all[0] += bank_amount
                        total_all[1] += cash_amount
                        total_all[3] += invoice.amount_residual
                    else:
                        row += 1
                        worksheet.write(row, 0, invoice.name)
                        date_sale = ''
                        if invoice.invoice_date!=False:
                            date_sale += invoice.invoice_date.strftime("%d/%m/%Y")
                        else:
                            date_sale += ''
                        worksheet.write(row, 1, date_sale)
                        worksheet.write(row, 2, user.name)
                        worksheet.write(row, 3, invoice.partner_id.name)
                        worksheet.write(row, 4, bank_amount)
                        worksheet.write(row, 5, cash_amount)
                        worksheet.write(row, 6, invoice.amount_residual)
                        worksheet.write(row, 7, bank_amount + cash_amount+invoice.amount_residual)
                        total_all[0] += bank_amount
                        total_all[1] += cash_amount
                        total_all[3] += invoice.amount_residual
            total_all[2] = total_all[0]+total_all[1]+total_all[3]
            row += 1
            worksheet.write(row, 3, 'Total', style=style_bold_white_left)
            worksheet.write(row, 4, total_all[0], style=style_bold_white_right)
            worksheet.write(row, 5, total_all[1], style=style_bold_white_right)
            worksheet.write(row, 6, total_all[3], style=style_bold_white_right)
            worksheet.write(row, 7, total_all[2], style=style_bold_white_right)
            row += 1
            payment_total['Bank'] += total_all[0]
            payment_total['Cash'] += total_all[1]
            payment_total['Total'] += payment_total['Bank']+payment_total['Cash']
        row += 1
        list4 = ['Name', 'Total']
        worksheet.write_merge(row, row, 0, 1, 'Payment Method', style=style_line_heading_center)
        row += 1
        worksheet.col(0).width = 5000
        worksheet.write(row, 0, list4[0], style=style_line_heading_center)
        worksheet.col(1).width = 5000
        worksheet.write(row, 1, list4[1], style=style_line_heading_center)
        row += 1
        worksheet.col(0).width = 5000
        for payment in payment_total:
            worksheet.write(row, 0, payment)
            worksheet.write(row, 1, payment_total[payment])
            row += 1
        tz = pytz.timezone('Asia/Kolkata')
        file_data = BytesIO()
        workbook.save(file_data)

        self.write({
            'data': base64.encodestring(file_data.getvalue()),
            'file_name': 'Payment Report for Invoice_Sales.xls'
        })
        action = {
            'type': 'ir.actions.act_url',
            'name': 'contract',
            'url': '/web/content/invoice.payment.wizard/%s/data/Payment Report for Invoice_Sales.xls?download=true' % (self.id),
            'target': 'self',
        }
        return action


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

