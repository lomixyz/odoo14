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


class DietPlan(models.Model):
    _name = 'diet.plan'
    _description = 'Diet Plan'

    def _is_only_member_status(self):
        for member in self:
            only_member = True
            if member.env.user.has_group('dev_gym_management.gym_trainer'):
                only_member = False
            if member.env.user.has_group('dev_gym_management.gym_manager'):
                only_member = False
            member.is_only_member = only_member

    name = fields.Char('Name')
    diet_line_ids = fields.One2many('diet.plan.line', 'diet_plan_id', string='Diet Lines')
    is_only_member = fields.Boolean(string='Member Only', compute='_is_only_member_status')


class DietPlanLine(models.Model):
    _name = 'diet.plan.line'
    _description = 'Diet Plan Line'

    diet_plan_id = fields.Many2one('diet.plan', string='Diet Plan')
    diet_food_id = fields.Many2one('diet.food', string='Diet Food')
    quantity = fields.Integer(string='Quantity')
    consume_at_id = fields.Many2one('consume.at', string='Consume At')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: