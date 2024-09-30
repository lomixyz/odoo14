# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO Open Source Management Solution
#
#    ODOO Addon module by Sprintit Ltd
#    Copyright (C) 2021 Sprintit Ltd (<http://sprintit.fi>).
#
##############################################################################

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auth_signup_approval = fields.Boolean(string='Signup Approval Needed?')
    
    @api.onchange('auth_signup_uninvited')
    def onchange_auth_signup_uninvited(self):
        self.auth_signup_approval = False if self.auth_signup_uninvited == 'b2b' else self.auth_signup_approval
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            auth_signup_approval=True if get_param('auth_signup.signup_approval', 'False').lower() == 'true' else False,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('auth_signup.signup_approval', self.auth_signup_approval)