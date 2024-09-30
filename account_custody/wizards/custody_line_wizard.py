from odoo import fields, api, models
from odoo.addons import decimal_precision as dp
from functools import wraps

def check_return(method):
    @wraps(method)
    def wrapper_function(self, *args, **kwargs):
        context = dict(self._context or {})
        return_amount = context.get('return_amount', False)
        if return_amount:
            return method(self, *args, **kwargs)
        else:
            return
    return wrapper_function


class EmployeeLoan(models.TransientModel):
    _name = 'account.custody.line.wizard'
    _description = 'Custody Line Wizard'

    def _default_custody(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', [])
        return self.env['account.custody'].browse(active_id)

    @check_return
    def default_journal(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', [])
        custody_id = self.env['account.custody'].browse(active_id)
        return custody_id.move_id.journal_id

    @check_return
    def default_account(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', [])
        custody_id = self.env['account.custody'].browse(active_id)
        return custody_id.move_id.journal_id.default_credit_account_id

    @check_return
    def default_amount(self):
        # Todo:: Add is_return_amount field to account.custody.line to identify the returned lines
        context = dict(self._context or {})
        active_id = context.get('active_id', [])
        custody_id = self.env['account.custody'].browse(active_id)
        amount = custody_id.amount - sum(custody_id.line_ids.mapped('amount'))
        return amount > 0.0 and amount or 0.0

    @check_return
    def default_name(self):
        context = dict(self._context or {})
        return 'Returned Amount'

    custody_id = fields.Many2one('account.custody', 'Custody', default=_default_custody)
    name = fields.Char('Description', default=default_name, required=True)
    product_id = fields.Many2one('product.product', string='Product')

    amount = fields.Monetary('Amount', currency_field='currency_id', digits=dp.get_precision('Account'), default=default_amount, required=True)
    date = fields.Date('Date', required=True)
    # journal_id = fields.Many2one('account.journal', 'Journal', required=False, default=default_journal)
    # account_id = fields.Many2one('account.account', 'Account', required=False, default=default_account)
    currency_id = fields.Many2one(related='custody_id.currency_id', string='Currency', readonly=True)

    def action_add_line(self):
        self.ensure_one()
        line_dict = {
            'name': self.name,
            'amount': self.amount,
            'date': self.date,
            'product_id': False,
            # 'account_id': self.account_id.id,
            'custody_id': self.custody_id.id,
        }
        line = self.env['account.custody.line'].create(line_dict)
        # line.post()
        return {'type': 'ir.actions.act_window_close'}
