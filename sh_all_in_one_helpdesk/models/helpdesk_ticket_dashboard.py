# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, _


class TicketDashboard(models.Model):
    _name = 'ticket.dashboard'
    _description = 'Ticket Dashboard'

    name = fields.Char('Name')

    def get_ticket_data(self, ids):
        return {
            'name': _('Tickets'),
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.ticket',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', ids)],
            'target': 'current'
        }
