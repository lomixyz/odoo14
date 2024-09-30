# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    
    module_hr_contract_grade_base = fields.Boolean(string="Grades Hierarchy")
    module_hr_contract_grade_extended = fields.Boolean(string="Top Down Salary Calculation")
    