# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models


class GymExercise(models.Model):
    _name = 'gym.exercise'
    _description = 'Gym Exercise'

    def _is_only_member_status(self):
        for member in self:
            only_member = True
            if member.env.user.has_group('dev_gym_management.gym_trainer'):
                only_member = False
            if member.env.user.has_group('dev_gym_management.gym_manager'):
                only_member = False
            member.is_only_member = only_member

    name = fields.Char('Name')
    body_part_id = fields.Many2one('body.part', string='Body Part')
    equipment_id = fields.Many2one('gym.equipment', string='Equipment')
    steps = fields.Text(string='Steps')
    benefits = fields.Text(string='Benefits')
    is_only_member = fields.Boolean(string='Member Only', compute='_is_only_member_status')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: