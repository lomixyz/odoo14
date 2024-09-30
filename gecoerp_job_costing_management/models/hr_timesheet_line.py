# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    start_time = fields.Float(
        string='Hora de Inicio',
    )
    end_time = fields.Float(
        string='Hora Final',
    )
    job_cost_id = fields.Many2one(
        'job.costing',
        string='Hoja de Obra',
    )
    job_cost_line_id = fields.Many2one(
        'job.cost.line',
        string='Concepto de Obra',
    )
    
