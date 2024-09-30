# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    job_cost_id = fields.Many2one(
        'job.costing',
        string='Hoja de Obra',
    )
    job_cost_line_id = fields.Many2one(
        'job.cost.line',
        string='Concepto de Obra',
    )
