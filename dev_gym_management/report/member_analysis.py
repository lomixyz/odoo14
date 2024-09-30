# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import tools
from odoo import api, fields, models


class MemberAnalysis(models.Model):
    _name = "member.analysis"
    _description = "Member Analysis Report"
    _auto = False

    name = fields.Char(string='Name')
    member_sequence = fields.Char(string='Member ID', default='New')
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip')
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string='State')
    country_id = fields.Many2one('res.country', string='Country')
    gender = fields.Selection(string='Gender', selection=[('male', 'Male'),
                                                          ('female', 'Female'),
                                                          ('other', 'Other')], default='male')
    dob = fields.Date(string='Date of Birth')
    mobile = fields.Char(string='Mobile')
    email = fields.Char(string='Email')
    trainer_id = fields.Many2one('gym.trainer', string='Trainer')
    user_id = fields.Many2one('res.users', string='User')
    state = fields.Selection(selection=[('waiting', 'Waiting'),
                                        ('joined', 'Joined'),
                                        ('left', 'Left')], default='waiting', string='Status')
    join_date = fields.Date(string='Join date')
    left_date = fields.Date(string='Left Date')
    membership_id = fields.Many2one('gym.membership', string='Membership')
    membership_fees = fields.Float(string='Fees')
    diet_plan_id = fields.Many2one('diet.plan', string='Diet Plan')
    workout_plan_id = fields.Many2one('workout.plan', string='Workout Plan')

    def _select(self):
        select_str = """ SELECT
                    min(gm.id) as id,
                    gm.name,
                    gm.member_sequence,
                    gm.street,
                    gm.street2,
                    gm.zip,
                    gm.city,
                    gm.state_id,
                    gm.country_id,
                    gm.gender,
                    gm.dob,
                    gm.mobile,
                    gm.email,
                    gm.trainer_id,
                    gm.user_id,
                    gm.state,
                    gm.join_date,
                    gm.left_date,
                    gm.membership_id,
                    gm.membership_fees,
                    md.diet_plan_id,
                    mw.workout_plan_id
        """
        return select_str

    def _from(self):
        from_str = """ gym_member gm join member_diet_detail md on (md.member_id = gm.id) join member_workout_detail mw on (mw.member_id = gm.id)"""
        return from_str

    def _group_by(self):
        group_by_str = """ GROUP BY
                gm.name,
                gm.member_sequence,
                gm.street,
                gm.street2,
                gm.zip,
                gm.city,
                gm.state_id,
                gm.country_id,
                gm.gender,
                gm.dob,
                gm.mobile,
                gm.email,
                gm.trainer_id,
                gm.user_id,
                gm.state,
                gm.join_date,
                gm.left_date,
                gm.membership_id,
                gm.membership_fees,
                md.diet_plan_id,
                mw.workout_plan_id
        """
        return group_by_str

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s ) %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: