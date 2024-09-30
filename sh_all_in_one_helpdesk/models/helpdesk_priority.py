# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api


class HelpdeskPriority(models.Model):
    _name = 'helpdesk.priority'
    _description = 'Helpdesk Priority'
    _rec_name = 'name'

    sequence = fields.Integer(string="Sequence")
    name = fields.Char(required=True, translate=True, string="Name")
    color = fields.Char(string="Color")

    @api.model
    def create(self, values):
        sequence = self.env['ir.sequence'].next_by_code('helpdesk.priority')
        values['sequence'] = sequence
        return super(HelpdeskPriority, self).create(values)
