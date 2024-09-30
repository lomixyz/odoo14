# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests
import logging
import json

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    msegat_username = fields.Char("Msegat Username",config_parameter="msegat.username")
    msegat_api_key = fields.Char("Msegat api key", config_parameter="msegat.api_key")
    msegat_sender = fields.Char("Msegat sender", config_parameter="msegat.sender")
    msegat_balance = fields.Char("Msegat balance", config_parameter="msegat.balance")

    def action_msegat_balance_inquiry(self):
        username = self.env['ir.config_parameter'].sudo().get_param('msegat.username')
        sender   = self.env['ir.config_parameter'].sudo().get_param('msegat.sender')
        api_key  = self.env['ir.config_parameter'].sudo().get_param('msegat.api_key')

        values = {'userName': username,"apiKey": api_key,"msgEncoding":"UTF-8"}
        mp_encoder = MultipartEncoder( fields=values)
        headers  = {'Content-Type': mp_encoder.content_type}

        try:
            response  = requests.post( 'https://www.msegat.com/gw/Credits.php', data=mp_encoder, headers=headers)
        except requests.exceptions.ConnectionError as ops:
            log =  ops.with_traceback
            _logger.warning(response.text)
            self.write({"state": "fail", "message_log": log })

        if response.status_code == 200:
            self.env['ir.config_parameter'].sudo().set_param('msegat.balance',response.text)
            return True
        else:
            log =  "status code :"+str(response.status_code) +"\nheaders : "+response.headers+"\nbody : " + resposne.text
            self.write({"state": "fail", "message_log": log })
