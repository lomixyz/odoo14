from odoo import fields, models, api


class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    cash_journal_id = fields.Many2one('account.journal',
                                      string='Cash Journal',
                                      domain=[('type', 'in', ['cash', 'bank'])],
                                      ondelete='restrict',
                                      help='The payment method is of type cash. A cash statement will be automatically generated.')
