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


class AssignWorkoutMember(models.TransientModel):
    _name = "assign.workout.member"

    def assign_workout_plans(self):
        active_ids = self._context.get('active_ids')
        if active_ids:
            member_ids = self.env['gym.member'].browse(active_ids)
        for member_id in member_ids:
            for workout_plan_id in self.workout_plan_ids:
                self.env['member.workout.detail'].create({'member_id': member_id.id,
                                                          'workout_plan_id': workout_plan_id.id,
                                                          'date_from': self.date_from,
                                                          'date_to': self.date_to})

    workout_plan_ids = fields.Many2many('workout.plan', string='Workout Plans', required=True)
    date_from = fields.Date(string='From', required=True)
    date_to = fields.Date(string='To', required=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
