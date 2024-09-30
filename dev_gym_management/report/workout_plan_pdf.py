# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models


class WorkoutPlanPdf(models.AbstractModel):
    _name = 'report.dev_gym_management.workout_plan_pdf_template'

    def get_days(self, days):
        all = ''
        count = 0
        for day in days:
            count += 1
            all += day.name
            if not count == len(days):
                all += ', '
        return all

    def _get_report_values(self, docids, data=None):
        docs = self.env['workout.plan'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'workout.plan',
            'docs': docs,
            'get_days': self.get_days
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: