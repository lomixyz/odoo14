# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api


class Task(models.Model):
    _inherit = 'project.task'

    ticket_count = fields.Integer('Tickets', compute='_compute_ticket_count')
    ticket_ids = fields.Many2many('helpdesk.ticket', string='Ticket')

    def _compute_ticket_count(self):
        if self:
            for rec in self:
                rec.ticket_count = 0
                ticket_ids = self.env['helpdesk.ticket'].sudo().search(
                    [('task_ids', 'in', [rec.id])])
                if ticket_ids:
                    rec.ticket_count = len(ticket_ids.ids)

    def action_view_ticket(self):
        ticket_ids = self.env['helpdesk.ticket'].sudo().search(
            [('task_ids', 'in', [self.id])])
        return{
            'name': 'Helpdesk Tickets',
            'res_model': 'helpdesk.ticket',
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', ticket_ids.ids)],
            'target': 'current',
        }

    @api.model
    def create(self, vals):
        res = super(Task, self).create(vals)
        if res.ticket_ids:
            for ticket in res.ticket_ids:
                ticket.sudo().write({
                    'task_ids': [(4, res.id)]
                })
                if ticket.attachment_ids:
                    for attachment in ticket.attachment_ids:
                        self.env['ir.attachment'].sudo().create({
                            'name': attachment.name,
                            'type': attachment.type,
                            'datas': attachment.datas,
                            'mimetype': attachment.mimetype,
                            'res_model': 'project.task',
                            'res_id': res.id,
                        })
        return res
