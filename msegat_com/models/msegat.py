# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.addons.iap import jsonrpc, InsufficientCreditError
from odoo.exceptions import UserError, ValidationError, Warning
import logging
from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests
import json

_logger = logging.getLogger(__name__)

class Msegat(models.Model):
    _name = 'msegat.sms'
    _description = 'Msegat SMS Odoo Integration'

    numbers = fields.Many2many("res.partner", string="Partners")
    message = fields.Text("Content")
    state = fields.Selection([('sent', 'Sent'), ('fail', 'Failed'), ('draft', 'Draft')], default='draft')
    message_log = fields.Text(string="Message Log")

    def action_cancel(self):
        self.write({"state": "draft","message_log":""})

    def action_send_sms(self):
        username = self.env['ir.config_parameter'].sudo().get_param('msegat.username')
        sender   = self.env['ir.config_parameter'].sudo().get_param('msegat.sender')
        api_key  = self.env['ir.config_parameter'].sudo().get_param('msegat.api_key')

        if self.numbers:
            numbers = []
            for contact in self.numbers:
                if contact.phone:
                    numbers += [contact.phone.strip().replace("-","").replace("(","").replace(")","")]
                if contact.mobile:
                    numbers += [contact.mobile.strip().replace("-","").replace("(","").replace(")","")]
        if numbers == []:
            raise ValidationError(_("please fill the destination numbers"))

        values = {
          "userName": username,
          "numbers": ",".join(numbers),
          "userSender": sender,
          "apiKey": api_key,
          "msg": self.message
          }

        headers = { 'Content-Type': 'application/json' }

        try:
            response = requests.post('https://www.msegat.com/gw/sendsms.php', data=json.dumps(values), headers=headers)
        except requests.exceptions.ConnectionError as ops:
            log =  ops.with_traceback
            self.write({"state": "fail", "message_log": log })
            return False

        if response.status_code == 200:
            result = response.json()
            if result['message'] == "Success":
                self.write({"state": "sent", "message_log": response.text})
            else:
                self.write({"state": "fail", "message_log": result['message'] })
            return True
        else:
            _logger.warning(values)
            log =  "status code :"+str(response.status_code) +"\nheaders : "+response.headers+"\nbody : " + resposne.text
            self.write({"state": "fail", "message_log": log })
            return False

    def action_calculate_cost(self):
        username = self.env['ir.config_parameter'].sudo().get_param('msegat.username')
        sender   = self.env['ir.config_parameter'].sudo().get_param('msegat.sender')
        api_key  = self.env['ir.config_parameter'].sudo().get_param('msegat.api_key')

        if self.numbers:
            numbers = []
            for contact in self.numbers:
                if contact.phone:
                    numbers += [contact.phone.strip().replace("-","").replace("(","").replace(")","")]
                if contact.mobile:
                    numbers += [contact.mobile.strip().replace("-","").replace("(","").replace(")","")]
        if numbers == []:
            raise ValidationError(_("please fill the destination numbers"))

        values = { "userName": username,
                   "apiKey"  : api_key,
                   "contactType": "numbers",
                   "contacts": ",".join(numbers),
                   "msg": self.message,
                   "By": "Link",
                   "msgEncoding": "UTF-8"
                   }
        mp_encoder = MultipartEncoder(fields=values)
        headers  = {'Content-Type': mp_encoder.content_type}

        try:
            response = requests.post('https://www.msegat.com/gw/calculateCost.php', data=mp_encoder, headers=headers)
        except requests.exceptions.ConnectionError as ops:
            log =  ops.with_traceback
            self.write({"state": "fail", "message_log": log })
            _logger.warning(log)
            return False

        if response.status_code == 200:
            total_numbers = response.text.split(",")[0]
            total_cost = response.text.split(",")[1]
            raise Warning(_("total numbers : %s number\ntotal cost : %s point") % (total_numbers,total_cost) )
            return True
        else:
            log =  "status code :"+str(response.status_code) +"\nheaders : "+response.headers+"\nbody : " + resposne.text
            self.write({"state": "fail", "message_log": log })
            _logger.warning(log)
            return False

