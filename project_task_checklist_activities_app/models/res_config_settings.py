# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    task_progress_restriction = fields.Selection([
        ('no_restriction', 'No Task Progress Restriction'),
        ('restriction', 'Restriction To Task Progress Before All Checklist Completion')
        ],related='company_id.task_progress_restriction',readonly=False
        )
