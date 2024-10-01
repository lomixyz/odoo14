from email.policy import default

from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'


    active = fields.Boolean(string='active', default=True)