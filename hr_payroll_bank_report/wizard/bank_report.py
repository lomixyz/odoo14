
import base64
import os
from datetime import datetime
from datetime import date
from datetime import *
from io import BytesIO
from odoo.exceptions import except_orm, Warning, RedirectWarning, UserError, ValidationError

import xlsxwriter
from PIL import Image as Image
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from xlsxwriter.utility import xl_rowcol_to_cell


class bankreportexcelwiz(models.TransientModel):
	_name = 'bank.report.wiz'

	bank_check = fields.Boolean('Main Bank')
	batch_id = fields.Many2one('hr.payslip.run', string="Payslip Batch")

	# to get salary rules names
	def get_values(self):
		vals = []

		batch = self.env['hr.payslip.run'].search([('id', '=',  self.batch_id.id)])
		c = 0
		payslips = self.env['hr.payslip'].search([('payslip_run_id', '=',  self.batch_id.id),('employee_id.bank_account_id.bank_id.main_bank','=',self.bank_check)])
		for payslip in payslips:
			c = c + 1
			r = []
			r.append(c)
			r.append(payslip.employee_id.name)
			r.append(payslip.employee_id.bank_account_id.acc_number)
			line = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id), ('code', '=', 'NET')])
			if line:
				r.append(line.amount)
			else:
				r.append(0.0)
			r.append(payslip.employee_id.bank_account_id.bank_id.bic if payslip.employee_id.bank_account_id and payslip.employee_id.bank_account_id.bank_id else '')
			r.append(len(payslips))
			r.append(payslip.employee_id.emp_code)
			r.append(payslip.employee_id.bank_account_id.branch)
			vals.append(r)

		return vals

	# to get salary rules names

	def get_payment_acc(self):
		vals = []

		for acc in self.env['res.partner.bank'].search([('payment_account','=', True)]):
			vals.append(acc.acc_number)

		return vals


	def get_payment_total(self):
		vals = []
		total_amount = 0
		batch = self.env['hr.payslip.run'].search([('id', '=',  self.batch_id.id)])
		for payslip in self.env['hr.payslip'].search([('payslip_run_id', '=',  self.batch_id.id), ('employee_id.bank_account_id.bank_id.main_bank', '=', self.bank_check)]):
			line = self.env['hr.payslip.line'].search([('slip_id','=',payslip.id), ('code', '=', 'NET')])
			if line:
				total_amount += line.amount  
		vals.append(total_amount)

		return vals

	def get_item_data(self):
		data = self.get_values()
		payment_acc = self.get_payment_acc()
		total_payment = self.get_payment_total()

		file_name = _('bank report.xlsx')
		fp = BytesIO()

		workbook = xlsxwriter.Workbook(fp)

		heading_format = workbook.add_format({'align': 'center','valign': 'vcenter','bold': True, 'size': 14})
		cell_text_format_n = workbook.add_format({'align': 'center','bold': True, 'size': 9,})
		cell_text_format = workbook.add_format({'align': 'left','bold': True, 'size': 9,})
		cell_text_format.set_border()
		cell_text_format_new = workbook.add_format({'align': 'left','size': 9,})
		cell_text_format_new.set_border()
		cell_number_format = workbook.add_format({'align': 'right','bold': False, 'size': 9,'num_format': '#,###0.00'})
		cell_number_format.set_border()
		worksheet = workbook.add_worksheet('bank report.xlsx')
		normal_num_bold = workbook.add_format({'bold': True, 'num_format': '#,###0.00', 'size': 9, })
		normal_num_bold.set_border()
		worksheet.set_column('A:A', 20)
		worksheet.set_column('B:B', 20)
		worksheet.set_column('C:C', 20)
		worksheet.set_column('D:D', 20)
		worksheet.set_column('E:E', 60)
		worksheet.set_column('F:F', 20)
		worksheet.set_column('G:G', 20)
		worksheet.set_column('H:H', 20)
		worksheet.set_column('I:I', 20)
		worksheet.set_column('J:J', 20)
		worksheet.set_column('K:K', 20)
		worksheet.set_column('L:L', 20)
		worksheet.set_column('M:M', 20)
		worksheet.set_column('N:N', 20)

		row = 0
		column = 0
		worksheet.write(row, 0, 'CR/DR', cell_text_format_n)
		worksheet.write(row, 1, 'Account Number', cell_text_format_n)
		worksheet.write(row, 2, 'Employee ID', cell_text_format_n)
		worksheet.write(row, 3, 'Employee Name', cell_text_format_n)
		worksheet.write(row, 4, 'Amount', cell_text_format_n)
		worksheet.write(row, 5, 'Branch', cell_text_format_n)
		if not self.bank_check:
			worksheet.write(row, 6, 'Swift Code', cell_text_format_n)

		row += 1

		worksheet.write(row, 0, 'DR', cell_text_format_n)
		worksheet.write(row, 1, payment_acc[0] if payment_acc else '', cell_text_format_n)
		worksheet.write(row, 2, data[0][5] if data else 0, cell_text_format_n)
		worksheet.write(row, 3, 'Company Account', cell_text_format_n)
		worksheet.write(row, 4, total_payment[0] or '', cell_text_format_n)

		row += 1

		for rec in data:
			no = rec[0]
			acc_number = rec[2]
			employee_name = rec[1]
			amount = rec[3]
			employee_code = rec[6]


			worksheet.write(row, 0, 'CR', cell_text_format_n)
			worksheet.write(row, 1, acc_number or '', cell_text_format_n)
			worksheet.write(row, 2, employee_code or '', cell_text_format_n)
			worksheet.write(row, 3, employee_name or '', cell_text_format_n)
			worksheet.write(row, 4, amount or '', cell_text_format_n)
			worksheet.write(row, 5, rec[7] or '', cell_text_format_n)
			if not self.bank_check:
				worksheet.write(row, 6, rec[4] or '', cell_text_format_n)

			row += 1

		workbook.close()
		file_download = base64.b64encode(fp.getvalue())

		fp.close()

		self = self.with_context(default_name=file_name, default_file_download=file_download)

		return {
			'name': 'bank report Download',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'bank.report.excel',
			'type': 'ir.actions.act_window',
			'target': 'new',
			'context': self._context,
		}


class bank_report_excel(models.TransientModel):
	_name = 'bank.report.excel'

	name = fields.Char('File Name', size=256, readonly=True)
	file_download = fields.Binary('Download bank', readonly=False)

