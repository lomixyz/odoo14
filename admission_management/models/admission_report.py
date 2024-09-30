from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
from datetime import date


class admission_report_line(models.Model):
    _name = 'admission.report.line'

    report_id = fields.Many2one('admission.management.report', string='Report')
    partner_id = fields.Many2one('res.partner', string='Customer')
    status = fields.Char(_('Status'))
    worker_inarabic = fields.Char(_('worker_inarabic'))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'verified'),
        ('confirm', 'Confirm'),
        ('done', 'Done'),
        ('paid', 'Paid'),
        ('cancel', 'Rejected')], string='Status')
    contract_no = fields.Char(string='contract no')
    contract_date = fields.Date(string='contract date')
    number_of_days = fields.Integer(string='number of days')
    arrival_date = fields.Date(string='arrival date')
    total_cost = fields.Float(string='total Cost')
    total_paid = fields.Float(string='total paid')
    total_remain = fields.Float(string='total remaining')
    discount = fields.Float(string='discount')
    additions = fields.Float(string='additions')
    total_contract_with_vat = fields.Float("Total contract Amount With VAT")
    contract_vat_amount = fields.Float("contract Vat")
    contract_net_amount = fields.Float("contract Net Amount")
    responsible_id = fields.Char(string='responsible_id')
    line_state = fields.Selection([('paid', 'Paid'),
                                   ('not', 'Not'), ('partial', 'Partial')])

class rent_report_line(models.Model):
    _name = 'rent.report.line'

    report_id = fields.Many2one('admission.management.report', string='Report')
    partner_id = fields.Many2one('res.partner', string='Customer')
    status = fields.Char(_('Status'))
    employee_id = fields.Char(_('worker'))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'verified'),
        ('confirm', 'Confirm'),
        ('done', 'Done'),
        ('paid', 'Paid'),
        ('cancel', 'Rejected')], string='Status')
    contract_no = fields.Char(string='contract no')
    date_from = fields.Date(string='date from')
    date_to = fields.Date(string='date to')
    number_of_days = fields.Integer(string='number of days')
    arrival_date = fields.Date(string='arrival date')
    total_cost = fields.Float(string='total Cost')
    total_paid = fields.Float(string='total paid')
    total_remain = fields.Float(string='total remaining')
    discount = fields.Float(string='discount')
    additions = fields.Float(string='additions')
    total_contract_with_vat = fields.Float("Total contract Amount With VAT")
    contract_vat_amount = fields.Float("contract Vat")
    contract_net_amount = fields.Float("contract Net Amount")
    responsible_id = fields.Char(string='responsible_id')
    line_state = fields.Selection([('paid', 'Paid'),
                                   ('not', 'Not'), ('partial', 'Partial')])

class availability_report_line(models.Model):
    _name = 'availability.report.line'

    report_id = fields.Many2one('admission.management.report', string='Report')
    status = fields.Char(_('Status'))
    employee_id = fields.Char(_('worker'))
    employee_nationality = fields.Char(_('nationality'))    
    identification_id = fields.Char(_('eqama number'))
    passport_id = fields.Char(_('passport number'))
    gender = fields.Char(_('gender'))
    birthday = fields.Date(_('birthday'))


class property_management_report(models.Model):
    _name = 'admission.management.report'
    _rec_name = 'report_type'
    _inherit = ["mail.thread"]
    _order = "date desc"

    def get_default_company_id(self):
        return self.env['res.users'].browse([self.env.uid]).company_id.id

    date = fields.Date(_('Date'), default=date.today(), translate=True)
    date_from = fields.Date(_('Date From'), default=date.today(), translate=True)
    date_to = fields.Date(_('Date To'), translate=True)
    report_type = fields.Selection([('contract', _('Recruitment contract')),
                                    ('rent_contract', _('rent contract')),
                                    ('workers', _('workers'))], string='Report Type', default='contract')
    customer_id = fields.Many2one('res.partner', _('Customer'))
    contract_ids = fields.One2many('admission.report.line', 'report_id', string='Contracts')
    rent_contract_ids = fields.One2many('rent.report.line', 'report_id', string='rent Contracts')
    workers_ids = fields.One2many('availability.report.line', 'report_id', string='workers')

    total_cost = fields.Float('Total Cost')
    total_amount_contracts_with_vat = fields.Float('Total Amount with VAT')
    total_amount_of_VAT = fields.Float('VAT Amount')
    total_Paid = fields.Float('Total Paid')
    total_remain = fields.Float('total remain')
    worker_state = fields.Selection([('available', 'available'),
                                   ('not_available', 'Not available'), ('all', 'all')],default="all")
    installment_status = fields.Selection([('full_paid', _('سددت')),
                                           ('partial_paid', _('سددت جزئيا')),
                                           ('not_paid', _('لم تسدد')),
                                           ('all_option', _('كل الدفعات'))], _('بحث بحالة الدفع') ,default='all_option')
    company = fields.Many2one('res.company', 'Company', required=True,
                                 readonly=True, default=get_default_company_id,
                                 help="The Company for which the "
                                      "report is made to")

    def get_details(self):
        if self.contract_ids:
            for line in self.contract_ids:
                line.unlink()
            self.total_cost = 0.0
            self.total_amount_contracts_with_vat = 0.0
            self.total_amount_of_VAT = 0.0
            self.total_Paid = 0.0
            self.total_remain = 0.0
        
        if self.rent_contract_ids:
            for line in self.rent_contract_ids:
                line.unlink()
            self.total_cost = 0.0
            self.total_amount_contracts_with_vat = 0.0
            self.total_amount_of_VAT = 0.0
            self.total_Paid = 0.0
            self.total_remain = 0.0
        
        if self.workers_ids:
            for line in self.workers_ids:
                line.unlink()

        if self.report_type == 'contract':
            search_criteria = []
            contract_pool = self.env['admission.request']
            contract_line_pool = self.env['admission.report.line']

            if self.customer_id:
                search_criteria.append(('partner_id', '=', self.customer_id.id))

            if self.date_from and self.date_to:
                search_criteria.append(('contract_date', '>=', self.date_from))
                search_criteria.append(('contract_date', '<=', self.date_to))

            contract_ids = contract_pool.search(search_criteria)
            for contract in contract_ids:
                self.total_cost = self.total_cost + contract.total_cost
                self.total_amount_contracts_with_vat = self.total_amount_contracts_with_vat + contract.total_contract_with_vat
                self.total_amount_of_VAT = self.total_amount_of_VAT + contract.contract_vat_amount
                self.total_Paid = self.total_Paid  + contract.total_paid
                self.total_remain = self.total_remain + contract.total_remain

                vals = {
                    'partner_id': contract.partner_id.id,
                    'contract_no': contract.contract_no,
                    'contract_date': contract.contract_date,
                    'total_cost': contract.total_cost,
                    'total_contract_with_vat': contract.total_contract_with_vat,
                    'contract_vat_amount': contract.contract_vat_amount,
                    'total_paid': contract.total_paid,
                    'total_remain': contract.total_remain,
                    'discount': contract.discount,
                    'additions': contract.additions,
                    'state': contract.state,
                    'worker_inarabic': contract.worker_inarabic,
                    'responsible_id': contract.user_id.name,
                    'report_id': self.id,

                }

                status = ''
                line_state = ''
                if contract.total_paid <= 0.0:
                    status = _('لم تسدد')
                    line_state = 'not'
                elif contract.total_paid > 0.0 and contract.total_remain > 0.0:
                    status = _('سددت جزئيا')
                    line_state = 'partial'
                elif contract.total_paid > 0.0 and contract.total_remain == 0.0:
                    status = _('سددت')
                    line_state = 'paid'

                vals.update({
                    'status': status,
                    'line_state': line_state,
                })

                contract_line_pool.create(vals)

        elif self.report_type == 'rent_contract':
            search_criteria = []
            contract_pool = self.env['rent.workers.management']
            contract_line_pool = self.env['rent.report.line']

            if self.customer_id:
                search_criteria.append(('partner_id', '=', self.customer_id.id))

            if self.date_to and self.date_from:
                search_criteria.append(('contract_date_to', '>=', self.date_from))
                search_criteria.append(('contract_date_to', '<=', self.date_to))

            contract_ids = contract_pool.search(search_criteria)
            for contract in contract_ids:
                self.total_cost = self.total_cost + contract.total_cost
                self.total_amount_contracts_with_vat = self.total_amount_contracts_with_vat + contract.total_contract_with_vat
                self.total_amount_of_VAT = self.total_amount_of_VAT + contract.contract_vat_amount
                self.total_Paid = self.total_Paid  + contract.total_paid
                self.total_remain = self.total_remain + contract.total_remain

                vals = {
                    'partner_id': contract.partner_id.id,
                    'contract_no': contract.name,
                    'date_from': contract.contract_date_from, 
                    'date_to': contract.contract_date_to,
                    'total_cost': contract.total_cost,
                    'total_contract_with_vat': contract.total_contract_with_vat,
                    'contract_vat_amount': contract.contract_vat_amount,
                    'total_paid': contract.total_paid,
                    'total_remain': contract.total_remain,
                    'discount': contract.discount,
                    'additions': contract.additions,
                    'state': contract.state,
                    'employee_id': contract.employee_id.name,
                    'responsible_id': contract.user_id.name,
                    'report_id': self.id,

                }

                status = ''
                line_state = ''
                if contract.total_paid <= 0.0:
                    status = _('لم تسدد')
                    line_state = 'not'
                elif contract.total_paid > 0.0 and contract.total_remain > 0.0:
                    status = _('سددت جزئيا')
                    line_state = 'partial'
                elif contract.total_paid > 0.0 and contract.total_remain == 0.0:
                    status = _('سددت')
                    line_state = 'paid'

                vals.update({
                    'status': status,
                    'line_state': line_state,
                })

                contract_line_pool.create(vals)
        
        else:
            search_criteria = [] 
            employee_pool = self.env['hr.employee']
            employee_line_pool = self.env['availability.report.line']
            

            if self.worker_state == "available":
                search_criteria.append(('is_available', '=', True))
                search_criteria.append(('is_worker', '=', True))
                
            elif  self.worker_state == "not_available": 
                search_criteria.append(('is_available', '=', False))
                search_criteria.append(('is_worker', '=', True))

            else:
                search_criteria.append(('is_worker', '=', True))

            emp_ids = employee_pool.search(search_criteria)

            for emp in emp_ids:
                status = ''
                
                if emp.is_available == True:
                    status = _('متاح')
                elif emp.is_available != True:
                    status = _('غير متاح ')
                
                vals = {
                    'employee_id': emp.name,
                    'employee_nationality': emp.country_id.name,
                    'identification_id': emp.identification_id,
                    'passport_id': emp.passport_id,
                    'gender': emp.gender,
                    'birthday': emp.birthday,
                    'status': status,
                    'report_id': self.id,
                }
                employee_line_pool.create(vals)