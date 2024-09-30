# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api

 
class ResUsers(models.Model):
    _inherit = 'res.users'

    sh_portal_user = fields.Boolean(
        string='Portal', compute='_compute_sh_portal_user', search='_search_sh_portal_user')
    sh_portal_user_access = fields.Selection([('user', 'Portal Support User'), (
        'manager', 'Portal Manager'), ('leader', 'Portal Leader')], string='Portal Access')
    sign = fields.Text('Signature')

    def __init__(self, pool, cr):
        """ Override of _init_ to add access rights on sign
            Access rights are disabled by default, but allowed
            on some specific fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        init_res = super(ResUsers, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        type(self).SELF_WRITEABLE_FIELDS.extend(['sign'])
        # duplicate list to avoid modifying the original reference
        type(self).SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        type(self).SELF_READABLE_FIELDS.extend(['sign'])
        return init_res

    @api.depends('groups_id')
    def _compute_sh_portal_user(self):
        if self:
            for rec in self:
                if self.env.ref('base.group_portal').id in rec.groups_id.ids:
                    rec.sh_portal_user = True
                else:
                    rec.sh_portal_user = False

    def _search_sh_portal_user(self, operator, value):
        user_obj = self.env['res.users']
        domain = []
        domain.append(('sh_portal_user', operator, value))
        users = user_obj.sudo().search(domain).ids
        if users:
            return [('id', 'in', users)]
        else:
            return []

class UserApiKey(models.Model):
    _inherit = 'res.users.apikeys'

    sign = fields.Text('Signature')
