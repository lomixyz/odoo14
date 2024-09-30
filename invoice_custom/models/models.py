# -*- coding: utf-8
# -*-

from odoo import models, fields, api ,_
from odoo.exceptions import ValidationError

# class Attachment(models.Model):
#     _name = 'account.move'
#     _inherit = 'account.move'
#     state = fields.Selection(selection=[
#         ('draft', 'Draft'),
#         ('validate', 'Validated'),
#         ('posted', 'Posted'),
#         ('cancel', 'Cancelled')
#     ], string='Status', required=True, readonly=True, copy=False, tracking=True,
#         default='draft')
#
#     def action_validated(self):
#         self.write({'state': 'validate'})
#
#
#
# class accountInheritPayment(models.Model):
#     _inherit = "account.payment"
#
#     @api.constrains('amount')
#     def _check_amount(self):
#         if self.amount == 0:
#             raise ValidationError(_('The payment amount cannot be Zero.'))
#




