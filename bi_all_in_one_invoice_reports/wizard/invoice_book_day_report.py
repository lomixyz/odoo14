# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import base64
from odoo import api, fields, models
from io import BytesIO
from io import StringIO
import io

try:
	import xlwt
except ImportError:
	xlwt = None


class InvoiceDayBookReport(models.TransientModel):
	_name = "invoice.day.book.report"
	_description = 'Invoice Day Book Report'

	start_date = fields.Date('Start Period', required=True)
	end_date = fields.Date('End Period', required=True)
	file_name = fields.Char('Excel File', readonly=True)
	data = fields.Binary(string="File")


	def invoice_day_book_pdf_report(self):
		datas = {
			'ids': self._ids,
			'model': 'invoice.day.book.report',
			'start_date': self.start_date,
			'end_date': self.end_date
		}
		return self.env.ref('bi_all_in_one_invoice_reports.invoice_day_book_report_template').report_action(self)


	def invoice_day_book_xls_report(self):
		filename = 'Invoice Day Book Report.xls'
		workbook = xlwt.Workbook()
		stylePC = xlwt.XFStyle()
		alignment = xlwt.Alignment()
		alignment.horz = xlwt.Alignment.HORZ_CENTER
		fontP = xlwt.Font()
		fontP.bold = True
		fontP.height = 200
		heading_xf = xlwt.easyxf(
			"font: bold on, color white;align:wrap on,vert centre,horiz center;pattern:pattern solid,pattern_fore_colour black;")
		heading_style = xlwt.easyxf(
			"font:height 300; font:name Liberation Sans,bold on,color black;align:vert centre,horiz center;pattern:pattern solid,fore_colour gray50;")
		worksheet = workbook.add_sheet('Sheet 1')
		worksheet.write_merge(0, 1, 0, 6, "Invoice Day Book Report", style=heading_style)
		worksheet.write(3, 1, 'Start Date:', heading_xf)
		worksheet.write(4, 1, str(self.start_date))
		worksheet.write(3, 3, 'End Date', heading_xf)
		worksheet.write(4, 3, str(self.end_date))
		final_header = []
		header = ['DATE', 'INVOICE NUMBER', 'ACCOUNT CODE', 'CUSTOMER', 'DESCRIPTION', 'TOTAL']
		key = ['date', 'name', 'acc_code', 'customer', 'name', 'total']
		header_tmp = self.env['report.bi_all_in_one_invoice_reports.invoice_book_report']._get_ref()
		categ_lst = list(set(header_tmp) - set(header))
		final_header.extend(header)
		final_header.extend(categ_lst)
		final_header.append('Tax')
		row = 6
		col = total = i = 0
		total_tax = 0
		obj = {'start_date': self.start_date, 'end_date': self.end_date}
		for a in final_header:
			worksheet.write(row, col, a, style=stylePC)
			col += 1
		row += 1
		col = 0
		invoice_ids = self.env['account.move'].search(
			[('invoice_date', '>=', self.start_date), ('invoice_date', '<=', self.end_date),
			 ('move_type', '=', 'out_invoice'), ('state', '=', 'posted')])
		for invoice in invoice_ids:
			total += invoice.amount_total
			detail_data = self.env['report.bi_all_in_one_invoice_reports.invoice_book_report']._get_data(invoice)
			if detail_data is not None:
				worksheet.write(row, 0, str(detail_data[0].get('date', '')))
				worksheet.write(row, 1, detail_data[0].get('number', 'Draft'))
				worksheet.write(row, 2, detail_data[0].get('acc_code', ''))
				worksheet.write(row, 3, detail_data[0].get('customer', 'Registered Customer'))
				worksheet.write(row, 4, detail_data[0].get('name', ''))
				worksheet.write(row, 5, detail_data[0].get('total', ''))
				total_tax += detail_data[0].get('tax', 0.0)

			col = 6
			for j in categ_lst:
				worksheet.write(row, col, detail_data[0].get(j))
				col += 1

			worksheet.write(row, col, detail_data[0].get('tax'))
			row += 1
			col = 0

		row += 1
		total_categ = self.env['report.bi_all_in_one_invoice_reports.invoice_book_report']._get_total(obj)
		worksheet.write(row, 5, 'Taxes Included ' + str(total))

		style = xlwt.XFStyle()

		font = xlwt.Font()
		font.bold = True
		style.font = font

		borders = xlwt.Borders()
		borders.bottom = xlwt.Borders.DASHED
		style.borders = borders

		col = 6
		for categ in categ_lst:
			worksheet.write(row, col, total_categ.get(categ), style=style)
			col += 1

		worksheet.write(row, col, total_tax, style=style)

		file_data = BytesIO()
		workbook.save(file_data)
		self.write({
			'data': base64.encodestring(file_data.getvalue()),
			'file_name': 'Invoice Day Book Report.xls'
		})
		action = {
			'type': 'ir.actions.act_url',
			'name': 'contract',
			'url': '/web/content/invoice.day.book.report/%s/data/Invoice Day Book Report.xls?download=true' % (
				self.id),
			'target': 'self',
		}
		return action


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: