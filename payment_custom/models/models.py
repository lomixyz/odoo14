from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PaymentCustom(models.Model):
    _inherit = 'account.move'

    cash = fields.Float(string='Cash')
    shabaka = fields.Float(string='Shabaka')
    transfer = fields.Float(string='Transfer')
    credit = fields.Float(string='Credit')

    @api.constrains('cash', 'shabaka', 'transfer', 'credit')
    def _check_positive_values(self):
        for record in self:
            if record.move_type == 'out_invoice':
                if all(value <= 0 for value in [record.cash , record.shabaka, record.transfer, record.credit]):
                    raise ValidationError(_("Values of fields cash, shabaka, transfer, and credit must be greater than zero for customer invoices."))


