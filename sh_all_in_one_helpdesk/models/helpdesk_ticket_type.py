# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class HelpdeskTicketType(models.Model):
    _inherit = 'helpdesk.ticket.type'
    _description = 'Helpdesk Ticket Type'
    # _rec_name = 'name'

    # name = fields.Char('Name', required=True,translate=True)
    sla_count = fields.Integer(compute='_compute_helpdesk_sla')
    category_id = fields.Many2one('helpdesk.category',"Category Name")
    def _compute_helpdesk_sla(self):
        for record in self:
            record.sla_count = 0
            slas = self.env['helpdesk.ticket'].sudo().search(
            [('ticket_type_id', '=', self.id),('sla_status_ids','!=',False)])
            record.sla_count = len(slas.ids)
    
    def action_view_sla(self):
        self.ensure_one()
        slas = self.env['helpdesk.ticket'].sudo().search(
            [('ticket_type_id', '=', self.id),('sla_status_ids','!=',False)])
        action = self.env["ir.actions.actions"]._for_xml_id(
            "sh_all_in_one_helpdesk.helpdesk_ticket_action")
        if len(slas) > 1:
            action['domain'] = [('id', 'in', slas.ids)]
        elif len(slas) == 1:
            form_view = [
                (self.env.ref('sh_all_in_one_helpdesk.helpdesk_ticket_form_view').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + \
                    [(state, view)
                     for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = slas.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
