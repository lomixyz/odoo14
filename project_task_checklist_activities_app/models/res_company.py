# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    task_progress_restriction = fields.Selection([
        ('no_restriction', 'No Task Progress Restriction'),
        ('restriction', 'Restriction To Task Progress Before All Checklist Completion')
        ])