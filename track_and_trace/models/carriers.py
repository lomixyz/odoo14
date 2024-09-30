from odoo import fields, models, api


class Carriers(models.Model):
    _name = 'track.and.trace.carriers'
    _description = 'The specific carrier you wish to see track and trace from.'

    number = fields.Integer(string="Number",required=True)
    name = fields.Char(string="Name",required=True)
