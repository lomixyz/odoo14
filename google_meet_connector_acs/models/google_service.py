# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

TIMEOUT = 20


class GoogleService(models.AbstractModel):
    _inherit = 'google.service'

    @api.model
    def _do_request(self, uri, params=None, headers=None, method='POST', preuri="https://www.googleapis.com", timeout=TIMEOUT):
        split_vals = uri.split('/')
        if split_vals and 'calendars' in split_vals and ('events' in split_vals or 'events?sendUpdates=all' in split_vals):
            if 'sendUpdates' in uri:
                # sendNotifications Parameter is deprecated,sendUpdates=all is now recommended to use. this can be a
                # conflict in the future, try removing sendNotifications.
                uri = uri + '&conferenceDataVersion=1&sendNotifications=True'
            else:
                uri = uri + '?conferenceDataVersion=1&sendNotifications=True'
        res = super(GoogleService, self)._do_request(uri=uri, params=params, headers=headers, method=method, preuri=preuri, timeout=timeout)
        return res
