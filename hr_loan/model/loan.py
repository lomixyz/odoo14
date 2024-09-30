# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import time
from datetime import datetime, timedelta
import calendar
from dateutil import relativedelta
from odoo.exceptions import UserError,Warning

class AccountPayment(models.Model):
	_inherit = 'account.payment'
	
	loan_id = fields.Many2one('hr.loan','Loan',help='Loan Record', readonly=True)
	
	#@api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id')
	@api.depends('journal_id', 'partner_id', 'partner_type', 'is_internal_transfer')
	def _compute_destination_account_id(self):
		for rec in self:
			if rec.loan_id:
				if rec.loan_id.employee_id.loan_account_type == 'once':
					if not rec.loan_id.company_id.loan_account_id:
						raise UserError(_('Please set loan account for company!'))
					rec.destination_account_id = self.loan_id.company_id.loan_account_id.id
				elif rec.loan_id.employee_id.loan_account_type == 'multiple':
					if not rec.loan_id.employee_id.loan_account_id:
						raise UserError(_('Please set loan account for selected employee!'))
					rec.destination_account_id = rec.loan_id.employee_id.loan_account_id.id
				else:
					raise UserError(_('Please set loan account method!'))
			else:
				return super(AccountPayment, rec)._compute_destination_account_id()

	def post(self):
		for rec in self:
			if rec.loan_id and rec.payment_type == 'inbound':
				amount =  rec.amount
				for line in rec.loan_id.loan_line_ids:
					if not line.is_settled and line.remaining_amount == amount:
						line.is_settled = True
						line.remaining_amount = 0.0
						break
					elif not line.is_settled and line.remaining_amount > amount:
						if  line.remaining_amount - amount < 0.01:
							line.is_settled = True
						line.remaining_amount -= amount
						break
					elif not line.is_settled and line.remaining_amount < amount:
						amount -= line.remaining_amount
						line.remaining_amount = 0.0
						line.is_settled = True
		return super(AccountPayment, self).post()
				
class HrLoan(models.Model):
	_name = "hr.loan"
	_description = "Loan"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_order = "id desc"
	
	def _get_employee_id(self):
		employee = self.env['hr.employee'].search([('user_id','=',self._uid)])
		if employee:
			return employee[0]
		else:
			return False

	name = fields.Char('Number',readonly=True,help='Sequence of loan',tracking=True, default="New", copy=False)
	employee_id = fields.Many2one('hr.employee','Employee', required=True,help='Employee Name',tracking=True, default = _get_employee_id)
	amount = fields.Float('Amount', required=True,help='Amount of loan',tracking=True)
	start_date = fields.Date('Date', required=True,help='Date of request',tracking=True, default = lambda *a: time.strftime('%Y-%m-%d'))
	reason = fields.Text('Reason',help='Reason of loan',tracking=True, copy=False)
	is_exceed = fields.Boolean('Exceed the Maximum',help='True if the amount is more than the employee limit',tracking=True, copy=False)
	is_exceed_2 = fields.Boolean('Exceed the Maximum',help='True if the amount is more than the employee limit', copy=False)
	payment_method = fields.Many2one('account.journal','Payment Method',help='Payment method to pay the loan',tracking=True)
	state = fields.Selection([('draft', 'Draft'), ('approved', 'Approved'),('cancel', 'Cancel'),('refused', 'Refused')], 'Status',default="draft", tracking=True, copy=False)
	type_id = fields.Many2one('hr.loan.type','Loan Type', required=True,tracking=True)
	depart_id = fields.Many2one('hr.department','Department',help='Department of employee')
	loan_line_ids = fields.One2many('hr.loan.line','loan_id','Loan Lines',help='Settlements Table',tracking=True, copy=False)
	refuse_reason = fields.Text('Refuse Reason',tracking=True, copy=False)
	total_amount = fields.Float('Total Amount', readonly=True,help='Amount of loan with interest rate',tracking=True, copy=False)
	number_months = fields.Integer('Number of Months',help='Number of months to deduct the loan total amount',tracking=True, copy=False) 
	is_generated = fields.Boolean('Generated',compute="_compute_is_generated")
	first_date = fields.Date('First Settlement Date',help='Start date for scheduling all settlements',tracking=True)
	contract_id = fields.Many2one('hr.contract', 'Contract', readonly=True)
	balance = fields.Float(compute="_get_balance" ,string='Balance',help='Remaining Amount')
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id, readonly=True)
	payment_id = fields.Many2one('account.payment','Payment Order', copy=False)
	has_reciept_voucher = fields.Boolean('Has Reciept Voucher',compute='_has_reciept_voucher')  
	
	def _has_reciept_voucher(self):
		self.has_reciept_voucher = True if self.env['account.payment'].search([('loan_id','=', self.id),('payment_type','=', 'inbound')]) else False
	
	@api.depends('loan_line_ids')
	def _compute_is_generated(self):
		for rec in self:
			if rec.loan_line_ids:
				rec.is_generated = True
			else:
				rec.is_generated = False
			
	def _get_balance(self):
		res = {}
		payslip_obj = self.env['hr.payslip']
		loan_lines_obj = self.env['hr.loan.line']
		for rec in self:
			rec.balance = sum(rec.loan_line_ids.mapped('remaining_amount'))
		
	
	@api.onchange('employee_id')
	def on_change_employee(self):
		self.depart_id = self.employee_id.department_id.id
		self.contract_id = self.employee_id.contract_id.id if self.employee_id.contract_id else False
	
	@api.onchange('type_id')
	def on_change_type(self):
		self.number_months = self.type_id.months
	
	def unlink(self):
		for loan in self:
			if loan.payment_id:
				raise UserError(_('You Can not Delete Loan/s has Payment Order !'))
			
			if loan.state != 'draft':
				raise UserError(_('You Can not Delete Loan/s not in draft status !'))
			
		return super(HrLoan,self).unlink()
	
	def refuse_advance(self):
		for loan in self:
			if not loan.refuse_reason:
				raise UserError(_('Please set the refuse reason !'))
		
		self.state = 'refused'
	
	def get_payment_vals(self):	
		return{
			'payment_type': 'outbound',
			# 'payment_date': self.start_date,
			'payment_method_id': 1,
			# 'communication': 'Loan For '+str(self.employee_id.name),
			'partner_type': 'supplier',
			'amount': self.total_amount,
			'journal_id': self.payment_method.id,
			'company_id': self.company_id.id,
			'loan_id': self.id
			   }
	
	def approve_loan(self):
		payment_obj = self.env['account.payment']
		
		if not self.payment_method:
			raise UserError(_('Please select a payment method first !'))
		
		
		if not self.loan_line_ids:
			raise UserError(_('Please set number of months and populate settlements table !'))
		
		payment_vals = self.get_payment_vals()
		
		if self.company_id.reference_employee_in_journal_entries and not self.employee_id.user_id:
			raise UserError(_("Please make sure the employee profile is linked it's user!"))
		elif self.company_id.reference_employee_in_journal_entries:
			payment_vals.update({'partner_id':self.employee_id.user_id.partner_id.id})
			
		
		payment = payment_obj.create(payment_vals)
		self.payment_id = payment.id
		self.state = 'approved'
		if self.name == 'New':
			self.name = self.env['ir.sequence'].sudo().next_by_code('hr.loan')
		return
	
	def cancel_loan(self):
		payment_obj = self.env['account.payment']
		if self.payment_id.state not in ['draft','sent','cancelled']:
			raise UserError(_('You can not cancel this loan, please contact accountant to cancel the payment order!'))
				
		self.payment_id.unlink()
		self.state = 'cancel'
		return True 

	def draft_loan(self):
		self.state = 'draft'
	
	@api.onchange('amount')	  
	@api.depends('employee_id','start_date')
	def on_change_amount(self):
		contract = self.employee_id.contract_id
		total_amount = 0.0
		employee_salary = 0.0
		warning = False
		res = {}
		if self.employee_id:
			if not contract:
				raise UserError(_('The Employee does not have valid contract'))
				
			employee_salary = contract.wage
			loan_percentage = ((contract.struct_id.loan_percentage) * 0.01)
			interest_rate = ((contract.struct_id.interest_rate) * 0.01)
			total_amount = self.amount + (self.amount*interest_rate)
			
			active_loans = self.search([('employee_id','=', self.employee_id.id), ('state','=', 'approved')])
			active_loan_total = 0
			for ac_loan in active_loans:
				active_loan_total += ac_loan.balance
			
			if (self.amount+active_loan_total) > (employee_salary*loan_percentage):
				res['value'] = {'is_exceed': True, 'is_exceed_2': True}
				warning = {
					'title': _("Warning"),
					'message': _('Amount is Above the Maximum limits '+str(employee_salary*loan_percentage - active_loan_total))
					}
		
		if warning:
			res['warning'] = warning
		if res:
			return res
		self.is_exceed = False
		self.is_exceed_2 = False
		self.total_amount = total_amount
		
	@api.model_create_multi
	@api.returns('self', lambda value: value.id)
	def create(self, vals):
		users_to_notify = self.env.user.company_id.loan_user_notify
		for val in vals:
			employee = self.env['hr.employee'].browse(val['employee_id'])
			contract = employee.contract_id
			date = datetime.strptime(val['start_date'], '%Y-%m-%d').date()
			equel = self.check_amount_totals(val ,'create')
			
			if val.get('is_exceed_2'):
				val['is_exceed'] = val['is_exceed_2']
			
			if contract:
				# set total_amount for loan with interest rate
				interest_rate = ((contract.struct_id.interest_rate) * 0.01)
				val['total_amount'] = val['amount'] + (val['amount']*interest_rate)
			else:
				raise UserError(_('The Employee does not have valid contract'))
		res = super(HrLoan,self).create(vals)
		
		if users_to_notify:
			for rec in res:
				res.add_follower(users_to_notify)
		res.validation()
		res.second_validation()
		return res
	
	def add_follower(self,users_to_notify):
		for user in users_to_notify:
			message = _('<div><p>Hello %s,</p><p>%s Created Loan and waiting your approval.</p></div>') % (user.name,self.employee_id.name)
			partner_id = user.partner_id
			add_follower = self.env['mail.wizard.invite'].create({'res_model':self._name,'res_id':self.id,'send_mail':True,'message':message})
			add_follower.partner_ids = partner_id.ids
			add_follower.add_followers()
	
	def check_amount_totals(self ,vals ,type_op):
		for rec in self:
			if type_op == 'create':
				if vals.get('loan_line_ids',False):
					amount_total = 0.0
					for line in vals['loan_line_ids']:
						amount_total += line[2]['amount']
					if abs(amount_total - vals['total_amount']) > 0.001:
						raise UserError(_('Total of Lines not equal to amount'))
			else:
				loan_line_obj = self.env['hr.loan.line']
				amount_total = 0.0
				loan_amount = rec.total_amount
				if vals.get('amount'):
					loan_amount = vals['amount']
					
				if vals.get('loan_line_ids'):
					for line in vals['loan_line_ids']:
						if type(line[2]) is dict and line[2].get('amount',0):
							amount_total += line[2]['amount']
						elif line[0] != 2:
							amount_total += loan_line_obj.browse(line[1]).amount
				else:
					for line in rec.loan_line_ids:
						amount_total += line.amount
				
				if amount_total and abs(amount_total - loan_amount) > 0.001:
					raise UserError(_('Total of Lines not equal to amount'))
		
	def write(self, vals):
		employee_obj = self.env['hr.employee']
		if vals.get('start_date'):
			start_date = vals['start_date']
		else:
			start_date = self.start_date
			
		if vals.get('employee_id'):
			employee = employee_obj.browse(vals['employee_id'])
		else:
			employee = self.employee_id
		
		if vals.get('is_exceed_2'):
			vals['is_exceed'] = vals['is_exceed_2']
			
		contract = employee.contract_id
		if not contract:
			raise UserError(_('The Employee does not have valid contract'))		
		
		if vals.get('loan_line_ids') or vals.get('amount'):
			equel = self.check_amount_totals(vals ,'write')
			
		if vals.get('start_date',False):
			date = datetime.strptime(vals['start_date'], '%Y-%m-%d').date()
			if not contract:
				raise UserError(_('The Employee does not have valid contract'))
					
		if vals.get('amount',False):
			if contract:
				loan_percentage = ((contract.struct_id.loan_percentage) * 0.01)
				# set total_amount for loan with interest rate
				interest_rate = ((contract.struct_id.interest_rate) * 0.01)
				vals['total_amount'] = vals['amount'] + (vals['amount']*interest_rate)
				
			else:
				raise UserError(_('The Employee does not have valid contract'))
					   
		res = super(HrLoan,self).write(vals)
		self.validation()
		self.second_validation()
		return res  
	
	def add_months(self, first_date, months):
		sourcedate = datetime.strptime(str(first_date),"%Y-%m-%d")
		month = sourcedate.month - 1 + months
		year = int(sourcedate.year + month / 12)
		month = month % 12 + 1
		day = min(sourcedate.day,calendar.monthrange(year,month)[1])
		return year,month,day

	def generate_months(self):
		loan_line_obj = self.env['hr.loan.line']
		for rec in self:
			loan_amount = rec.total_amount
			num_months = rec.number_months
			start_date = rec.start_date
			first_date = rec.first_date
			if not num_months:
				raise UserError(_('Set number of months to generate.'))
			
			if self.state != 'draft':
				raise UserError(_('Loan is not draft.'))
			
			if not loan_amount:
				raise UserError(_('Set amount to generate.'))
			
			if not first_date:
				raise UserError(_('Set start date to generate.'))
			else:
				if first_date < start_date:
					raise UserError(_('Start date must be after or equal of loan date.'))
				
			amount_per_month = loan_amount / num_months
			for i in range(0,num_months):
				date =  rec.add_months(first_date, i)
				new_date = str(date[0])+"-"+str(date[1])+"-"+str(date[2])
				vals = {'loan_id': self.id ,'discount_date': new_date ,'amount':amount_per_month}
				loan_line_obj.create(vals)
	
	def clean_months(self):
		for rec in self:
			if rec.state == 'draft':
				rec.loan_line_ids.unlink()
			else:
				raise UserError(_('Loan is not draft'))
	
	@api.model
	def second_validation(self):
		for rec in self:
			if rec.type_id.marriage:
				res = self.search_count([('type_id','=',self.type_id.id),('employee_id','=',self.employee_id.id),('state','=','approved')])
				if res >  1:
					raise UserError(_('The marriage loan only once per service period!'))
	
	# TO CHECK
	@api.model
	def validation(self):
		return True
		if self.type_id.marriage:
			if self.employee_id.marital != 'single':
				raise UserError(_('The Marriage loan eligible for single employees only!'))
			
			if self.employee_id.gender != 'male':
				raise UserError(_('The Marriage loan not eligible for females!'))
				
		if self.contract_id.trial_date_start and self.contract_id.trial_date_end:
			if self.start_date >= self.contract_id.trial_date_start and self.start_date <= self.contract_id.trial_date_end:
				raise UserError(_('The Employee not eligible for the loan in Trial Period Duration! '))
		else:
			return True
		
		
	def move_res_partner_to_payment(self):
		payments = self.env['account.payment'].search([('loan_id','!=',False)])
		for payment in payments:
			if payment.loan_id.employee_id.user_id:
				payment.partner_id = payment.loan_id.employee_id.user_id.partner_id.id
				for move in payment.move_line_ids:
					move.partner_id = payment.loan_id.employee_id.user_id.partner_id.id
	
	
class HrLoanLine(models.Model):
	_name = "hr.loan.line"
	_order = 'discount_date'

	loan_id = fields.Many2one('hr.loan','Loan')
	discount_date = fields.Date('Settlement Date', required=True, help='Date of which the settlement will apprear in payslip')
	amount = fields.Float('Amount', required=True, help='Amount of each payment')
	is_settled = fields.Boolean('Settled', readonly=True)
	remaining_amount = fields.Float('Remaining Amount', readonly=True)
	
	def write(self,vals):
		if 'amount' in vals:
			vals['remaining_amount'] = vals['amount']
		return super(HrLoanLine, self).write(vals)
	
	@api.model_create_multi
	@api.returns('self', lambda value: value.id)
	def create(self,vals):
		for val in vals:
			val['remaining_amount'] = val['amount'] if 'amount' in val else 0
		return super(HrLoanLine, self).create(vals)
	
	def unlink(self):
		for l in self:
			if l.is_settled:
				raise UserError(_('You cannot delete line already settled!'))
		
		return super(HrLoanLine, self).unlink()
	
	
class HrLoanType(models.Model):
	_name = "hr.loan.type"
	
	name = fields.Char('Name', required=True)
	months = fields.Integer('Number of Months', help='Default number of months to deduct the loan total amount for this type')
	marriage = fields.Boolean('Is Marriage')
	
class HrPayrollStructure(models.Model):
	_inherit = "hr.payroll.structure"

	interest_rate = fields.Float('Interest Rate')
	loan_percentage = fields.Integer('Max Loan Percentage (%)', default=100 ,help='Maximum percentage of loan for each structure')
	 
class HrPayslip(models.Model): 
	_inherit = 'hr.payslip'
	
	
	@api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
	def _onchange_employee(self):
		vals=[]
		res = super(HrPayslip, self).onchange_employee()
		contract_obj = self.env['hr.contract']
		loan_obj = self.env['hr.loan']
		loan_line_obj = self.env['hr.loan.line']
		input_type = self.env.ref('hr_loan.loan_input_type')
		for rec in self:
			if rec.employee_id and rec.date_from and rec.date_to:
				loans = loan_obj.search([('employee_id','=',rec.employee_id.id),('state','=','approved'),])
				loan_total = 0.0
				loan_name = 'Loan - '
				if loans:
					contract = rec.employee_id.contract_id
					for loan in loans:
						lines = loan_line_obj.search([('loan_id','=',loan.id),('is_settled','!=', True),
													  ('discount_date','>=',rec.date_from),('discount_date','<=',rec.date_to)])
						if lines:
							for line in lines :
								if  line.id  not in rec.mapped('input_line_ids').loan_line_id.ids:
									rec.input_line_ids = [(0, 0,{'name': loan_name+str(line.loan_id.name), 
																 'amount': line.remaining_amount, 
																 'contract_id': contract.id,
																 'loan_line_id': line.id,
																 'code':'LOAN',
																 'input_type_id':input_type.id
														})]
		return res
	   
	def action_payslip_done(self):
		changed_rules = []
		for slip in self:
			for line in slip.line_ids:
				if line.code == 'LOR' and slip.employee_id.loan_account_type:
					acc_id = False
					if slip.employee_id.loan_account_type == 'once':
						acc_id = slip.employee_id.company_id.loan_account_id.id
					else:
						acc_id = slip.employee_id.loan_account_id.id
					
					if line.amount < 0:
						line.salary_rule_id.account_debit = acc_id
						changed_rules.append(line.salary_rule_id)
					else:
						line.salary_rule_id.account_credit = acc_id
						changed_rules.append(line.salary_rule_id)
					
		res = super(HrPayslip, self).action_payslip_done()
		for lin in slip.line_ids:
			if lin.code == 'LOR' and self.env.user.company_id.loan_account_type == 'once' and self.env.user.company_id.reference_employee_in_journal_entries == True:
				for account in self.move_id.line_ids:
					if account.account_id.id == self.env.user.company_id.loan_account_id.id:
						account.write({'partner_id':self.browse(self.ids[0]).employee_id.user_id.partner_id.id})
		for payslip in self:
			for l in payslip.input_line_ids:
				if l.loan_line_id:
					if l.loan_line_id.discount_date >= payslip.date_from and l.loan_line_id.discount_date <= payslip.date_to:
						l.loan_line_id.is_settled = not payslip.credit_note
						l.loan_line_id.remaining_amount = 0.0
					else:
						raise UserError(_('Loan %s not in period!') % (l.loan_line_id.loan_id.name))
		
		for rule in changed_rules:
			rule.account_debit = False
			rule.account_credit = False
		
		return res
	
	
	def refund_sheet(self):
		res = super(HrPayslip, self).refund_sheet()
		loan_line_model = self.env['hr.loan.line']
		for line in self:
			loan_line = loan_line_model.search([('loan_id.employee_id','=',line.employee_id.id),
											('discount_date','<=',line.date_to),
											('discount_date','>=',line.date_from)])
			if loan_line :
				loan_line.write({'is_settled':False})
				for rec in loan_line:
					rec.remaining_amount = rec.amount

	
		
		
		
class HrPayslipInput(models.Model):
	_inherit = 'hr.payslip.input'
	input_type_id = fields.Many2one('hr.payslip.input.type', string='Description', required=True, domain="[]")
	loan_line_id = fields.Many2one('hr.loan.line')
	struct_id = fields.Many2one('hr.payroll.structure', string='Structure', related='payslip_id.struct_id')
	_allowed_input_type_ids = fields.Many2many('hr.payslip.input.type',
											   related='payslip_id.struct_id.input_line_type_ids')


	@api.model_create_multi
	@api.returns('self', lambda value: value.id)
	def create(self, vals):
		res = super(HrPayslipInput, self).create(vals)
		for rec in res:
			if rec.loan_line_id:
				rec.amount = rec.loan_line_id.remaining_amount
		return res


	@api.onchange('struct_id')
	def _onchange_struct_id(self):
		return {'domain': {'input_type_id': ['|', ('id', 'in', self.payslip_id.struct_id.input_line_type_ids.ids), ('struct_ids', '=', False)]}}

	
class HrEmployee(models.Model): 
	_inherit = 'hr.employee'
	
	
	loan_count = fields.Integer(compute="_get_loan_counts", string='Loans')
	loan_account_id = fields.Many2one('account.account','Loan Account')
	loan_account_type = fields.Selection([('once','One Account For All Employees'),('multiple','Account Per Employee')], 
										 string='Employees Loan Account', related='company_id.loan_account_type', readonly=True)
	
	def _get_loan_counts(self):
		loan = self.env['hr.loan']
		for rec in self:
			rec.loan_count = loan.search_count([('employee_id', '=', self.id)]) 
		
class HrPayslipInputType(models.Model):
    _name = 'hr.payslip.input.type'
    _description = 'Payslip Input Type'

    name = fields.Char(string='Description', required=True)
    code = fields.Char(required=True, help="The code that can be used in the salary rules")
    struct_ids = fields.Many2many('hr.payroll.structure', string='Availability in Structure', help='This input will be only available in those structure. If empty, it will be available in all payslip.')
    country_id = fields.Many2one('res.country', string='Country', default=lambda self: self.env.company.country_id)


