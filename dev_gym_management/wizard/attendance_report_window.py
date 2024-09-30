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
from datetime import date


class AttendanceReportWindow(models.TransientModel):
    _name = 'attendance.report.window'

    start_date = fields.Date(string='Start Date', required=True, default=date.today())
    end_date = fields.Date(string='End Date', required=True, default=date.today())
    attendance_of = fields.Selection(selection=[('members', 'Members'),
                                                ('trainers', 'Trainers')], default='members',
                                     string='Attendance Of', required=True)

    def print_gym_attendance_report(self):
        return self.env.ref('dev_gym_management.menu_attendance_report_pdf_print').report_action(self)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: