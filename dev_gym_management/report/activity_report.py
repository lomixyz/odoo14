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


class GymActivityReport(models.AbstractModel):
    _name = 'report.dev_gym_management.activity_template'

    def date_conversion(self, base_date):
        final_date = base_date
        if base_date:
            final_date = datetime.strptime(str(base_date), "%Y-%m-%d").strftime('%d-%m-%Y')
        return final_date

    def get_activity_data(self, window_id):
        data = []
        activity_ids = self.env['gym.activity'].search([('date', '>=',window_id.start_date),
                                                        ('date','<=',window_id.end_date)])
        if activity_ids:
            for activity in activity_ids:
                data.append({'member': activity.member_id.name,
                             'date': self.date_conversion(activity.date),
                             'exercise': activity.exercise_id.name,
                             'equipment': activity.equipment_id.name,
                             'sets': activity.sets,
                             'repeat': activity.repeat,
                             'weight': activity.weight,
                             })
        return data

    def _get_report_values(self, docids, data=None):
        docs = self.env['activity.report.window'].browse(docids)
        return {'doc_ids': docids,
                'doc_model': 'activity.report.window',
                'docs': docs,
                'get_activity_data': self.get_activity_data,
                'date_conversion': self.date_conversion,
                }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: