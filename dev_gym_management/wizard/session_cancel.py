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


class SessionCancel(models.TransientModel):
    _name = "session.cancel"

    reason = fields.Text(string='Remark', required=1)

    def cancel_session(self):
        active_id = self._context.get('active_id')
        if active_id:
            session_id = self.env['special.session'].browse(int(active_id))
            if session_id:
                session_id.state = 'cancel'
                session_id.cancel_reason = self.reason
                session_id.cancel_notification()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
