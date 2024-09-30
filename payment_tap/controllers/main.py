# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

import json
import logging
import pprint
import requests
import werkzeug

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class TapController(http.Controller):
    _return_url = '/payment/tap/return/'
    _refund_url = '/payment/tap/refund/'

    @http.route(_return_url, type='http', auth='public', csrf=False)
    def tap_return_feedback(self, **post):
        tap_id = http.request.params.get('tap_id')
        url = "https://api.tap.company/v2/charges/%s" % tap_id
        acquirer_id = request.env['payment.acquirer'].sudo().search([('provider', '=', 'tap')], limit=1)
        headers = {'authorization': 'Bearer %s' % acquirer_id.tap_secret_key}
        response = requests.request("GET", url, data="{}", headers=headers)
        data = json.loads(response.text)
        _logger.info('Tap: entering return feedback with post data %s', pprint.pformat(data))
        request.env['payment.transaction'].sudo().form_feedback(data, 'tap')
        return werkzeug.utils.redirect('/payment/process')

    @http.route(['/payment/tap/s2s/create_json'], type='json', auth='public', csrf=False)
    def tap_s2s_create_json(self, **kwargs):
        if not kwargs.get('partner_id'):
            kwargs = dict(kwargs, partner_id=request.env.user.partner_id.id)
        acquirer = request.env['payment.acquirer'].browse(int(kwargs.get('acquirer_id'))).s2s_process(kwargs)
        return acquirer.id

    @http.route([_refund_url], type='json', auth='public', csrf=False)
    def tap_payment_refund(self, **post):
        tx = request.env['payment.transaction'].browse(int(post.get('metadata').get('udf1')))
        tx._tap_form_validate(post)
        return tx.id
