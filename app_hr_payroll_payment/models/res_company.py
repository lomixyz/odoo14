# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    payslip_payment_mode = fields.Selection([('employee', 'Per Employee'), ('group', 'Grouped')], string="Batch Payment Mode",
                                            required=True, related='company_id.payslip_payment_mode', readonly=False)
    

class Company(models.Model):
    _inherit = 'res.company'

    payslip_payment_mode = fields.Selection([('employee', 'Per Employee'), ('group', 'Grouped')], string="Batch Payment",
                                            default='group', readonly=False)
