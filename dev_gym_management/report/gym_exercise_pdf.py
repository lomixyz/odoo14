# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import api, models, addons


class GymExercise(models.AbstractModel):
    _name = 'report.dev_gym_management.gym_exercise_pdf_template'

    def _get_report_values(self, docids, data=None):
        docs = self.env['gym.exercise'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'gym.exercise',
            'docs': docs,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: