# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, timedelta, datetime
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.osv import expression
import math


class AdmissionRequest(models.Model):
    _name = 'admission.request.setting'

    addmission_income_account_id = fields.Many2one('account.account', required=True, string='addmission income Account',
                                                   help="Default addmission income Account",
                                                   domain=[('user_type_id.internal_group', '=', 'income')])
    rent_income_account_id = fields.Many2one('account.account', required=True, string='rent income Account',
                                             help="Default rent income Account",
                                             domain=[('user_type_id.internal_group', '=', 'income')])
    insurance_account_id = fields.Many2one('account.account', required=True, string='insurance liability Account',
                                           help="Default rent income Account",
                                           domain=[('user_type_id.internal_group', '=', 'liability')])


class AdmissionDocument(models.Model):
    _name = 'admission.request.document'

    name = fields.Char(string='Document name', required=True)
    doc_id = fields.Many2one('admission.request', string='document')
    attach_ids = fields.Binary(_('upload Document'), required=True)
    binary_fname = fields.Char('Binary Name')
    doc_date = fields.Date(string='doc date', required=True, default=date.today())


class Assesstant(models.Model):
    _name = 'assesstant'

    assesstant_no = fields.Char(string='assesstant no')
    assesstant_date = fields.Date(string='assesstant date', default=date.today())
    assesstant_status = fields.Selection([('paid', 'Paid'), ('not_paid', 'Not Paid')])
    assesstant_profission = fields.Char(string='assesstant profission')
    assesstant_nationality = fields.Char(string='assesstant nationality')
    assesstant_religous = fields.Char(string='assesstant religous')
    assesstant_salary = fields.Char(string='assesstant salary')
    assesstant_period = fields.Char(string='assesstant period')
    assesstant_arrival_station = fields.Char(string='assesstant arrival station')
    assesstant_visa_no = fields.Char(string='assesstant visa no')
    assesstant_visa_date = fields.Date(string='assesstant visa date')
    assesstant_visa_cost = fields.Float(string='assesstant visa cost')
    assesstant_visa_fees = fields.Float(string='assesstant visa fees')
    assesstant_ahala = fields.Char(string='assesstant ahala')
    admission_request_id = fields.Many2one('admission.request', string='assesstant')


class HrEmployeeRent(models.Model):
    _inherit = "hr.employee"

    is_worker = fields.Boolean(string='Is worker')
    is_available = fields.Boolean(string='Is available', readonly=True)
    rent_contract_date_from = fields.Date(string='contract date from')
    rent_contract_date_to = fields.Date(string='contract date to')

    def write(self, vals):
        result = super(HrEmployeeRent, self).write(vals)
        if vals.get('is_worker'):
            self._cron_availabile_rent_workers()
        return result

    @api.model
    def create(self, vals):
        result = super(HrEmployeeRent, self).create(vals)
        if vals.get('is_worker'):
            self._cron_availabile_rent_workers()
        return result

    @api.model
    def _cron_availabile_rent_workers(self):
        employee_obj = self.env['hr.employee'].search([('is_worker', '=', True)])
        for emp in employee_obj:
            if emp.rent_contract_date_to:
                if emp.rent_contract_date_to < date.today():
                    emp.write({'rent_contract_date_from': False})
                    emp.write({'rent_contract_date_to': False})
                    emp.is_available = True
                else:
                    emp.write({'is_available': False})
            else:
                emp.write({'is_available': True})
        return True


class Partner(models.Model):
    _inherit = "res.partner"

    is_website_customer = fields.Boolean(string='Is Website Customer')


class CancelRentContract(models.Model):
    _name = 'rent.cancel'
    _inherit = ['mail.thread']
    _description = 'rent cancel'
    _order = 'create_date desc'

    contract_id = fields.Many2one('rent.workers.management', string='contract', required=True,
                                  domain=[('is_cancel', '=', False), ('state', '=', 'paid'),
                                          ('contract_date_to', '>', date.today())])
    name = fields.Char(string='Cancel Contract Reference', required=True, copy=False, readonly=True,
                       states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    user_id = fields.Many2one('res.users', string='reguest person', readonly=True,
                              states={'draft': [('readonly', False)]}, index=True, track_visibility='onchange',
                              track_sequence=2, default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True,
                                 related="contract_id.partner_id")
    invoice_id = fields.Many2one('account.move', string='invoice', readonly=True,
                                 related="contract_id.invoice_id")
    identification = fields.Char(string='identification', related="contract_id.identification")
    employee_id = fields.Many2one('hr.employee', related="contract_id.employee_id", readonly=True)
    employee_image = fields.Binary('employee Image', related="employee_id.image_1920", store=False, readonly=True)
    last_contract_date = fields.Date(string='last contract date', required=True, default=date.today())
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'verified'),
        ('done', 'Done'),
        ('invoiced', 'invoiced'),
        ('cancel', 'Rejected')], string='Status', index=True, readonly=True, copy=False, default='draft',
        track_visibility='onchange')
    contract_date_from = fields.Date(string='new contract date from', related="contract_id.contract_date_from")
    contract_date_to = fields.Date(string='new contract date to', related="contract_id.contract_date_to")
    paid_amount = fields.Float(string='paid amount', required=True)
    rent_days = fields.Integer(compute='_compute_rent_days_count', string='rent days')
    cancel_payment_id = fields.Many2one("account.payment", "cancel payment")

    def _compute_rent_days_count(self):
        if self.contract_date_from and self.contract_date_to:
            delta = self.contract_date_to - self.last_contract_date
            self.rent_days = delta.days
            paid_amount = self.contract_id.total_contract_with_vat / self.contract_id.rent_days
            if self.state == "draft":
                self.write({'paid_amount': self.rent_days * paid_amount})

    def action_verify(self):
        if self.paid_amount <= 0.0:
            raise UserError(_('Please Fill Cost amount field!! '))

        if self.last_contract_date <= self.contract_date_from:
            raise UserError(_('last contract date less than first contract date!! '))

        if self.last_contract_date > self.contract_date_to:
            raise UserError(_('last contract date grater than end contract date!! '))

        self.write({'state': 'verify'})

    def done(self):
        if self.paid_amount <= 0.0:
            raise UserError(_("amount equal zero !!"))

        self.contract_id.write({'contract_date_to': self.last_contract_date, 'is_cancel': True})
        self.employee_id.write({'rent_contract_date_to': self.last_contract_date})
        self.employee_id._cron_availabile_rent_workers()
        self.write({'state': 'done'})
        return True

    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'rent.cancel') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('rent.cancel') or _('New')

        result = super(CancelRentContract, self).create(vals)
        return result

    def unlink(self):
        if any(self.filtered(lambda reg: reg.state not in ('draft'))):
            raise ValidationError(_("You cannot delete any confirmed cancel order."))
        return super(CancelRentContract, self).unlink()


class RentWorkersManagement(models.Model):
    _name = 'rent.workers.management'
    _inherit = ['mail.thread']
    _description = 'rent workers'
    _order = 'create_date desc'

    def unlink(self):
        if any(self.filtered(lambda reg: reg.state not in ('draft'))):
            raise ValidationError(_("You cannot delete any confirmed cancel order."))
        return super(RentWorkersManagement, self).unlink()

    def action_verify(self):
        if self.total_cost <= 0.0:
            raise UserError(_('Please Fill Cost amount field!! '))
        self.partner_id.write({'ref': self.identification})
        self.write({'state': 'verify'})

    @api.constrains('contract_date_from', 'contract_date_to')
    def _check_wage(self):
        if self.contract_date_to < self.contract_date_from:
            raise ValidationError(_("date to less than date from !!"))

    def action_insurance_payment(self):
        global result
        account_payment_obj = self.env['account.payment']
        account_journal_obj = self.env['account.journal'].search([('type', 'in', ['bank', 'cash'])])[0]
        account_payment_method_obj = \
            self.env['account.payment.method'].search([('code', '=', 'electronic'), ('payment_type', '=', 'inbound')])[
                0]
        if self.insurance_amount <= 0.0:
            raise UserError(_("insurance amount equal zero !!"))
        if self.is_insurance_paid:
            raise UserError(_("insurance amount has been paid !!"))

        res = account_payment_obj.create({'partner_id': self.partner_id.id,
                                          'journal_id': account_journal_obj.id,
                                          'date': date.today(),
                                          'payment_type': 'inbound',
                                          'partner_type': 'customer',
                                          'rent_contract_id': self.id,
                                          'is_insurance': True,
                                          'amount': self.insurance_amount,
                                          'payment_method_id': account_payment_method_obj.id,
                                          'ref': self.name,
                                          })
        self.write({'is_insurance_paid': True, 'insurance_payment_id': res.id})

        if res:
            imd = self.env['ir.model.data']
            action = imd.xmlid_to_object('account.action_account_payments')
            list_view_id = imd.xmlid_to_res_id('account.view_account_payment_form')
            result = {
                'name': action.name,
                'help': action.help,
                'type': action.type,
                'views': [[list_view_id, 'form']],
                'target': action.target,
                'context': action.context,
                'res_model': action.res_model,
                'res_id': res.id,
            }
            if res:
                result['domain'] = "[('id','=',%s)]" % res.id

        return result

    def action_confirm(self):
        account_payment_obj = self.env['account.payment']
        employee_obj = self.env['hr.employee'].search([('id', '=', self.employee_id.id)])
        account_journal_obj = self.env['account.journal'].search([('type', 'in', ['bank', 'cash'])])[0]
        account_payment_method_obj = \
            self.env['account.payment.method'].search([('code', '=', 'electronic'), ('payment_type', '=', 'inbound')])[
                0]
        if self.total_remain == 0.0:
            employee_obj.write({'rent_contract_date_from': self.contract_date_from,
                                'rent_contract_date_to': self.contract_date_to, })
            Warning(_("remain amount equal zero !!"))
        if (self.total_paid + self.total_remain) > self.total_contract_with_vat:
            raise UserError(_("paid amount greater than remainning amount !!"))

        res = account_payment_obj.create({'partner_id': self.partner_id.id,
                                          'journal_id': account_journal_obj.id,
                                          'date': date.today(),
                                          'payment_type': 'inbound',
                                          'partner_type': 'customer',
                                          'rent_contract_id': self.id,
                                          'amount': self.total_remain,
                                          'payment_method_id': account_payment_method_obj.id,
                                          'ref': self.name,
                                          })
        employee_obj.write({'rent_contract_date_from': self.contract_date_from,
                            'rent_contract_date_to': self.contract_date_to, })
        employee_obj._cron_availabile_rent_workers()

        if res:
            imd = self.env['ir.model.data']
            action = imd.xmlid_to_object('account.action_account_payments')
            list_view_id = imd.xmlid_to_res_id('account.view_account_payment_form')
            result = {
                'name': action.name,
                'help': action.help,
                'type': action.type,
                'views': [[list_view_id, 'form']],
                'target': action.target,
                'context': action.context,
                'res_model': action.res_model,
                'res_id': res.id,
            }
            if res:
                result['domain'] = "[('id','=',%s)]" % res.id

        return result

    def action_unlock(self):
        self.write({'state': 'draft'})

    def action_cancel(self):
        if self.invoice_id:
            if self.invoice_id.state == 'draft':
                self.invoice_id.write({'state': 'cancel'})
                self.write({'state': 'cancel'})
            else:
                account_invoice_obj = self.env['account.move'].search(
                    [('id', '=', self.invoice_id.id), ('ref', '=', self.invoice_id.name)])
                if not account_invoice_obj:
                    raise UserError(_('Please make Credit Note for this invoice !'))
                else:
                    self.write({'state': 'cancel'})
        else:
            self.write({'state': 'cancel'})

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'rent.workers.management') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('rent.workers.management') or _('New')

        result = super(RentWorkersManagement, self).create(vals)
        return result

    def write(self, vals):
        if vals.get('state'):
            for rec in self:
                tax_amount = rec.vat_id.compute_all(rec.total_cost - rec.discount + rec.additions)
                rec.total_contract_with_vat = math.ceil(tax_amount['total_included'])
                rec.contract_vat_amount = abs(math.ceil(rec.total_contract_with_vat - rec.contract_net_amount))

        result = super(RentWorkersManagement, self).write(vals)
        return result

    @api.depends('discount', 'additions', 'vat_id', 'total_cost')
    def cal_total_amount_with_vat(self):
        for order in self:
            tax_amount = order.vat_id.compute_all(order.total_cost - order.discount + order.additions)
            if tax_amount['total_included'] == 0.00:
                order.total_contract_with_vat = order.total_cost
            else:
                order.total_contract_with_vat = math.ceil(tax_amount['total_included'])
                order.contract_vat_amount = abs(math.ceil(order.total_contract_with_vat - order.contract_net_amount))

    @api.depends('total_contract_with_vat', 'total_cost', 'contract_vat_amount', 'vat_id')
    def cal_paid_remain(self):
        account_payment_obj = self.env['account.payment']
        for order in self:
            amount = 0.0
            for payments in account_payment_obj.search(
                    [('rent_contract_id', '=', order.id), ('is_insurance', '=', False)]):
                amount = amount + payments.amount

            order.total_paid = amount
            order.total_remain = order.total_contract_with_vat - amount


    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        domain = args or []
        domain = expression.AND([domain, ['|', '|', ('name', operator, name), ('partner_id.name', operator, name),
                                          ('employee_id.name', operator, name)]])
        rec = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(rec).name_get()

    name = fields.Char(string='Rent Contract Reference', required=True, copy=False, readonly=True,
                       states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    user_id = fields.Many2one('res.users', string='reguest person', readonly=True,
                              states={'draft': [('readonly', False)]}, index=True, track_visibility='onchange',
                              track_sequence=2, default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True,
                                 states={'draft': [('readonly', False)]}, required=True,
                                 change_default=True, index=True, track_visibility='always', track_sequence=1,
                                 help="You can find a customer by its Name, TIN, Email or Internal Reference.")
    identification = fields.Char(string='identification', required=True)
    employee_id = fields.Many2one('hr.employee', required=True, domain=[('is_available', '=', True)])
    employee_image = fields.Binary('employee Image', related="employee_id.image_1920", store=False, readonly=True)
    contract_date = fields.Date(string='contract date', required=True, default=date.today())
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'verified'),
        ('done', 'Done'),
        ('paid', 'Paid'),
        ('cancel', 'Rejected')], string='Status', index=True, readonly=True, copy=False, default='draft',
        track_visibility='onchange')
    contract_date_from = fields.Date(string='contract date from', required=True, default=date.today())
    contract_date_to = fields.Date(string='contract date to', required=True)
    total_cost = fields.Float(string='total Cost', required=True)
    insurance_amount = fields.Float(string='insurance amount')
    days_remain = fields.Integer(string='days remain', compute="cal_days_remain", )
    total_paid = fields.Float(string='total paid', compute="cal_paid_remain", store=True)
    total_remain = fields.Float(string='total remaining', compute="cal_paid_remain", store=True)
    discount = fields.Float(string='discount', required=True)
    additions = fields.Float(string='additions', required=True)
    vat_id = fields.Many2one("account.tax", "VAT", required=True,
                             default=lambda self: self.env['account.tax'].search([('type_tax_use', "=", "sale")]))
    total_contract_with_vat = fields.Float("Total contract Amount With VAT", compute="cal_total_amount_with_vat",
                                           store=True)
    contract_vat_amount = fields.Float("contract Vat", compute="cal_total_amount_with_vat", store=True)
    contract_net_amount = fields.Float("contract Net Amount", compute="cal_contract_net_amount", store=True)
    is_invoiced = fields.Boolean(copy=False, default=False)
    invoice_id = fields.Many2one("account.move", "invoice")
    insurance_payment_id = fields.Many2one("account.payment", "insurance payment")
    note = fields.Text(string='Internal Notes')
    payments_count = fields.Integer(compute='_compute_payments_count', string='Payments Count')
    is_from_website = fields.Boolean(string='from website ?', copy=False, default=False)
    rent_days = fields.Integer(compute='_compute_rent_days_count', string='rent days')
    is_cancel = fields.Boolean(string='is cancel ?', copy=False, default=False)
    is_insurance_paid = fields.Boolean(string='is insurance paid ?', copy=False, default=False)

    def action_invoice(self):
        # try:
            account_obj = self.env['admission.request.setting'].search([])[0]
            account_invoice_obj = self.env['account.move']
            account_invoice_line_obj = self.env['account.move.line']

            rent_req = self
            if rent_req.is_invoiced == True:
                raise UserError(_(' Invoice is Already Exist'))

            tax_account_obj = self.env['account.tax.repartition.line'].search(
                [('tax_id.type_tax_use', '=', 'sale'), ('repartition_type', '=', 'tax')])[0]

            if not tax_account_obj:
                raise UserError(_('Tax Account is not set !!!'))

            if not account_obj:
                raise UserError(_('Please configure admission income Account  !'))

            action = self.env.ref('account.action_move_out_invoice_type')
            result = action.read()[0]

            # override the context to get rid of the default filtering
            # rent_contract_id
            mov_line_credit = {
                'move_name': self.name,
                'debit': 0.0,
                'credit': self.contract_net_amount,
                'date': date.today(),
                'partner_id': self.partner_id.id,
                'product_id': False,
                'account_id': account_obj.rent_income_account_id.id,
                'name': self.name,
                'tax_ids': [(6, 0, self.vat_id.ids)],
                'quantity': 1,
                'price_unit': float(self.contract_net_amount)}

            mov_line_credit_tax = {
                'move_name': self.name,
                'debit': 0.0,
                'credit': self.contract_vat_amount,
                'date': date.today(),
                'partner_id': self.partner_id.id,
                'tax_repartition_line_id': tax_account_obj.id,
                'tax_line_id': self.vat_id.id,
                'tax_base_amount': self.contract_net_amount,
                'product_id': False,
                'account_id': tax_account_obj.account_id.id,
                'name': self.name,
                'exclude_from_invoice_tab': True,
                'quantity': 1,
                'price_unit': float(self.contract_vat_amount)}

            mov_line_debit = {
                'move_name': self.name,
                'debit': self.total_contract_with_vat,
                'credit': 0.0,
                'date': date.today(),
                'partner_id': self.partner_id.id,
                'product_id': False,
                'account_id': self.partner_id.property_account_receivable_id.id,
                'name': self.name,
                'exclude_from_invoice_tab': True,
                'quantity': 1,
                'price_unit': float(self.total_contract_with_vat)}

            invoice_vals = account_invoice_obj.create({
                'ref': self.name or '',
                'move_type': 'out_invoice',
                'invoice_user_id': self.user_id and self.user_id.id,
                'partner_id': self.partner_id.id,
                'invoice_origin': self.name,
                'rent_contract_id': self.id,
                'invoice_date': date.today(),
                'line_ids': [(0, 0, mov_line_credit), (0, 0, mov_line_credit_tax), (0, 0, mov_line_debit)],
                'state': 'draft',
            })
            invoice_vals._compute_amount()
            self.write({'state': 'done', 'invoice_id': invoice_vals.id})
        # except:
        #     pass




    def _compute_rent_days_count(self):
        if self.contract_date_from and self.contract_date_to:
            delta = self.contract_date_to - self.contract_date_from
            self.rent_days = delta.days

    def cal_days_remain(self):
        for rec in self:
            if rec.contract_date_from and rec.contract_date_to:
                today = date.today()
                if rec.contract_date_from > today:
                    rec.days_remain = 0
                elif today <= rec.contract_date_to:
                    delta = rec.contract_date_to - today
                    rec.days_remain = delta.days
                else:
                    rec.days_remain = 0

    def _compute_payments_count(self):
        # read_group as sudo, since contract count is displayed on form view
        payments_data = self.env['account.payment'].sudo().read_group([('rent_contract_id', 'in', self.ids)],
                                                                      ['rent_contract_id'], ['rent_contract_id'])
        result = dict((data['rent_contract_id'][0], data['rent_contract_id_count']) for data in payments_data)
        for rent in self:
            rent.payments_count = result.get(rent.id, 0)

    @api.depends('total_cost', 'discount', 'additions', 'vat_id')
    def cal_contract_net_amount(self):
        for item in self:
            item.contract_net_amount = (item.total_cost + item.additions) - item.discount


class AccountInvoiceAdmission(models.Model):
    _inherit = "account.move"

    admission_request_id = fields.Many2one('admission.request', string='admission')
    rent_contract_id = fields.Many2one('rent.workers.management', string='Rent contract')


class AdmissionManagementRequest(models.Model):
    _name = 'admission.request'
    _inherit = ['mail.thread']
    _description = 'admission request'
    _order = 'create_date desc'

    def unlink(self):
        if any(self.filtered(lambda reg: reg.state not in ('draft'))):
            raise ValidationError(_("You cannot delete any confirmed cancel order."))
        return super(AdmissionManagementRequest, self).unlink()

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        domain = args or []
        domain = expression.AND([domain, ['|', '|', ('name', operator, name), ('partner_id.name', operator, name),
                                          ('partner_id.mobile', operator, name)]])
        rec = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(rec).name_get()

    def action_verify(self):
        if self.total_cost <= 0.0:
            raise UserError(_('Please Fill Cost amount field!! '))

        payment_obj = self.env['account.payment'].search([('admission_request_id', '=', self.id)])
        if payment_obj:
            for rec in payment_obj:
                if rec.state != 'cancelled':
                    raise UserError(_('there are payments for this contract!! '))

        self.partner_id.write({'ref': self.identification})
        self.contract_no = self.env['ir.sequence'].next_by_code('admission.contracts') or _('New')
        self.write({'state': 'verify'})

    def action_confirm(self):
        account_payment_obj = self.env['account.payment']
        account_journal_obj = self.env['account.journal'].search([('type', 'in', ['bank', 'cash'])])[0]
        account_payment_method_obj = \
        self.env['account.payment.method'].search([('code', '=', 'electronic'), ('payment_type', '=', 'inbound')])[0]
        if self.total_remain == 0.0:
            raise UserError(_("remain amount equal zero !!"))
        if (self.total_paid + self.total_remain) > self.total_contract_with_vat:
            raise UserError(_("paid amount greater than remainning amount !!"))

        res = account_payment_obj.create({'partner_id': self.partner_id.id,
                                          'journal_id': account_journal_obj.id,
                                          'date': date.today(),
                                          'payment_type': 'inbound',
                                          'partner_type': 'customer',
                                          'admission_request_id': self.id,
                                          'amount': self.total_remain,
                                          'payment_method_id': account_payment_method_obj.id,
                                          'ref': self.contract_no,
                                          })
        if res:
            imd = self.env['ir.model.data']
            action = imd.xmlid_to_object('account.action_account_payments')
            list_view_id = imd.xmlid_to_res_id('account.view_account_payment_form')
            result = {
                'name': action.name,
                'help': action.help,
                'type': action.type,
                'views': [[list_view_id, 'form']],
                'target': action.target,
                'context': action.context,
                'res_model': action.res_model,
                'res_id': res.id,
            }
            if res:
                result['domain'] = "[('id','=',%s)]" % res.id

        return result

    def action_unlock(self):
        self.write({'state': 'draft'})

    def action_cancel(self):
        payment_obj = self.env['account.payment'].search([('admission_request_id', '=', self.id)])
        if payment_obj:
            for rec in payment_obj:
                if rec.state == 'draft':
                    rec.cancel()
                    self.write({'state': 'cancel'})
                else:
                    rec.cancel()

        if self.invoice_id:
            if self.invoice_id.state == 'draft':
                self.invoice_id.write({'state': 'cancel'})
                self.write({'state': 'cancel'})
            else:
                account_invoice_obj = self.env['account.move'].search(
                    [('id', '=', self.invoice_id.id), ('ref', '=', self.invoice_id.name)])
                if not account_invoice_obj:
                    raise UserError(_('Please make Credit Note for this invoice !'))
                else:
                    self.write({'state': 'cancel'})
        else:
            self.write({'state': 'cancel'})

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'admission.request') or _('New')
                vals['contract_no'] = _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('admission.request') or _('New')
                vals['contract_no'] = _('New')

        result = super(AdmissionManagementRequest, self).create(vals)
        return result

    def write(self, vals):
        if vals.get('state'):
            for rec in self:
                tax_amount = rec.vat_id.compute_all(rec.total_cost - rec.discount + rec.additions)
                rec.total_contract_with_vat = math.ceil(tax_amount['total_included'])
                rec.contract_vat_amount = abs(math.ceil(rec.total_contract_with_vat - rec.contract_net_amount))

        result = super(AdmissionManagementRequest, self).write(vals)
        return result

    @api.depends('discount', 'additions', 'vat_id', 'total_cost')
    def cal_total_amount_with_vat(self):
        for order in self:
            tax_amount = order.vat_id.compute_all(order.total_cost - order.discount + order.additions)
            if tax_amount['total_included'] == 0.00:
                order.total_contract_with_vat = order.total_cost
            else:
                order.total_contract_with_vat = math.ceil(tax_amount['total_included'])
                order.contract_vat_amount = abs(math.ceil(order.total_contract_with_vat - order.contract_net_amount))

    @api.depends('discount', 'additions', 'total_contract_with_vat', 'contract_vat_amount', 'vat_id')
    def cal_paid_remain(self):
        account_payment_obj = self.env['account.payment']

        for order in self:
            amount = 0.0
            for payments in account_payment_obj.search([('admission_request_id', '=', order.id)]):
                amount = amount + payments.amount

            order.total_paid = amount
            order.total_remain = order.total_contract_with_vat - amount

    def action_done(self):
        account_obj = self.env['admission.request.setting'].search([])[0]
        account_invoice_obj = self.env['account.move']
        account_invoice_line_obj = self.env['account.move.line']

        rent_req = self
        if rent_req.is_invoiced == True:
            raise UserError(_(' Invoice is Already Exist'))

        tax_account_obj = self.env['account.tax.repartition.line'].search(
            [('tax_id.type_tax_use', '=', 'sale'), ('repartition_type', '=', 'tax')])[0]

        if not tax_account_obj:
            raise UserError(_('Tax Account is not set !!!'))

        if not account_obj:
            raise UserError(_('Please configure admission income Account  !'))

        action = self.env.ref('account.action_move_out_invoice_type')
        result = action.read()[0]

        # override the context to get rid of the default filtering
        # admission_id

        mov_line_credit = {
            'move_name': self.name,
            'debit': 0.0,
            'credit': self.contract_net_amount,
            'date': date.today(),
            'partner_id': self.partner_id.id,
            'product_id': False,
            'account_id': account_obj.addmission_income_account_id.id,
            'name': self.name,
            'tax_ids': [(6, 0, self.vat_id.ids)],
            'quantity': 1,
            'price_unit': float(self.contract_net_amount)}

        mov_line_credit_tax = {
            'move_name': self.name,
            'debit': 0.0,
            'credit': self.contract_vat_amount,
            'date': date.today(),
            'partner_id': self.partner_id.id,
            'product_id': False,
            'account_id': tax_account_obj.account_id.id,
            'tax_repartition_line_id': tax_account_obj.id,
            'tax_line_id': self.vat_id.id,
            'tax_base_amount': self.contract_net_amount,
            'name': self.name,
            'exclude_from_invoice_tab': True,
            'quantity': 1,
            'price_unit': float(self.contract_vat_amount)}

        mov_line_debit = {
            'move_name': self.name,
            'debit': self.total_contract_with_vat,
            'credit': 0.0,
            'date': date.today(),
            'partner_id': self.partner_id.id,
            'product_id': False,
            'account_id': self.partner_id.property_account_receivable_id.id,
            'name': self.name,
            'exclude_from_invoice_tab': True,
            'quantity': 1,
            'price_unit': float(self.total_contract_with_vat)}

        invoice_vals = account_invoice_obj.create({
            'ref': self.name or '',
            'type': 'out_invoice',
            'invoice_user_id': self.user_id and self.user_id.id,
            'partner_id': self.partner_id.id,
            'invoice_origin': self.name,
            'admission_request_id': self.id,
            'invoice_date': date.today(),
            'line_ids': [(0, 0, mov_line_credit), (0, 0, mov_line_credit_tax), (0, 0, mov_line_debit)],
            'state': 'draft',
        })
        self.write({'state': 'done', 'invoice_id': invoice_vals.id})

        return True

    name = fields.Char(string='Request Reference', required=True, copy=False, readonly=True,
                       states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    user_id = fields.Many2one('res.users', string='reguest person', readonly=True,
                              states={'draft': [('readonly', False)]}, index=True, track_visibility='onchange',
                              track_sequence=2, default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True,
                                 states={'draft': [('readonly', False)]}, required=True,
                                 change_default=True, index=True, track_visibility='always', track_sequence=1,
                                 help="You can find a customer by its Name, TIN, Email or Internal Reference.")
    identification = fields.Char(string='identification', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'verified'),
        ('confirm', 'Confirm'),
        ('done', 'Done'),
        ('paid', 'Paid'),
        ('cancel', 'Rejected')], string='Status', index=True, readonly=True, copy=False, default='draft',
        track_visibility='onchange')

    contract_no = fields.Char(string='contract no', required=True, default=lambda self: _('New'))
    contract_date = fields.Date(string='contract date', required=True, default=date.today())
    number_of_days = fields.Integer(string='number of days', required=True)
    arrival_date = fields.Date(string='arrival date', compute="_compute_arrival_date", store=True)
    total_cost = fields.Float(string='total Cost', required=True)
    total_paid = fields.Float(string='total paid', compute="cal_paid_remain", store=True)
    total_remain = fields.Float(string='total remaining', compute="cal_paid_remain", store=True)
    discount = fields.Float(string='discount', required=True)
    additions = fields.Float(string='additions', required=True)
    vat_id = fields.Many2one("account.tax", "VAT", required=True,
                             default=lambda self: self.env['account.tax'].search([('type_tax_use', "=", "sale")]))
    total_contract_with_vat = fields.Float("Total contract Amount With VAT", compute="cal_total_amount_with_vat",
                                           store=True)
    contract_vat_amount = fields.Float("contract Vat", compute="cal_total_amount_with_vat", store=True)
    contract_net_amount = fields.Float("contract Net Amount", compute="cal_contract_net_amount", store=True)
    is_invoiced = fields.Boolean(copy=False, default=False)
    invoice_id = fields.Many2one("account.move", "invoice")
    worker_inarabic = fields.Char(string='worker in arabic')
    worker_inenglish = fields.Char(string='worker in english')
    is_worker_sent = fields.Selection([('sent', 'Sent'), ('not_yet', 'Not Yet')])
    mission_date = fields.Date(string='mission date')
    mission_no = fields.Char(string='mission no')
    agent_id = fields.Many2one('res.partner', string='agent')
    docs = fields.One2many('admission.request.document', 'doc_id', string='Documents')
    assesstant_ids = fields.One2many('assesstant', 'admission_request_id', string='assesstant')
    payments_count = fields.Integer(compute='_compute_payments_count', string='Payments Count')

    def _compute_payments_count(self):
        # read_group as sudo, since contract count is displayed on form view
        payments_data = self.env['account.payment'].sudo().read_group([('admission_request_id', 'in', self.ids)],
                                                                      ['admission_request_id'],
                                                                      ['admission_request_id'])
        result = dict((data['admission_request_id'][0], data['admission_request_id_count']) for data in payments_data)
        for rent in self:
            rent.payments_count = result.get(rent.id, 0)

    @api.depends('total_cost', 'discount', 'additions', 'vat_id')
    def cal_contract_net_amount(self):
        for item in self:
            item.contract_net_amount = (item.total_cost + item.additions) - item.discount

    @api.depends('number_of_days', 'contract_date')
    def _compute_arrival_date(self):
        start = str(self.contract_date).split(' ')[0]
        date_1 = datetime.strptime(start, '%Y-%m-%d')
        end_date = date_1 + timedelta(days=self.number_of_days)
        self.arrival_date = str(end_date).split(' ')[0]


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    admission_request_id = fields.Many2one('admission.request', string='admission')
    rent_contract_id = fields.Many2one('rent.workers.management', string='rent contract')
    is_insurance = fields.Boolean(string='is insurance')

    def action_validate_invoice_payment(self):
        """ Posts a payment used to pay an invoice. This function only posts the
        payment by default but can be overridden to apply specific post or pre-processing.
        It is called by the "validate" button of the popup window
        triggered on invoice form by the "Register Payment" button.
        """

        if self.invoice_ids.rent_contract_id.id:
            employee_obj = self.env['hr.employee'].search(
                [('id', '=', self.invoice_ids.rent_contract_id.employee_id.id)])
            if self.invoice_ids.rent_contract_id.total_remain == 0.0:
                raise UserError(_("remain amount equal zero !!"))
            if (
                    self.invoice_ids.rent_contract_id.total_paid + self.invoice_ids.rent_contract_id.total_remain) > self.invoice_ids.rent_contract_id.total_contract_with_vat:
                raise UserError(_("paid amount greater than remainning amount !!"))

            employee_obj.write({'rent_contract_date_from': self.invoice_ids.rent_contract_id.contract_date_from,
                                'rent_contract_date_to': self.invoice_ids.rent_contract_id.contract_date_to, })
            employee_obj._cron_availabile_rent_workers()
            self.write({'rent_contract_id': self.invoice_ids.rent_contract_id.id})

        if any(len(record.invoice_ids) != 1 for record in self):
            # For multiple invoices, there is account.register.payments wizard
            raise UserError(_("This method should only be called to process a single invoice's payment."))
        return self.post()

    def post(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconcilable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconcilable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        AccountMove = self.env['account.move'].with_context(default_type='entry')
        for rec in self:
            if rec.admission_request_id:
                admission_request_obj = self.env['admission.request'].search([('id', '=', rec.admission_request_id.id)])
                if admission_request_obj.total_remain == 0.0:
                    raise UserError(_("remain amount equal zero !!"))
                if (admission_request_obj.total_paid + rec.amount) > admission_request_obj.total_contract_with_vat:
                    raise UserError(_("paid amount greater than contract amount !!"))

                admission_request_obj.write({'total_paid': admission_request_obj.total_paid + rec.amount})
                admission_request_obj.write(
                    {'total_remain': admission_request_obj.total_contract_with_vat - admission_request_obj.total_paid})
                if admission_request_obj.total_remain == 0.0:
                    admission_request_obj.write({'state': 'confirm'})

            if rec.rent_contract_id and not rec.is_insurance:
                rent_contract_obj = self.env['rent.workers.management'].search([('id', '=', rec.rent_contract_id.id)])
                if rent_contract_obj.total_remain == 0.0:
                    raise UserError(_("remain amount equal zero !!"))
                if (rent_contract_obj.total_paid + rec.amount) > rent_contract_obj.total_contract_with_vat:
                    raise UserError(_("paid amount greater than remainning amount !!"))

                rent_contract_obj.write({'total_paid': rent_contract_obj.total_paid + rec.amount})
                rent_contract_obj.write(
                    {'total_remain': rent_contract_obj.total_contract_with_vat - rent_contract_obj.total_paid})
                if rent_contract_obj.total_remain == 0.0:
                    rent_contract_obj.write({'state': 'paid'})

            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted."))

            if any(inv.state != 'posted' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # keep the name in case of a payment reset to draft
            if not rec.name:
                # Use the right sequence to set the name
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'
                rec.name = self.env['ir.sequence'].next_by_code(sequence_code, sequence_date=rec.date)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            moves = AccountMove.create(rec._prepare_payment_moves())
            moves.filtered(lambda move: move.journal_id.post_at != 'bank_rec').post()

            # Update the state / move before performing any reconciliation.
            move_name = self._get_move_name_transfer_separator().join(moves.mapped('name'))
            rec.write({'state': 'posted', 'move_name': move_name})

            if rec.payment_type in ('inbound', 'outbound'):
                # ==== 'inbound' / 'outbound' ====
                if rec.invoice_ids:
                    (moves[0] + rec.invoice_ids).line_ids \
                        .filtered(lambda line: not line.reconciled and line.account_id == rec.destination_account_id) \
                        .reconcile()
            elif rec.payment_type == 'transfer':
                # ==== 'transfer' ====
                moves.mapped('line_ids') \
                    .filtered(lambda line: line.account_id == rec.company_id.transfer_account_id) \
                    .reconcile()

            if rec.is_insurance and rec.rent_contract_id:
                account_obj = self.env['admission.request.setting'].search([])[0]
                if not account_obj:
                    raise UserError(_('Please configure insurance liability Account  !'))
                for line in moves.line_ids:
                    if line.credit:
                        line.with_context(check_move_validity=False).write(
                            {'account_id': account_obj.insurance_account_id.id})
                        moves.post()

            if rec.admission_request_id:
                move_line_obj = self.env['account.move.line']
                tax_account_obj = self.env['account.tax.repartition.line'].search(
                    [('tax_id.type_tax_use', '=', 'sale'), ('repartition_type', '=', 'tax')])[0]
                if not tax_account_obj:
                    raise UserError(_("fill sales tax in accouning with correct data"))
                for line in moves.line_ids:
                    if line.credit:
                        if rec.amount == rec.admission_request_id.total_contract_with_vat:
                            tax_amount = rec.admission_request_id.contract_vat_amount
                            line.with_context(
                                check_move_validity=False).write({'credit': line.credit})

                            moves.post()
                        elif rec.amount < rec.admission_request_id.total_contract_with_vat:
                            new_credit = math.ceil(rec.amount / (rec.admission_request_id.vat_id.amount / 100 + 1))
                            tax_amount = rec.amount - new_credit

                            line.with_context(
                                check_move_validity=False).write({'credit': new_credit})

                            moves.post()
                        elif rec.amount > rec.admission_request_id.total_contract_with_vat:
                            raise UserError(
                                _("amount grater than contract total amount %s" % rec.admission_request_id.total_contract_with_vat))

        return True

    def _prepare_payment_moves(self):
        ''' Prepare the creation of journal entries (account.move) by creating a list of python dictionary to be passed
        to the 'create' method.

        Example 1: outbound with write-off:

        Account             | Debit     | Credit
        ---------------------------------------------------------
        BANK                |   900.0   |
        RECEIVABLE          |           |   1000.0
        WRITE-OFF ACCOUNT   |   100.0   |

        Example 2: internal transfer from BANK to CASH:

        Account             | Debit     | Credit
        ---------------------------------------------------------
        BANK                |           |   1000.0
        TRANSFER            |   1000.0  |
        CASH                |   1000.0  |
        TRANSFER            |           |   1000.0

        :return: A list of Python dictionary to be passed to env['account.move'].create.
        '''
        all_move_vals = []
        for payment in self:
            company_currency = payment.company_id.currency_id
            move_names = payment.move_name.split(
                payment._get_move_name_transfer_separator()) if payment.move_name else None

            # Compute amounts.
            write_off_amount = payment.payment_difference_handling == 'reconcile' and -payment.payment_difference or 0.0
            if payment.payment_type in ('outbound', 'transfer'):
                counterpart_amount = payment.amount
                liquidity_line_account = payment.journal_id.default_debit_account_id
            else:
                counterpart_amount = -payment.amount
                liquidity_line_account = payment.journal_id.default_credit_account_id

            # Manage currency.
            if payment.currency_id == company_currency:
                # Single-currency.
                balance = counterpart_amount
                write_off_balance = write_off_amount
                counterpart_amount = write_off_amount = 0.0
                currency_id = False
            else:
                # Multi-currencies.
                balance = payment.currency_id._convert(counterpart_amount, company_currency, payment.company_id,
                                                       payment.date)
                write_off_balance = payment.currency_id._convert(write_off_amount, company_currency, payment.company_id,
                                                                 payment.date)
                currency_id = payment.currency_id.id

            # Manage custom currency on journal for liquidity line.
            if payment.journal_id.currency_id and payment.currency_id != payment.journal_id.currency_id:
                # Custom currency on journal.
                if payment.journal_id.currency_id == company_currency:
                    # Single-currency
                    liquidity_line_currency_id = False
                else:
                    liquidity_line_currency_id = payment.journal_id.currency_id.id
                liquidity_amount = company_currency._convert(
                    balance, payment.journal_id.currency_id, payment.company_id, payment.date)
            else:
                # Use the payment currency.
                liquidity_line_currency_id = currency_id
                liquidity_amount = counterpart_amount

            # Compute 'name' to be used in receivable/payable line.
            rec_pay_line_name = ''
            if payment.payment_type == 'transfer':
                rec_pay_line_name = payment.name
            else:
                if payment.partner_type == 'customer':
                    if payment.payment_type == 'inbound':
                        rec_pay_line_name += _("Customer Payment")
                    elif payment.payment_type == 'outbound':
                        rec_pay_line_name += _("Customer Credit Note")
                elif payment.partner_type == 'supplier':
                    if payment.payment_type == 'inbound':
                        rec_pay_line_name += _("Vendor Credit Note")
                    elif payment.payment_type == 'outbound':
                        rec_pay_line_name += _("Vendor Payment")
                if payment.invoice_ids:
                    rec_pay_line_name += ': %s' % ', '.join(payment.invoice_ids.mapped('name'))

            # Compute 'name' to be used in liquidity line.
            if payment.payment_type == 'transfer':
                liquidity_line_name = _('Transfer to %s') % payment.destination_journal_id.name
            else:
                liquidity_line_name = payment.name

            # ==== 'inbound' / 'outbound' ====

            move_vals = {
                'date': payment.date,
                'ref': payment.ref,
                'journal_id': payment.journal_id.id,
                'currency_id': payment.journal_id.currency_id.id or payment.company_id.currency_id.id,
                'partner_id': payment.partner_id.id,
                'line_ids': [
                    # Receivable / Payable / Transfer line.
                    (0, 0, {
                        'name': rec_pay_line_name,
                        'amount_currency': counterpart_amount + write_off_amount if currency_id else 0.0,
                        'currency_id': currency_id,
                        'debit': balance + write_off_balance > 0.0 and balance + write_off_balance or 0.0,
                        'credit': balance + write_off_balance < 0.0 and -balance - write_off_balance or 0.0,
                        'date_maturity': payment.date,
                        'partner_id': payment.partner_id.commercial_partner_id.id,
                        'account_id': payment.destination_account_id.id,
                        'payment_id': payment.id,
                    }),
                    # Liquidity line.
                    (0, 0, {
                        'name': liquidity_line_name,
                        'amount_currency': -liquidity_amount if liquidity_line_currency_id else 0.0,
                        'currency_id': liquidity_line_currency_id,
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                        'date_maturity': payment.date,
                        'partner_id': payment.partner_id.commercial_partner_id.id,
                        'account_id': liquidity_line_account.id,
                        'payment_id': payment.id,
                    }),
                ],
            }
            if write_off_balance:
                # Write-off line.
                move_vals['line_ids'].append((0, 0, {
                    'name': payment.writeoff_label,
                    'amount_currency': -write_off_amount,
                    'currency_id': currency_id,
                    'debit': write_off_balance < 0.0 and -write_off_balance or 0.0,
                    'credit': write_off_balance > 0.0 and write_off_balance or 0.0,
                    'date_maturity': payment.date,
                    'partner_id': payment.partner_id.commercial_partner_id.id,
                    'account_id': payment.writeoff_account_id.id,
                    'payment_id': payment.id,
                }))

            if move_names:
                move_vals['name'] = move_names[0]

            all_move_vals.append(move_vals)

            # ==== 'transfer' ====
            if payment.payment_type == 'transfer':
                journal = payment.destination_journal_id

                # Manage custom currency on journal for liquidity line.
                if journal.currency_id and payment.currency_id != journal.currency_id:
                    # Custom currency on journal.
                    liquidity_line_currency_id = journal.currency_id.id
                    transfer_amount = company_currency._convert(balance, journal.currency_id, payment.company_id,
                                                                payment.date)
                else:
                    # Use the payment currency.
                    liquidity_line_currency_id = currency_id
                    transfer_amount = counterpart_amount

                transfer_move_vals = {
                    'date': payment.date,
                    'ref': payment.ref,
                    'partner_id': payment.partner_id.id,
                    'journal_id': payment.destination_journal_id.id,
                    'line_ids': [
                        # Transfer debit line.
                        (0, 0, {
                            'name': payment.name,
                            'amount_currency': -counterpart_amount if currency_id else 0.0,
                            'currency_id': currency_id,
                            'debit': balance < 0.0 and -balance or 0.0,
                            'credit': balance > 0.0 and balance or 0.0,
                            'date_maturity': payment.date,
                            'partner_id': payment.partner_id.commercial_partner_id.id,
                            'account_id': payment.company_id.transfer_account_id.id,
                            'payment_id': payment.id,
                        }),
                        # Liquidity credit line.
                        (0, 0, {
                            'name': _('Transfer from %s') % payment.journal_id.name,
                            'amount_currency': transfer_amount if liquidity_line_currency_id else 0.0,
                            'currency_id': liquidity_line_currency_id,
                            'debit': balance > 0.0 and balance or 0.0,
                            'credit': balance < 0.0 and -balance or 0.0,
                            'date_maturity': payment.date,
                            'partner_id': payment.partner_id.commercial_partner_id.id,
                            'account_id': payment.destination_journal_id.default_credit_account_id.id,
                            'payment_id': payment.id,
                        }),
                    ],
                }

                if move_names and len(move_names) == 2:
                    transfer_move_vals['name'] = move_names[1]

                all_move_vals.append(transfer_move_vals)

            # validate the payment
            # if not self.journal_id.post_at_bank_rec:
            #    if not self.admission_request_id and not self.is_insurance:
            #        self.post() 

        return all_move_vals


class HrExpenseInherit(models.Model):
    _inherit = "hr.expense"

    expense_type = fields.Selection([('supplier', 'Supplier'), ('employee', 'Employee')], required=True,
                                    default='employee')
    supplier = fields.Many2one('res.partner', string='Supplier')
    admission_request_id = fields.Many2one('admission.request', string='admission reference')

    def _get_expense_account_destination(self):
        self.ensure_one()
        account_dest = self.env['account.account']
        if self.payment_mode == 'company_account':
            if not self.sheet_id.bank_journal_id.default_credit_account_id:
                raise UserError(_("No credit account found for the %s journal, please configure one.") % (
                    self.sheet_id.bank_journal_id.name))
            account_dest = self.sheet_id.bank_journal_id.default_credit_account_id.id
        else:
            if self.expense_type == "employee":
                if not self.employee_id.address_home_id:
                    raise UserError(
                        _("No Home Address found for the employee %s, please configure one.") % (self.employee_id.name))
                account_dest = self.employee_id.address_home_id.property_account_payable_id.id
            else:
                account_dest = self.supplier.property_account_payable_id.id
        return account_dest

    def _get_account_move_line_values(self):
        move_line_values_by_expense = {}
        for expense in self:
            if expense.expense_type == "employee":
                move_line_name = expense.employee_id.name + ': ' + expense.name.split('\n')[0][:64]
            else:
                move_line_name = expense.supplier.name + ': ' + expense.name.split('\n')[0][:64]

            account_src = expense._get_expense_account_source()
            account_dst = expense._get_expense_account_destination()
            account_date = expense.sheet_id.accounting_date or expense.date or fields.Date.context_today(expense)

            company_currency = expense.company_id.currency_id
            different_currency = expense.currency_id and expense.currency_id != company_currency

            move_line_values = []
            taxes = expense.tax_ids.with_context(round=True).compute_all(expense.unit_amount, expense.currency_id,
                                                                         expense.quantity, expense.product_id)
            total_amount = 0.0
            total_amount_currency = 0.0
            if expense.expense_type == "employee":
                partner_id = expense.employee_id.address_home_id.commercial_partner_id.id
            else:
                partner_id = expense.supplier.id

            # source move line
            amount = taxes['total_excluded']
            amount_currency = False
            if different_currency:
                amount = expense.currency_id._convert(amount, company_currency, expense.company_id, account_date)
                amount_currency = taxes['total_excluded']
            move_line_src = {
                'name': move_line_name,
                'quantity': expense.quantity or 1,
                'debit': amount if amount > 0 else 0,
                'credit': -amount if amount < 0 else 0,
                'amount_currency': amount_currency if different_currency else 0.0,
                'account_id': account_src.id,
                'product_id': expense.product_id.id,
                'product_uom_id': expense.product_uom_id.id,
                'analytic_account_id': expense.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)],
                'expense_id': expense.id,
                'partner_id': partner_id,
                'tax_ids': [(6, 0, expense.tax_ids.ids)],
                'currency_id': expense.currency_id.id if different_currency else False,
            }
            move_line_values.append(move_line_src)
            total_amount += -move_line_src['debit'] or move_line_src['credit']
            total_amount_currency += -move_line_src['amount_currency'] if move_line_src['currency_id'] else (
                    -move_line_src['debit'] or move_line_src['credit'])

            # taxes move lines
            for tax in taxes['taxes']:
                amount = tax['amount']
                amount_currency = False
                if different_currency:
                    amount = expense.currency_id._convert(amount, company_currency, expense.company_id, account_date)
                    amount_currency = tax['amount']
                move_line_tax_values = {
                    'name': tax['name'],
                    'quantity': 1,
                    'debit': amount if amount > 0 else 0,
                    'credit': -amount if amount < 0 else 0,
                    'amount_currency': amount_currency if different_currency else 0.0,
                    'account_id': tax['account_id'] or move_line_src['account_id'],
                    'tax_line_id': tax['id'],
                    'expense_id': expense.id,
                    'partner_id': partner_id,
                    'currency_id': expense.currency_id.id if different_currency else False,
                }
                total_amount -= amount
                total_amount_currency -= move_line_tax_values['amount_currency'] or amount
                move_line_values.append(move_line_tax_values)

            # destination move line
            move_line_dst = {
                'name': move_line_name,
                'debit': total_amount > 0 and total_amount,
                'credit': total_amount < 0 and -total_amount,
                'account_id': account_dst,
                'date_maturity': account_date,
                'amount_currency': total_amount_currency if different_currency else 0.0,
                'currency_id': expense.currency_id.id if different_currency else False,
                'expense_id': expense.id,
                'partner_id': partner_id,
            }
            move_line_values.append(move_line_dst)

            move_line_values_by_expense[expense.id] = move_line_values
        return move_line_values_by_expense

    def action_submit_expenses(self):
        if any(expense.state != 'draft' or expense.sheet_id for expense in self):
            raise UserError(_("You cannot report twice the same line!"))
        if len(self.mapped('employee_id')) != 1:
            raise UserError(_("You cannot report expenses for different employees in the same report."))

        todo = self.filtered(lambda x: x.payment_mode == 'own_account') or self.filtered(
            lambda x: x.payment_mode == 'company_account')

        if self.expense_type == "supplier":
            return {
                'name': _('New Expense Report'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'hr.expense.sheet',
                'target': 'current',
                'context': {
                    'default_expense_line_ids': todo.ids,
                    'default_employee_id': self[0].employee_id.id,
                    'default_expense_type': "supplier",
                    'default_supplier': self[0].supplier.id,
                    'default_name': todo[0].name if len(todo) == 1 else ''
                }
            }
        else:
            return {
                'name': _('New Expense Report'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'hr.expense.sheet',
                'target': 'current',
                'context': {
                    'default_expense_line_ids': todo.ids,
                    'default_employee_id': self[0].employee_id.id,
                    'default_name': todo[0].name if len(todo) == 1 else ''
                }
            }


class HrexpenseSheetInherit(models.Model):
    _inherit = "hr.expense.sheet"

    supplier = fields.Many2one('res.partner', string='Supplier')
    expense_type = fields.Selection([('supplier', 'Supplier'), ('employee', 'Employee')])
