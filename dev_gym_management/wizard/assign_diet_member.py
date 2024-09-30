# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields


class AssignDietMember(models.TransientModel):
    _name = "assign.diet.member"

    def assign_diet_plans(self):
        active_ids = self._context.get('active_ids')
        if active_ids:
            member_ids = self.env['gym.member'].browse(active_ids)
        for member_id in member_ids:
            for diet_plan_id in self.diet_plan_ids:
                self.env['member.diet.detail'].create({'member_id': member_id.id,
                                                       'diet_plan_id': diet_plan_id.id,
                                                       'date_from': self.date_from,
                                                       'date_to': self.date_to})

    diet_plan_ids = fields.Many2many('diet.plan', string='Diet Plans', required=True)
    date_from = fields.Date(string='From', required=True)
    date_to = fields.Date(string='To', required=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
