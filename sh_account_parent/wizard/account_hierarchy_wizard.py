# -*- coding: utf-8 -*-
# Part of Softhealer Technologies
from email.policy import default
from shutil import move
from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.tools import safe_eval


class AccountHierarchyWizard(models.TransientModel):
    _name = 'sh.account.hierarchy.wizard'
    _description = 'Account Hierarchy Wizard'
    auto_unfold = fields.Boolean(string="Auto Unfold")
    start_date = fields.Date(string="Start Date",)
    end_date = fields.Date(string="End Date",)
    target_moves = fields.Selection([
        ('all_posted_entries', 'All Posted Entries'),
        ('all_entries', 'All Entries')
    ], default='all_posted_entries')
    include_zero_amount_transaction = fields.Boolean(string="Include Zero Amount Transaction", default=True)
    hierarchy_based_on = fields.Selection([
        ('account', 'Account'),
        ('account_type', 'Account Type')
    ], default='account')

    def get_account_type_data(self):

        parent_account_types = [
				{   'name': 'Balance Sheet', 'id':-5001, 'parent_id': False,
				    'internal_group': ['asset', 'liability', 'equity'], 'account_type':False},

				{   'name': 'Profit & Loss', 'id':-5002, 'parent_id': False,
				    'internal_group': ['income', 'expense'], 'account_type':False},

				{   'name': 'Assets', 'id':-5003, 'parent_id':-5001,
					'internal_group': ['asset'], 'account_type':False},

				{   'name': 'Liabilities', 'id':-5004, 'parent_id':-5001,
					'internal_group':['liability'], 'account_type':False},

				{   'name': 'Equity', 'id':-5005, 'parent_id':-5001,
					'internal_group':['equity'], 'account_type':False},

				{   'name': 'Income', 'id':-5006, 'parent_id':-5002,
					'internal_group':['income'], 'account_type':False},

				{   'name': 'Expense', 'id':-5007, 'parent_id':-5002,
					'internal_group':['expense'], 'account_type':False},
				]
        
        parent_account_types_temp = parent_account_types[:]

        for parent_account_type in parent_account_types_temp:
            if not parent_account_type['parent_id']:
                continue
            account_types = self.env['account.account.type'].search([('internal_group', 'in', parent_account_type['internal_group'])])

            for account_type in account_types:
                parent_account_types.append({   'name': account_type.name,
                                                'id':-1 * account_type.id,
                                                'parent_id': parent_account_type['id'],
                                                'internal_group': [account_type.internal_group],
                                                'account_type':account_type.id
                                            })
        
        return parent_account_types

    @api.model
    def get_account_type_line_data(self, parent_id, level, js_context):
        
        list_of_account_type_data_dict = []

        wizard_id = self.env['sh.account.hierarchy.wizard'].browse(js_context.get('active_id'))
        dict_datas = list(filter(lambda x:x['parent_id'] == parent_id, self.get_account_type_data()))
        
        if dict_datas:

            for data in dict_datas:
                
                accounts = self.env['account.account'].search([('user_type_id.internal_group', 'in', data['internal_group']), ('company_id', '=', self.env.company.id)])

                if data['account_type'] != False:
                    accounts = accounts.filtered(lambda x:x.user_type_id.id == data['account_type'])

                move_lines = self.env['account.move.line'].search([('account_id', 'in', accounts.ids)])

                if wizard_id.start_date and wizard_id.end_date:
                    move_lines = move_lines.filtered(lambda x:x.date >= wizard_id.start_date and x.date <= wizard_id.end_date)

                if wizard_id.target_moves == 'all_posted_entries':
                    move_lines = move_lines.filtered(lambda x:x.parent_state == 'posted')
                
                total_debit = sum(move_lines.mapped('debit'))
                total_credit = sum(move_lines.mapped('credit'))

                total_balance = total_debit - total_credit
            
                if not wizard_id.include_zero_amount_transaction and total_balance == 0:
                    continue

                list_of_account_type_data_dict.append({
                    'id': data['id'],
                    'name': data['name'],
                    'code': data['name'].upper(),
                    'unfoldable': True,
                    'auto_unfold': wizard_id.auto_unfold,
                    'parent_id': parent_id,
                    'level': level,
                    'type': 'View',
                    'total_debit': round(total_debit, 2),
                    'total_credit': round(total_credit, 2),
                    'total_balance': round(total_balance, 2),
                    'wizard_id': wizard_id.id
                })
        
        # if dict data not found means now we need to find account related to account type
        else:
            
            accounts = self.env['account.account'].sudo().search([('user_type_id', '=', parent_id * -1)])

            for account in accounts:

                move_lines = self.env['account.move.line'].search([('account_id', '=', account.id)])

                if wizard_id.start_date and wizard_id.end_date:
                    move_lines = move_lines.filtered(lambda x:x.date >= wizard_id.start_date and x.date <= wizard_id.end_date)

                if wizard_id.target_moves == 'all_posted_entries':
                    move_lines = move_lines.filtered(lambda x:x.parent_state == 'posted')
                
                total_debit = sum(move_lines.mapped('debit'))
                total_credit = sum(move_lines.mapped('credit'))

                total_balance = total_debit - total_credit
            
                if not wizard_id.include_zero_amount_transaction and total_balance == 0:
                    continue

                list_of_account_type_data_dict.append({
                'id': account.id,
                'name': account.name,
                'code':account.code,
                'unfoldable': False ,
                'auto_unfold': wizard_id.auto_unfold,
                'parent_id': parent_id,
                'level': level,
                'type': account.user_type_id.name,
                'total_debit': round(total_debit, 2),
                'total_credit': round(total_credit, 2),
                'total_balance': round(total_balance, 2),
                'wizard_id': wizard_id.id
                })
        
        return list_of_account_type_data_dict

    def _get_child_accounts(self, parent_account, child_account_list):
        child_accounts = self.env['account.account'].sudo().search([('sh_parent_id', '=', parent_account)])
        for account in child_accounts:
            child_account_list.append(account.id)
            child_account_list = self._get_child_accounts(account.id, child_account_list)
            
        return child_account_list

    @api.model
    def get_account_line_data(self, parent_id, level, js_context):
        
        list_of_account_data_dict = []

        wizard_id = self.env['sh.account.hierarchy.wizard'].browse(js_context.get('active_id'))
        accounts = self.env['account.account'].search([('sh_parent_id', '=', parent_id), ('company_id', '=', self.env.company.id)])

        for account in accounts:

            child_account_list = [account.id]
            child_account_list = wizard_id._get_child_accounts(account.id, child_account_list)

            move_lines = self.env['account.move.line'].search([('account_id', 'in', child_account_list)])

            if wizard_id.start_date and wizard_id.end_date:
                move_lines = move_lines.filtered(lambda x:x.date >= wizard_id.start_date and x.date <= wizard_id.end_date)

            if wizard_id.target_moves == 'all_posted_entries':
                move_lines = move_lines.filtered(lambda x:x.parent_state == 'posted')
            
            total_debit = sum(move_lines.mapped('debit'))
            total_credit = sum(move_lines.mapped('credit'))

            total_balance = total_debit - total_credit
            
            if not wizard_id.include_zero_amount_transaction and total_balance == 0:
                continue

            list_of_account_data_dict.append({
                'id': account.id,
                'name': account.name,
                'code':account.code,
                'unfoldable': True if account.user_type_id.type == 'view' else False,
                'auto_unfold': wizard_id.auto_unfold,
                'parent_id': parent_id,
                'level': level,
                'type': account.user_type_id.name,
                'total_debit': round(total_debit, 2),
                'total_credit': round(total_credit, 2),
                'total_balance': round(total_balance, 2),
                'wizard_id': wizard_id.id
            })
        
        return list_of_account_data_dict

    # get html method calls one through will start function of js
    @api.model
    def get_html(self, js_context=False):
        result = {}
        data_dict = {}
        wizard_id = self.env['sh.account.hierarchy.wizard'].browse(js_context.get('active_id'))

        if wizard_id.hierarchy_based_on == 'account':
            account_line_data = wizard_id.get_account_line_data(False, 1, js_context)
        else:
            account_line_data = wizard_id.get_account_type_line_data(False, 1, js_context)
        
        data_dict.update({
            'account_data': account_line_data,
            'company_name': self.env.company.name,
        })

        result['html'] = self.env.ref('sh_account_parent.sh_account_hierarchy_report')._render(data_dict)

        return result

    def update_context(self):
        self.ensure_one()

        result = {}

        result['auto_unfold'] = self.auto_unfold or False
        result['start_date'] = self.env['ir.qweb.field.date'].value_to_html(self.start_date, {}) or ''
        result['end_date'] = self.env['ir.qweb.field.date'].value_to_html(self.end_date, {}) or ''
        result['target_moves'] = self.target_moves
        result['include_zero_amount_transaction'] = self.include_zero_amount_transaction
        result['hierarchy_based_on'] = self.hierarchy_based_on

        return result
    
    def display_account_hierarchy(self):

        res = self.env.ref('sh_account_parent.sh_display_account_hierarchy').read([])[0]

        updated_context = self.update_context()

        result_context = self.env.context or {}
        updated_context.update(result_context)
        res['context'] = str(updated_context)

        return res
