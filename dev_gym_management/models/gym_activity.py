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
from datetime import date


class GymActivity(models.Model):
    _name = 'gym.activity'
    _description = 'Gym Activity'

    def get_logged_in_member(self):
        member = False
        member_id = self.env['gym.member'].search([('user_id', '=', self.env.user.id)], limit=1)
        if member_id:
            member = member_id.id
        return member

    member_id = fields.Many2one('gym.member', string='Member', default=get_logged_in_member)
    trainer_id = fields.Many2one('gym.trainer', string='Trainer', related='member_id.trainer_id', readonly='2')
    date = fields.Date(string='Date', default=date.today())
    exercise_id = fields.Many2one('gym.exercise', string='Exercise')
    equipment_id = fields.Many2one('gym.equipment', string='Equipment')
    sets = fields.Integer(string='Sets')
    repeat = fields.Integer(string='Repeat')
    weight = fields.Integer(string='Weight(kgs)')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: