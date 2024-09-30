# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import api, models
from datetime import datetime
import pytz


class GymAttendanceReport(models.AbstractModel):
    _name = 'report.dev_gym_management.attendance_template'

    def date_conversion(self, base_date):
        final_date = base_date
        if base_date:
            final_date = datetime.strptime(str(base_date), "%Y-%m-%d").strftime('%d-%m-%Y')
        return final_date

    def get_formatted_date(self, date):
        input_date = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S")
        user = self.env.user
        tz = pytz.timezone(user.tz) or pytz.utc
        user_tz_date = pytz.utc.localize(input_date).astimezone(tz)
        date_without_tz = user_tz_date.replace(tzinfo=None)
        return date_without_tz

    def get_attendance_data(self, window_id):
        data = []
        attendance_model = 'member.attendance'
        if window_id.attendance_of == 'trainers':
            attendance_model = 'trainer.attendance'
        attendance_ids = self.env[attendance_model].search([('check_in', '>=',window_id.start_date), ('check_in','<=',window_id.end_date)])
        if attendance_ids:
            for attendance in attendance_ids:
                check_in = self.get_formatted_date(attendance.check_in)
                check_out = self.get_formatted_date(attendance.check_out)
                if window_id.attendance_of == 'trainers':
                    namee = attendance.trainer_id.name
                else:
                    namee = attendance.member_id.name
                data.append({'member': namee,
                             'check_in': check_in,
                             'check_out': check_out,
                             'time_difference': attendance.time_difference
                             })
        return data

    def _get_report_values(self, docids, data=None):
        docs = self.env['attendance.report.window'].browse(docids)
        return {'doc_ids': docids,
                'doc_model': 'attendance.report.window',
                'docs': docs,
                'get_attendance_data': self.get_attendance_data,
                'date_conversion': self.date_conversion,
                'get_formatted_date': self.get_formatted_date
                }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: