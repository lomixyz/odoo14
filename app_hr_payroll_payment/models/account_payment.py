# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class Payment(models.Model):
    _inherit = 'account.payment'

    payslip_run_id = fields.Many2one('hr.payslip.run', string="Payslip Batch")