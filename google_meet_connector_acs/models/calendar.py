# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import string
import requests
import random
from odoo import api, fields, models, _

def status_response(status):
    return int(str(status)[0]) == 2


class Meeting(models.Model):
    _inherit = "calendar.event"

    hangout_url = fields.Char('Meet URL')
    request_id = fields.Char('Request ID', readonly=False)
    meeting_code = fields.Char('Conference Code', readonly=True)
    conference_type = fields.Selection([
        ('hangoutsMeet', 'Google Meeting')], string='Conference Type')

    @api.onchange('conference_type')
    def onchange_conference_type(self):
        self.request_id = False
        self.hangout_url = False
        self.meeting_code = False
        if self.conference_type:
            self.request_id = ''.join(random.choice(string.ascii_uppercase + \
                string.digits + string.ascii_lowercase) for _ in range(32))

    def join_hangouts(self):
        return {
            'type': 'ir.actions.act_url',
            'url': self.hangout_url,
            'target': 'new',
            'nodestroy': False,
        }

    def write(self, vals):
        if 'conference_type' in vals.keys() and not vals['conference_type']:
            vals['hangout_url'] = False
            vals['request_id'] = False
            vals['meeting_code'] = False
        return super(Meeting, self).write(vals)

    # def _check_email(self):
    #     """
    #         This Method used for conferenceType G Suite users and normal user.
    #     """
    #     status, current_google, ask_time = self.get_calendar_primary_id()
    #     conferenceType = None
    #     if current_google and self.conference_type == 'eventHangout':
    #         gc_email = current_google
    #         if gc_email:
    #             domain = 'gmail.com'
    #             email_domain = gc_email.split("@")[-1]
    #             if email_domain == domain:
    #                 conferenceType = 'eventHangout'
    #             else:
    #                 conferenceType = 'eventNamedHangout'
    #     elif self.conference_type == 'hangoutsMeet':
    #         conferenceType = 'hangoutsMeet'
    #     return conferenceType

    def _google_values(self):
        values = super(Meeting, self)._google_values()
        values["conferenceData"] = None
        conferenceType = 'hangoutsMeet'
        if conferenceType:
            values['conferenceDataVersion'] = 1
            values["conferenceData"] = {"createRequest": {"conferenceSolutionKey": {'type': conferenceType}, 'requestId': self.request_id}}
        return values

    @api.model
    def _odoo_values(self, google_event, default_reminders=()):
        values = super(Meeting, self)._odoo_values(google_event=google_event, default_reminders=default_reminders)
        conferenceData = google_event.conferenceData
        conference_type = conferenceData and conferenceData.get('conferenceSolution') and conferenceData.get('conferenceSolution').get('key') and conferenceData.get('conferenceSolution').get('key').get('type') or False
        if conference_type and conference_type != 'hangoutsMeet':
            conference_type = 'hangoutsMeet'
        values.update({
            'conference_type': conference_type,
            'meeting_code': conferenceData and conferenceData.get('conferenceId'),
            'hangout_url': google_event.hangoutLink,
            'request_id': conferenceData and conferenceData.get('createRequest') and conferenceData.get('createRequest').get('requestId') or False
        })
        return values

    @api.model
    def _get_google_synced_fields(self):
        values = super(Meeting, self)._get_google_synced_fields()
        values.add('conference_type')
        return values

    def get_calendar_primary_id(self):
        """ In google calendar, you can have multiple calendar. But only one is
            the 'primary' one. This Calendar identifier is 'primary'.
        """
        params = {
            'fields': 'id',
            'access_token': self.env.user._get_google_calendar_token()
        }
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        url = "/calendar/v3/calendars/primary"

        try:
            status, content, ask_time = self.env['google.service']._do_request(url, params=params, headers=headers, method='GET')
        except requests.HTTPError as e:
            if e.response.status_code == 401:  # Token invalid / Acces unauthorized
                error_msg = _("Your token is invalid or has been revoked !")

                self.env.user.write({'google_calendar_token': False, 'google_calendar_token_validity': False})
                self.env.cr.commit()

                raise self.env['res.config.settings'].get_config_warning(error_msg)
            raise

        return (status_response(status), content['id'] or False, ask_time)
