# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO Open Source Management Solution
#
#    ODOO Addon module by Sprintit Ltd
#    Copyright (C) 2021 Sprintit Ltd (<http://sprintit.fi>).
#
##############################################################################

import logging
logger = logging.getLogger(__name__)

from odoo import models, fields, api, _
from datetime import datetime


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    for_approval_menu = fields.Boolean('For Approval Menu', copy=False)
    approved_date = fields.Datetime('Approved Date', copy=False)
    action_by_user_id = fields.Many2one('res.users', string="Approved or Rejected By", copy=False)
        
    def approve_user(self):
        self.write({'approved_date':datetime.now(), 'active':True, 'action_by_user_id': self._uid})
        channel_for_approval = self.env.ref('sprintit_website_signup.channel_for_approval_users')
        channel_for_approval.message_post(
                            body=_("<b>%s User Approved by %s</b>" % (self.name, self.env.user.name)), subject=_('User Approval'),
                            subtype_xmlid='mail.mt_comment', message_type='comment', content_subtype='html')
        self.partner_id.active = True
        template = self.env.ref('sprintit_website_signup.mail_template_user_signup_account_approved', raise_if_not_found=False)
        if template:
            template.sudo().with_context(
                lang=self.lang,
                auth_login=self.login,
            ).send_mail(self.id, force_send=True)
        
    def reject_user(self):
        self.write({'active':False, 'action_by_user_id': self._uid})
        channel_for_approval = self.env.ref('sprintit_website_signup.channel_for_approval_users')
        channel_for_approval.message_post(
                            body=_("<b>%s User Rejected by %s</b>" % (self.name, self.env.user.name)), subject=_('User Rejected'),
                            subtype_xmlid='mail.mt_comment', message_type='comment', content_subtype='html')
        self.partner_id.active = False
        template = self.env.ref('sprintit_website_signup.mail_template_user_signup_account_rejected', raise_if_not_found=False)
        if template:
            template.sudo().with_context(
                lang=self.lang,
                auth_login=self.login,
            ).send_mail(self.id, force_send=True)
