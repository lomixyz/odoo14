from odoo import fields, models, api


class InheritResCompnay(models.Model):
    _inherit = 'res.company'

    track_and_trace_user_name = fields.Char(string="User Name")
    track_and_trace_password = fields.Char(string="Password")
