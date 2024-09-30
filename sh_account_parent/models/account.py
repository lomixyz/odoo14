# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountAccount(models.Model):
    _inherit = 'account.account'
    _parent_name = "parent_id"
    _parent_store = True

    parent_id = fields.Many2one('account.account', string="Parent Account", store=True)
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many('account.account', 'parent_id', 'Child Accounts')
    auto_code = fields.Char(compute='_compute_auto_code', store=True, size=64, index=True)
    level = fields.Integer(compute="_compute_level", store=True, string='Level')
    automatic_accounts_codes = fields.Boolean(related='company_id.automatic_accounts_codes')

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        if args is None:
            args = []
        domain = args 
        if not self.env.context.get('show_view'):
            domain += [('internal_type', '!=', 'view')]
        return super(AccountAccount, self)._name_search(name, domain, operator, limit, name_get_uid)

    @api.depends('parent_id')
    def _compute_level(self):
        for rec in self:
            level = 0
            if rec.parent_id:
                level = rec.parent_id.level + 1
            if rec.company_id.use_fixed_tree and rec.company_id.chart_account_length:
                if level > rec.company_id.chart_account_length:
                    raise UserError(
                        _('This account level is greater than the chart of account length.'))
            rec.level = level

    @api.depends('parent_id', 'code', 'parent_id.code')
    def _compute_auto_code(self):
        for rec in self:
            if not rec.company_id.automatic_accounts_codes and rec.code:
                rec.auto_code = rec.code
                continue

            code = str(0)
            rec_id = rec.id
            try:
                rec_id = self._origin.id
            except:
                pass
            if rec.parent_id:
                default_padding = self.env.user.company_id.chart_account_padding
                if rec.internal_type == 'view':
                    default_padding = False
                parent_code = rec.parent_id.read(['code'])[0]['code']
                parent_code = int(parent_code) != 0 and str(parent_code) or ''
                max_siblings_code = False
                siblings = self.search([
                    ('parent_id', '=', rec.parent_id.id),
                    type(rec_id) == int and ('id', '!=', rec_id) or (1, '=', 1)
                ])
                siblings = [x.read(['code'])[0]['code'] for x in siblings]
                if siblings:
                    max_siblings_code = max([int(x) for x in siblings])

                if not max_siblings_code:
                    code = parent_code + str(1).zfill(default_padding)
                if max_siblings_code:
                    code = str(max_siblings_code + 1)
            rec.write({'code': code, 'auto_code': code})


class AccountAccountType(models.Model):
    _inherit = "account.account.type"

    type = fields.Selection(selection_add=[('view', 'View')], ondelete={'view': 'cascade'})
    internal_group = fields.Selection(selection_add=[('view', 'View')],
                                       ondelete={'view': lambda recs: recs.write({'internal_group': 'off_balance'})})


class AccountAccountTemplate(models.Model):
    _inherit = "account.account.template"
    _parent_name = "parent_id"
    _parent_store = True

    parent_id = fields.Many2one(
        comodel_name='account.account.template',
        domain=[('internal_type', '=', 'view')]
    )
    parent_path = fields.Char(
        index=True
    )


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    def generate_account(self, tax_template_ref, acc_template_ref, code_digits, company):
        temp_model = self.env['account.account.template']
        acc_model = self.env['account.account']
        res = super(AccountChartTemplate, self).generate_account(tax_template_ref, acc_template_ref, code_digits, company)
        for temp, acc in res.items():
            parent = temp_model.browse(temp).parent_id.id
            if parent:
                acc_model.browse(acc).write({'parent_id': res[parent]})
        return res

# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = "account.journal"

    @api.model
    def _fill_missing_values(self, vals):

        journal_type = vals.get('type')

        # 'type' field is required.
        if not journal_type:
            return

        # Fill missing company
        company = self.env['res.company'].browse(vals.get('company_id')) if vals.get('company_id') else self.env.company
        vals['company_id'] = company.id

        # Don't get the digits on 'chart_template_id' since the chart template could be a custom one.
        random_account = self.env['account.account'].search([('company_id', '=', company.id)], limit=1)
        digits = len(random_account.code) if random_account else 6

        liquidity_type = self.env.ref('account.data_account_type_liquidity')
        current_assets_type = self.env.ref('account.data_account_type_current_assets')

        if journal_type in ('bank', 'cash'):
            has_liquidity_accounts = vals.get('default_account_id')
            has_payment_accounts = vals.get('payment_debit_account_id') or vals.get('payment_credit_account_id')
            has_profit_account = vals.get('profit_account_id')
            has_loss_account = vals.get('loss_account_id')

            if journal_type == 'bank':
                liquidity_account_prefix = company.bank_account_code_prefix or ''
            else:
                liquidity_account_prefix = company.cash_account_code_prefix or company.bank_account_code_prefix or ''

            parent = self.env['account.account'].search([('code', '=', liquidity_account_prefix)], limit=1)
            if not parent:
                raise UserError(
                    _("Can not find account with code (%s).") % (liquidity_account_prefix,))

            # Fill missing name
            vals['name'] = vals.get('name') or vals.get('bank_acc_number')

            # Fill missing code
            if 'code' not in vals:
                vals['code'] = self.get_next_bank_cash_default_code(journal_type, company)
                if not vals['code']:
                    raise UserError(_("Cannot generate an unused journal code. Please fill the 'Shortcode' field."))

            # Fill missing accounts
            if not has_liquidity_accounts:
                default_account_code = self.env['account.account']._search_new_account_code(company, digits, liquidity_account_prefix)
                default_account_vals = self._prepare_liquidity_account_vals(company, default_account_code, vals)
                default_account_vals['parent_id'] = parent.id
                res = self.env['account.account'].create(default_account_vals)
                vals['default_account_id'] = res.id 
            if not has_payment_accounts:
                vals['payment_debit_account_id'] = self._create_payment_account(_("Outstanding Receipts"), current_assets_type, company, parent, digits, liquidity_account_prefix)
                vals['payment_credit_account_id'] = self._create_payment_account(_("Outstanding Payments"), current_assets_type, company, parent, digits, liquidity_account_prefix)
            if journal_type == 'cash' and not has_profit_account:
                vals['profit_account_id'] = company.default_cash_difference_income_account_id.id
            if journal_type == 'cash' and not has_loss_account:
                vals['loss_account_id'] = company.default_cash_difference_expense_account_id.id

        # Fill missing refund_sequence
        if 'refund_sequence' not in vals:
            vals['refund_sequence'] = vals['type'] in ('sale', 'purchase')

    def _create_payment_account(self, name, account_type, company, parent, digits, prefix):
        return self.env['account.account'].create({
            'name': name,
            'code': self.env['account.account']._search_new_account_code(company, digits, prefix),
            'reconcile': True,
            'user_type_id': account_type.id,
            'company_id': company.id,
            'parent_id': parent.id,
        }).id

