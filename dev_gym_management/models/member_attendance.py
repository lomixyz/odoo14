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
from datetime import datetime
from odoo.tools import pytz
from dateutil.relativedelta import relativedelta


class MemberAttendance(models.Model):
    _name = 'member.attendance'
    _description = 'Member Attendance'
    _rec_name = 'member_id'

    def get_logged_in_member(self):
        member = False
        member_id = self.env['gym.member'].search([('user_id', '=', self.env.user.id)], limit=1)
        if member_id:
            member = member_id.id
        return member

    def get_formatted_date(self, date):
        input_date = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S")
        user = self.env.user
        tz = pytz.timezone(user.tz) or pytz.utc
        user_tz_date = pytz.utc.localize(input_date).astimezone(tz)
        date_without_tz = user_tz_date.replace(tzinfo=None)
        return date_without_tz

    def get_difference(self, check_in, check_out):
        difference = relativedelta(check_out, check_in)
        hours = difference.hours
        minutes = difference.minutes
        difference_time = str(hours) + ' hours, ' + str(minutes) + ' minutes'
        hour = hours
        list_data = [difference_time,hour,minutes]
        return list_data

    def _get_time_difference(self):
        for record in self:
            time_differnace = ''
            if record.check_in and record.check_out:
                check_in = record.get_formatted_date(record.check_in)
                check_out = record.get_formatted_date(record.check_out)
                if check_in and check_out:
                    difference = self.get_difference(check_in, check_out)
                    if difference:
                        time_differnace = difference[0]
            record.time_difference = time_differnace

    member_id = fields.Many2one('gym.member', string='Gym Member', default=get_logged_in_member)
    trainer_id = fields.Many2one('gym.trainer', string='Gym Trainer', related='member_id.trainer_id', readonly=True)
    check_in = fields.Datetime(string='Check In')
    check_out = fields.Datetime(string='Check Out')
    time_difference = fields.Char(string='Time Spent', compute="_get_time_difference")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: