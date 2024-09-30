# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.exceptions import AccessError


def access_rights_check(group, orm_obj):
    if not orm_obj.env.user.has_group(group):
        raise AccessError(_('Sorry, you are not allowed to process this document.'))


class Custody(models.Model):
    _name = 'account.custody'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    @api.depends('amount', 'line_ids.amount')
    def _compute_balance(self):
        for r in self:
            amount_paid = sum(r.line_ids.mapped('amount'))
            r.balance = r.amount - amount_paid

    name = fields.Char('Custody Reference', readonly=True, default=_('New'))

    description = fields.Char('Description', required=True,
                              states={'posted': [('readonly', True)],
                                      'w_clear': [('readonly', True)], 'approve': [('readonly', True)],
                                      'post2': [('readonly', True)], 'cleared': [('readonly', True)]},
                              track_visibility='onchange')

    amount = fields.Monetary('Amount', currency_field='currency_id', digits=dp.get_precision('Account'),
                             required=True,
                             states={'posted': [('readonly', True)], 'w_clear': [('readonly', True)],
                                     'approve': [('readonly', True)],
                                     'post2': [('readonly', True)], 'cleared': [('readonly', True)]},
                             track_visibility='onchange')

    date = fields.Date('Date', required=True, default=fields.Date.context_today,
                       states={'posted': [('readonly', True)],
                               'w_clear': [('readonly', True)], 'approve': [('readonly', True)],
                               'post2': [('readonly', True)], 'cleared': [('readonly', True)]},
                       track_visibility='onchange')

    employee_id = fields.Many2one('hr.employee', required=True,
                                  states={'posted': [('readonly', True)], 'w_clear': [('readonly', True)],
                                          'approve': [('readonly', True)], 'post2': [('readonly', True)],
                                          'cleared': [('readonly', True)]}, track_visibility='onchange')

    journal_id = fields.Many2one('account.journal', 'Journal',
                                 domain=['|', ('type', '=', 'cash'), ('type', '=', 'bank')],
                                 states={'posted': [('readonly', True)], 'w_clear': [('readonly', True)],
                                         'approve': [('readonly', True)], 'post2': [('readonly', True)],
                                         'cleared': [('readonly', True)]}, track_visibility='onchange')

    account_id = fields.Many2one('account.account', 'Account',
                                 states={'posted': [('readonly', True)], 'w_clear': [('readonly', True)],
                                         'approve': [('readonly', True)], 'post2': [('readonly', True)],
                                         'cleared': [('readonly', True)]}, track_visibility='onchange')

    pay_date = fields.Date('Payment Date', default=fields.Date.context_today,
                           states={'posted': [('readonly', True)], 'w_clear': [('readonly', True)],
                                   'approve': [('readonly', True)], 'post2': [('readonly', True)],
                                   'cleared': [('readonly', True)]}, track_visibility='onchange')

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',
                                          states={'posted': [('readonly', True)], 'w_clear': [('readonly', True)],
                                                  'approve': [('readonly', True)], 'post2': [('readonly', True)],
                                                  'cleared': [('readonly', True)]}, track_visibility='onchange')

    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags',
                                        states={'posted': [('readonly', True)], 'w_clear': [('readonly', True)],
                                                'approve': [('readonly', True)], 'post2': [('readonly', True)],
                                                'cleared': [('readonly', True)]}, track_visibility='onchange')

    cus_journal_id = fields.Many2one('account.journal', 'Custody Journal', domain=[('type', '=', 'general')],
                                     states={'post2': [('readonly', True)], 'cleared': [('readonly', True)]},
                                     track_visibility='onchange')

    move_id = fields.Many2one('account.move', 'Accounting Entry', readonly=True, copy=False)

    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 states={'draft': [('readonly', False)], 'refused': [('readonly', False)]},
                                 default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True,
                                  states={'draft': [('readonly', False)], 'refused': [('readonly', False)]},
                                  default=lambda self: self.env.user.company_id.currency_id)
    line_ids = fields.One2many('account.custody.line', 'custody_id', 'Custody Lines',
                               states={'draft': [('readonly', True)], 'submit': [('readonly', True)],
                                       'posted': [('readonly', True)], 'post2': [('readonly', True)],
                                       'cleared': [('readonly', True)]})

    balance = fields.Monetary('Balance', currency_field='currency_id', compute=_compute_balance, store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('posted', 'Register Payment'),  # Change The Label To Register Payment But The Tech Name Not Changed
        ('w_clear', 'Wait Clear'),
        ('approve', 'Approve'),
        ('post2', 'Post'),
        ('cleared', 'Cleared'),  # Change The Name And Tech But Function Name Not Changed
    ], default='draft', track_visibility='onchange')

    def action_submit(self):
        # access_rights_check('hr_payroll.group_hr_payroll_manager', self)
        for r in self:
            if r.amount == 0.0:
                raise UserError(_("Amount Can't be 0"))
            r.name = self.env['ir.sequence'].next_by_code('custody')
        self.write({'state': 'submit'})

    def action_last_approve(self):
        self.write({'state': 'approve'})

    def action_close(self):
        for r in self:
            lines_total = sum(r.line_ids.mapped('amount'))
            if lines_total < r.amount:
                raise UserError(_('Custody is not fully paid!'))
        self.write({'state': 'cleared'})

    def action_refuse(self):
        self.write({'state': 'refused'})

    def action_post(self):
        # post the first payment entry
        # todo: correct this doc
        # debit: Custody Account
        # credit: Cash/Bank account
        for r in self:
            name = r.description

            date = r.pay_date

            move_value = {
                'narration': name,
                # 'ref': r.name,
                'journal_id': r.journal_id.id,
                'date': date,
            }
            move = self.env['account.move'].create(move_value)

            line_ids = []
            credit_acc_id = r.journal_id.default_account_id.id
            if not credit_acc_id:
                raise UserError(
                    _('The Journal "%s" has not properly configured the Credit Account!') % (r.journal_id.name))
            debit_acc_id = r.account_id.id

            currency = r.currency_id
            if r.employee_id.address_home_id.id:
                adjust_credit = {
                    'name': r.description,
                    'partner_id': r.employee_id.address_home_id.id,
                    'account_id': credit_acc_id,
                    'journal_id': r.journal_id.id,
                    'date': date,
                    'debit': 0.0,
                    'credit': currency.round(r.amount),
                }

                adjust_debit = {
                    'name': r.description,
                    'partner_id': r.employee_id.address_home_id.id,
                    'account_id': debit_acc_id,
                    'analytic_account_id': r.analytic_account_id.id,
                    'journal_id': r.journal_id.id,
                    'date': date,
                    'debit': currency.round(r.amount),
                    'credit': 0.0,
                }
            else:
                raise ValidationError(
                    _("The Employee  '  {}  '  Does not have a Private Address".format(r.employee_id.name)))

            line_ids.append(adjust_credit)
            line_ids.append(adjust_debit)

            # Create Payment
            # journal = self.journal_id
            # amount = self.amount
            #
            # payment_methods = journal.outbound_payment_method_ids if amount < 0 else journal.inbound_payment_method_ids
            # payment = self.env['account.payment'].create({
            #     'payment_method_id': payment_methods and payment_methods[0].id or False,
            #
            #     'payment_type': 'outbound',
            #     'partner_id': self.employee_id.address_home_id.commercial_partner_id.id,
            #     'partner_type': 'supplier',
            #     'journal_id': journal.id,
            #     'date': self.pay_date,
            #     'state': 'draft',
            #     'currency_id': self.currency_id.id,
            #     'amount': abs(amount),
            #     'name': self.description,
            # })
            # payment.action_post()

            # adjust_credit['payment_id'] = payment.id

            move.with_context(dont_create_taxes=True).write({
                'line_ids': [(0, 0, line) for line in line_ids]
            })

            r.write({'move_id': move.id, 'state': 'posted'})
            move.post()

    def action_wait(self):
        self.write({'state': 'w_clear'})

    def unlink(self):
        for r in self:
            if r.state not in ['draft', 'submit']:
                raise UserError(_('You can not delete an custody line if not in draft state '))
        return super(Custody, self).unlink()

    def action_line_post(self):
        # post the line entry
        # todo: correct this doc
        # debit: Expenses
        # credit: Custody Account (previously debited in the first payment entry)
        for r in self.line_ids:
            name = r.name
            amount = r.custody_id.currency_id.round(r.amount)
            if amount == 0.0:
                raise UserError("Amount can't be zero")
            if not r.date:
                raise UserError("Please add date in custody line")
            date = r.date
            move_dict = {
                'narration': name,
                'ref': r.custody_id.name,
                'journal_id': r.cus_journal_id.id,
                'date': date,
            }
            line_ids = []

            debit_acc_id = r.account_id.id
            credit_acc_id = r.custody_id.account_id.id
            if not debit_acc_id:
                raise UserError(_("Please set line's account!"))
            if not credit_acc_id:
                raise UserError(_("Please set Custody's account!"))

            # original_credit_acc_id = r.custody_id.journal_id.default_credit_account_id.id
            analytic_account_id = r.custody_id.analytic_account_id.id
            analytic = r.analytic_account_id.id
            # if debit_acc_id == original_credit_acc_id:
            #     analytic_account_id = r.custody_id.analytic_account_id and r.custody_id.analytic_account_id.id

            adjust_credit = (0, 0, {
                'name': r.name,
                'partner_id': r.custody_id.employee_id.address_home_id.id,
                'account_id': credit_acc_id,
                'analytic_account_id': analytic_account_id,
                'date': date,
                'debit': 0.0,
                'credit': amount,
            })
            adjust_debit = (0, 0, {
                'name': r.name,
                'partner_id': r.custody_id.employee_id.address_home_id.id,
                'account_id': debit_acc_id,
                'analytic_account_id': analytic,
                'date': date,
                'debit': amount,
                'credit': 0.0,
            })
            line_ids.append(adjust_credit)
            line_ids.append(adjust_debit)

            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            r.write({'move_id': move.id, 'state': 'post2'})
            move.post()


class CustodyLine(models.Model):
    _name = 'account.custody.line'
    _description = 'Custody Line'
    _order = 'date asc, id asc'
    # states = {'done': [('readonly', True)], 'cancel': [('readonly', True)]}

    custody_id = fields.Many2one('account.custody', 'Custody', ondelete="cascade", required=True)
    name = fields.Char('Description')

    product_id = fields.Many2one('product.product', string='Product')

    amount = fields.Monetary('Amount', currency_field='currency_id', digits=dp.get_precision('Account'))

    date = fields.Date('Date')

    journal_id = fields.Many2one('account.journal', 'Journal')

    account_id = fields.Many2one('account.account', 'Debit Account (Expense)', required=False)

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')

    currency_id = fields.Many2one(related='custody_id.currency_id', string='Currency', readonly=True)

    cus_journal_id = fields.Many2one(related='custody_id.cus_journal_id')
    attachment_id = fields.Many2many('ir.attachment', string='Files')
    can_reset = fields.Boolean('Can Reset', compute='_compute_can_reset')

    move_id = fields.Many2one('account.move', 'Accounting Entry', readonly=True, copy=False)
    state = fields.Selection('state ', related='custody_id.state', readonly=False)

    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)

    @api.constrains('amount')
    def validate_line_amounts(self):
        for r in self:
            lines_sum = sum(r.custody_id.line_ids.mapped('amount'))
            if lines_sum > r.custody_id.amount:
                raise UserError('Entered amount is larger than the custody.')

    def unlink(self):
        for r in self:
            if r.custody_id.state in ['post2', 'cleared', 'approve']:
                raise UserError(_('You can not delete an custody line if the custody line is in approved'))
        return super(CustodyLine, self).unlink()

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            rec.account_id = rec.product_id.property_account_expense_id
