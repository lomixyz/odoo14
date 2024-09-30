# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    task_count = fields.Integer('Tasks', compute='_compute_task_count')
    task_ids = fields.Many2many('project.task', string='Task')

    def _compute_task_count(self):
        if self:
            for rec in self:
                rec.task_count = 0
                task_ids = self.env['project.task'].sudo().search(
                    [('ticket_ids', 'in', [rec.id])])
                if task_ids:
                    rec.task_count = len(task_ids.ids)

    def create_task(self):
        return{
            'name': 'Tasks',
            'res_model': 'project.task',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {
                'default_name': self.name,
                'default_user_id': self.user_id.id,
                'default_ticket_ids': [(4, self.id)],
                'default_partner_id': self.partner_id.id,
                'default_date_deadline': fields.Date.today(),
                'default_description': self.description
            }
        }

    def view_task(self):
        task_ids = self.env['project.task'].sudo().search(
            [('ticket_ids', 'in', [self.id])])
        return{
            'name': 'Tasks',
            'res_model': 'project.task',
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', task_ids.ids)],
            'target': 'current',
        }
