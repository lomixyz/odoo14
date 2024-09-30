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


class MemberPDF(models.AbstractModel):
    _name = 'report.dev_gym_management.member_pdf_template'

    def date_conversion(self, base_date):
        final_date = base_date
        if base_date:
            final_date = datetime.strptime(str(base_date), "%Y-%m-%d").strftime('%d-%m-%Y')
        return final_date

    def _get_report_values(self, docids, data=None):
        docs = self.env['gym.member'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'gym.member',
            'docs': docs,
            'date_conversion': self.date_conversion
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: