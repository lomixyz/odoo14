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
from stdnum import isin


class InvoiceSummaryReport(models.TransientModel):
	_name = 'invoice.summary.report.wizard'
	_description = 'Invoice Summary Report Wizard'

	start_date = fields.Date(string="Start Date")
	end_date = fields.Date(string="End Date")
	select_state = fields.Selection([
		('all', 'All'),
		('unpaid','Unpaid'),
		('paid', 'Paid'),
	], string='Invoice Status', default='all')
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
		final_data = {}
		state = []
		if self.select_state == 'all':
			state.extend(['in_payment', 'partial', 'reversed','invoicing_legacy','not_paid','paid'])
		elif self.select_state == 'unpaid':
			state.extend(['not_paid'])
		elif self.select_state == 'paid':
			state.extend(['paid'])
		elif self.select_state == False:
			state.extend(['in_payment', 'partial', 'reversed','invoicing_legacy','not_paid','paid'])
		status = ('payment_state', 'in', state)
		invoice_ids = self.env['account.move'].search([('invoice_date', '>=', start_date),
												  ('invoice_date', '<=', end_date),('move_type','=','out_invoice'),
												  ('company_id', 'in', selected_companies),status])
		
		list1 = []
		total_amount = 0 
		for invoice in invoice_ids:
			if invoice:
				invoiced_currency = invoice.currency_id
				user_currency = self.env.user.company_id.currency_id
				user_currency_amount = invoiced_currency._convert(invoice.amount_total, user_currency, invoice.company_id, invoice.invoice_date)
				user_currency_amount = user_currency_amount
				list1.append([invoice.name, invoice.partner_id.name, invoice.invoice_date, invoice.amount_total, invoice.currency_id.name, user_currency_amount])

		if self.select_state == False:
			final_data.update({'date': [self.start_date, self.end_date, self.company_record(),
										self.select_state,],
							   'invoice_data': list1,})
		else:
			final_data.update({'date': [self.start_date, self.end_date, self.company_record(),
										self.select_state.capitalize()],
							   'invoice_data': list1,})

		 
		return self.env.ref(
			'bi_all_in_one_invoice_reports.action_invoice_summary_report').report_action(self,
																				   data=final_data)

	def company_record(self):
		comp_name = []
		for comp in self.company_ids:
			comp_name.append(comp.name)
		listtostr = ', '.join([str(elem) for elem in comp_name])
		return listtostr

	def generate_xls_report(self):
		workbook = xlwt.Workbook()
		stylePC = xlwt.XFStyle()
		worksheet = workbook.add_sheet('Invoice Summary Report')
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

		worksheet.write_merge(0, 1, 0, 5, 'Invoice Summary Report', style=stylePC)
		worksheet.col(2).width = 5600
		worksheet.write_merge(2, 3, 0, 5, 'Companies: ' + str(self.company_record()), style=xlwt.easyxf(
			"font: name Liberation Sans, bold on; align: horiz center;"))
		worksheet.write(4, 0, 'Start Date: ' + str(self.start_date.strftime('%d-%m-%Y')),
						style=xlwt.easyxf(
							"font: name Liberation Sans, bold on;"))
		worksheet.write(4, 5, 'End Date: ' + str(
			self.end_date.strftime('%d-%m-%Y')), style=xlwt.easyxf(
			"font: name Liberation Sans, bold on; align: horiz left;"))
		if self.select_state == False:
			worksheet.write(5, 0, 'Status: ', style=xlwt.easyxf(
				"font: name Liberation Sans, bold on;"))
		else:
			worksheet.write(5, 0, 'Status: ' + str(self.select_state).capitalize(), style=xlwt.easyxf(
				"font: name Liberation Sans, bold on;"))
		row = 7
		list1 = ['Invoice Number', 'Customer', 'Invoice Date', 'Invoice Amount', 'Invoice Currency','Amount in Company Currency']
		worksheet.col(0).width = 5000
		worksheet.write(row, 0, list1[0], style=style_line_heading_left)
		worksheet.col(1).width = 5000
		worksheet.write(row, 1, list1[1], style=style_line_heading_left)
		worksheet.col(2).width = 5000
		worksheet.write(row, 2, list1[2], style=style_line_heading_left)
		worksheet.col(3).width = 5000
		worksheet.write(row, 3, list1[3], style=style_line_heading_left)
		worksheet.col(4).width = 5000
		worksheet.write(row, 4, list1[4], style=style_line_heading_left)
		worksheet.col(5).width = 8000
		worksheet.write(row, 5, list1[5], style=style_line_heading_left)

		row += 1
		invoice_records = self.generate_pdf_report()
		if invoice_records['context'].get('report_action')==None:
			invoice_datas = invoice_records['data']['invoice_data']
		else:
			invoice_datas = invoice_records['context']['report_action']['data']['invoice_data']
		for invoice in invoice_datas:
			worksheet.write(row, 0, invoice[0])
			worksheet.write(row, 1, invoice[1])
			worksheet.write(row, 2, invoice[2].strftime('%m-%d-%Y'))
			worksheet.write(row, 3, invoice[3])
			worksheet.write(row, 4, invoice[4])
			amount = round(invoice[5], 2)
			worksheet.write(row, 5, amount)
			row = row + 1
		total = sum([invoice[5] for invoice in invoice_datas])
		rounded_total = round(total, 2)
		worksheet.write(row, 5, rounded_total)

		row += 2
		file_data = BytesIO()
		workbook.save(file_data)
		self.write({
			'data': base64.b64encode(file_data.getvalue()),
			'file_name': 'Invoice Summary Report.xls'
		})
		action = {
			'type': 'ir.actions.act_url',
			'name': 'contract',
			'url': '/web/content/invoice.summary.report.wizard/%s/data/Invoice Summary Report.xls?download=true' % (
				self.id),
			'target': 'self',
		}
		return action