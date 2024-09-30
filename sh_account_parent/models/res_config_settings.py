# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    chart_account_length = fields.Integer(
        string='Chart of Accounts Length'
    )
    chart_account_padding = fields.Integer(
        string='Chart of Accounts Padding'
    )
    use_fixed_tree = fields.Boolean(
        string='Use Fixed Length Chart of Accounts',
        default=False
    )
    automatic_accounts_codes = fields.Boolean(
        string='Automatically Generate Accounts Codes',
        default=False
    )
    parent_bank_cash_account_id = fields.Many2one('account.account')

    @api.model
    def setting_chart_of_accounts_action(self):
        """Action for 'Chart of Accounts' button in setup bar."""
        company = self.env.company
        company.set_onboarding_step_done('account_setup_coa_state')

        if company.opening_move_posted():
            return self._open_accounts_tree_view()

        company.create_op_move_if_non_existant()
        return self._open_custom_tree_view()

    def _open_accounts_tree_view(self):
        """Open accounts tree view."""
        company = self.env.company
        domain = [
            ('user_type_id', 'not in', [
                self.env.ref('account.data_unaffected_earnings').id,
                self.env.ref('sh_account_parent.data_account_type_view').id
            ]),
            ('company_id', '=', company.id)
        ]
        return {
            'type': 'ir.actions.act_window',
            'name': _('Chart of Accounts'),
            'res_model': 'account.account',
            'view_mode': 'tree',
            'limit': 99999999,
            'search_view_id': self.env.ref('account.view_account_search').id,
            'views': [[self.env.ref('account.init_accounts_tree').id, 'list']],
            'domain': domain,
        }

    def _open_custom_tree_view(self):
        """Open custom tree view for editing opening balances."""
        view_id = self.env.ref('account.init_accounts_tree').id
        domain = [('company_id', '=', self.env.company.id)]
        return {
            'type': 'ir.actions.act_window',
            'name': _('Chart of Accounts'),
            'res_model': 'account.account',
            'view_mode': 'tree',
            'limit': 99999999,
            'search_view_id': self.env.ref('account.view_account_search').id,
            'views': [[view_id, 'list']],
            'domain': domain,
        }


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    chart_account_length = fields.Integer(
        related='company_id.chart_account_length',
        readonly=False
    )
    chart_account_padding = fields.Integer(
        related='company_id.chart_account_padding',
        readonly=False
    )
    use_fixed_tree = fields.Boolean(
        related='company_id.use_fixed_tree',
        readonly=False
    )
    automatic_accounts_codes = fields.Boolean(
        related='company_id.automatic_accounts_codes',
        readonly=False
    )
    bank_account_code_prefix = fields.Char(
        string='Bank Prefix',
        related='company_id.bank_account_code_prefix',
        readonly=False
    )
    cash_account_code_prefix = fields.Char(
        string='Cash Prefix',
        related='company_id.cash_account_code_prefix',
        readonly=False
    )


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def search_panel_select_range(self, field_name, **kwargs):
        kwargs.update({
            'limit': 500,
        })
        return super(Base, self).search_panel_select_range(field_name, **kwargs)
