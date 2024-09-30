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
import pytz


class SpecialSession(models.Model):
    _name = 'special.session'
    _description = 'Special Session'

    def user_timezone_start_at(self):
        input_date = datetime.strptime(str(self.start_at), "%Y-%m-%d %H:%M:%S")
        user = self.env.user
        tz = pytz.timezone(user.tz) or pytz.utc
        user_tz_date = pytz.utc.localize(input_date).astimezone(tz)
        date_without_tz = user_tz_date.replace(tzinfo=None)
        return str(date_without_tz)

    def user_timezone_end_at(self):
        input_date = datetime.strptime(str(self.end_at), "%Y-%m-%d %H:%M:%S")
        user = self.env.user
        tz = pytz.timezone(user.tz) or pytz.utc
        user_tz_date = pytz.utc.localize(input_date).astimezone(tz)
        date_without_tz = user_tz_date.replace(tzinfo=None)
        return str(date_without_tz)

    def invite_attendees(self):
        user_ids = []
        if self.member_ids:
            for member_id in self.member_ids:
                user_ids.append(member_id.user_id)
            for trainer_id in self.trainer_ids:
                user_ids.append(trainer_id.user_id)
        if user_ids:
            template_id = self.env.ref('dev_gym_management.template_special_session_arranged')
            for user_id in user_ids:
                if user_id.partner_id and user_id.partner_id.email:
                    template_id.write({'email_to': user_id.partner_id.email})
                    template_id.send_mail(self.id, force_send=True)
        self.state = 'sent'

    def cancel_notification(self):
        user_ids = []
        if self.member_ids:
            for member_id in self.member_ids:
                user_ids.append(member_id.user_id)
            for trainer_id in self.trainer_ids:
                user_ids.append(trainer_id.user_id)
        if user_ids:
            template_id = self.env.ref('dev_gym_management.template_special_session_canceled')
            for user_id in user_ids:
                if user_id.partner_id and user_id.partner_id.email:
                    template_id.write({'email_to': user_id.partner_id.email})
                    template_id.send_mail(self.id, force_send=True)

    def session_done(self):
        self.state = 'done'

    def set_to_pending(self):
        self.state = 'pending'

    name = fields.Char('Name')
    start_at = fields.Datetime(string='Start At')
    end_at = fields.Datetime(string='End At')
    member_ids = fields.Many2many('gym.member', string='Members')
    trainer_ids = fields.Many2many('gym.trainer', string='Trainer')
    description = fields.Text(string='Description')
    state = fields.Selection(selection=[('pending', 'Pending'),
                                        ('sent', 'Invitation Sent'),
                                        ('done', 'Done Successfully'),
                                        ('cancel', 'Canceled')], default='pending')
    cancel_reason = fields.Text(string='Cancel Reason')
    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.user.company_id)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: