# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models, api


class WorkoutPlan(models.Model):
    _name = 'workout.plan'
    _description = 'Workout Plan'

    def _is_only_member_status(self):
        for member in self:
            only_member = True
            if member.env.user.has_group('dev_gym_management.gym_trainer'):
                only_member = False
            if member.env.user.has_group('dev_gym_management.gym_manager'):
                only_member = False
            member.is_only_member = only_member

    name = fields.Char('Name')
    day_id = fields.Many2many('workout.day', string='Workout Days')
    workout_line_ids = fields.One2many('workout.plan.line', 'workout_plan_id', string='Workout Lines')
    is_only_member = fields.Boolean(string='Member Only', compute='_is_only_member_status')


class WorkoutPlanLine(models.Model):
    _name = 'workout.plan.line'
    _description = 'Workout Plan Line'

    @api.onchange('exercise_id')
    def onchange_exercise_id(self):
        body_part_id = False
        equipment_id = False
        if self.exercise_id:
            if self.exercise_id.body_part_id:
                body_part_id = self.exercise_id.body_part_id.id
            if self.exercise_id.equipment_id:
                equipment_id = self.exercise_id.equipment_id.id
        self.body_part_id = body_part_id
        self.equipment_id = equipment_id

    workout_plan_id = fields.Many2one('workout.plan', string='Workout Plan')
    exercise_id = fields.Many2one('gym.exercise', string='Exercise')
    body_part_id = fields.Many2one('body.part', string='Body Part')
    equipment_id = fields.Many2one('gym.equipment', string='Equipment')
    sets = fields.Integer(string='Sets')
    repeat = fields.Integer(string='Repeat')
    weight = fields.Integer(string='Weight(kgs)')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: