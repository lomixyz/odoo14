# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

import json
import logging
import requests
from werkzeug import urls

from odoo import api, fields, models, _
from odoo.addons.payment_tap.controllers.main import TapController
from odoo.addons.payment.models.payment_acquirer import _partner_split_name, ValidationError
from odoo.tools.float_utils import float_compare
from odoo.tools.misc import get_lang

_logger = logging.getLogger(__name__)


class PaymentAcquirerTap(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('tap', 'Tap')], ondelete={'tap': 'set default'})
    tap_secret_key = fields.Char(string='Secret Key', required_if_provider='tap', groups='base.group_user')
    tap_publishable_key = fields.Char(string='Publishable Key', required_if_provider='tap', groups='base.group_user')
    tap_payment_options = fields.Selection([
        ('src_all', 'All'),
        ('src_card', 'Card Payment'),
        ('src_kw.knet', 'KNET'),
        ('src_bh.benefit', 'BENEFIT'),
        ('src_sa.mada', 'MADA'),
        ('src_om.omannet', 'Oman Net'),
        ('src_apple_pay', 'Apple Pay')], string='Payment Options', required_if_provider='tap', default="src_all", groups='base.group_user')
    tap_use_3d_secure = fields.Boolean('Use 3D Secure', groups='base.group_user')

    @api.onchange('tap_use_3d_secure')
    def onchange_tap_use_3d_secure(self):
        if self.tap_use_3d_secure:
            if '(3D Secure)' not in self.name:
                self.name += '(3D Secure)'
        else:
            if '(3D Secure)' in self.name:
                self.name = self.name.replace('(3D Secure)', '')

    def _get_feature_support(self):
        res = super(PaymentAcquirerTap, self)._get_feature_support()
        res['fees'].append('tap')
        res['tokenize'].append('tap')
        return res

    def tap_compute_fees(self, amount, currency_id, country_id):
        if not self.fees_active:
            return 0.0
        country = self.env['res.country'].browse(country_id)
        if country and self.company_id.country_id.id == country.id:
            percentage = self.fees_dom_var
            fixed = self.fees_dom_fixed
        else:
            percentage = self.fees_int_var
            fixed = self.fees_int_fixed
        fees = (percentage / 100.0 * amount + fixed) / (1 - percentage / 100.0)
        return fees

    def _tap_requests(self, payload, endpoint, customer=False):
        url = "https://api.tap.company"
        headers = {
            'authorization': "Bearer %s" % self.tap_secret_key,
            'content-type': "application/json",
        }
        if customer:
            headers.update({'lang_code': get_lang(self.env, customer.lang).iso_code})
        response = requests.request("POST", url + endpoint, data=json.dumps(payload), headers=headers)
        res = response.json()
        if response.status_code != 200:
            errors = res.get('errors')
            error_msg = ', '.join(e.get('description') for e in errors)
            raise ValidationError(error_msg)
        return res

    def _tap_verify_card(self, values):
        url = "https://api.tap.company"
        headers = {
            'authorization': "Bearer %s" % self.tap_secret_key,
            'content-type': "application/json",
        }
        payload = {
            "currency": values.get('currency'),
            "threeDSecure": False,
            "save_card": True,
            "customer": {
                "id": values.get('customer_id')
            },
            "source": {
                "id": values.get('source_id')
            }
        }
        response = requests.post(url + "/v2/card/verify", data=json.dumps(payload), headers=headers)
        res = response.json()
        if response.status_code != 200:
            errors = res.get('errors')
            error_msg = ', '.join(e.get('description') for e in errors)
            raise ValidationError(error_msg)
        return res

    def _tap_create_charges(self, values):
        base_url = self.get_base_url()
        url = "https://api.tap.company"
        payload = {
            "amount": values.get('amount', 0.0),
            "currency": values['currency'] and values['currency'].name or "",
            "threeDSecure": self.tap_use_3d_secure,
            "save_card": False,
            "description": '%s: %s' % (self.company_id.name, values['reference']),
            "statement_descriptor": '%s: %s' % (self.company_id.name, values['reference']),
            "reference": {
                "transaction": values['reference'],
                "order": values['reference']
            },
            "customer": {
                "first_name": values.get('partner_first_name'),
                "last_name": values.get('partner_last_name'),
                "email": values.get('partner_email'),
                "phone": {
                    "country_code": values.get('partner_country') and values.get('partner_country').phone_code or "965",
                    "number": values.get('partner_phone')
                }
            },
            "source": {"id": self.tap_payment_options},
            "redirect": {"url": urls.url_join(base_url, TapController._return_url)}
        }
        headers = {
            'authorization': "Bearer %s" % self.tap_secret_key,
            'content-type': "application/json",
            'lang_code': get_lang(self.env, values.get('partner').lang).iso_code
        }
        response = requests.request("POST", url + "/v2/charges", data=json.dumps(payload), headers=headers)
        res = json.loads(response.text)
        return res

    def tap_form_generate_values(self, values):
        self.ensure_one()

        if self.tap_payment_options == 'src_card' and values['currency'].name not in ["AED", "BHD", "EGP", "EUR", "GBP", "KWD", "OMR", "QAR", "SAR", "USD"]:
            raise ValidationError("Tap payment gateway can not supports '%s' currency !" % values['currency'].name)
        if self.tap_payment_options == 'src_kw.knet' and values['currency'].name != "KWD":
            raise ValidationError("Tap payment gateway can not supports '%s' currency !" % values['currency'].name)
        if self.tap_payment_options == 'src_kw.mada' and values['currency'].name != "SAR":
            raise ValidationError("Tap payment gateway can not supports '%s' currency !" % values['currency'].name)
        if self.tap_payment_options == 'src_kw.benefit' and values['currency'].name != "BHD":
            raise ValidationError("Tap payment gateway can not supports '%s' currency !" % values['currency'].name)
        if self.tap_payment_options == 'src_kw.omannet' and values['currency'].name != "OMR":
            raise ValidationError("Tap payment gateway can not supports '%s' currency !" % values['currency'].name)

        res = self._tap_create_charges(values)
        _logger.info("Respones from Tap : %s" % res)
        error_msg = ''
        if res.get('errors'):
            error_msg += '\n'.join(error.get('code') + ' - ' + error.get('description') for error in res.get('errors'))
        if error_msg != '':
            raise ValidationError(error_msg)
        url = res.get('transaction').get('url')
        _logger.info("Tap payment post URL : %s" % url)
        values.update({
            'form_url': url,
        })
        return values

    @api.model
    def tap_s2s_form_process(self, data):
        values = {
            'cc_number': data.get('cc_number'),
            'cc_cvc': int(data.get('cc_cvc')),
            'cc_holder_name': data.get('cc_holder_name'),
            'cc_expiry': data.get('cc_expiry'),
            'cc_brand': data.get('cc_brand'),
            'acquirer_id': int(data.get('acquirer_id')),
            'partner_id': int(data.get('partner_id'))
        }
        payment_token = self.env['payment.token'].sudo().create(values)
        return payment_token

    def tap_s2s_form_validate(self, data):
        error = dict()
        mandatory_fields = ["cc_number", "cc_cvc", "cc_holder_name", "cc_expiry", "cc_brand"]
        # Validation
        for field_name in mandatory_fields:
            if not data.get(field_name):
                error[field_name] = 'missing'

        return False if error else True


class PaymentTransactionTap(models.Model):
    _inherit = 'payment.transaction'

    state = fields.Selection(selection_add=[('refund_initiate', 'Refund Initiate'), ('refunded', 'Refunded')], ondelete={'refund_initiate': 'set default', 'refunded': 'set default'})
    refund_acquirer_reference = fields.Char(string='Refund Reference', readonly=True, help='Reference of the refund as stored in the acquirer database')
    refund_initiated_date = fields.Datetime('Refund Initiated Date', readonly=True)
    refund_date = fields.Datetime('Refund Date', readonly=True)
    tap_payment_method = fields.Char('Tap Payment Method')

    @api.model
    def _tap_form_get_tx_from_data(self, data):
        reference = data.get('reference').get('transaction')
        if not reference:
            error_msg = 'Tap: received data with missing reference (%s)' % reference
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        tx = self.env['payment.transaction'].search([('reference', '=', reference)])

        if not tx or len(tx) > 1:
            error_msg = 'Tap: received data for reference %s' % (reference)
            if not tx:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return tx[0]

    def _tap_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        # check what is buyed
        if float_compare(float(data.get('amount', '0.0')), self.amount, 2) != 0:
            invalid_parameters.append(('Amount', data.get('amount'), '%.2f' % self.amount))
        if data.get('currency') != self.currency_id.name:
            invalid_parameters.append(('currency', data.get('currency'), self.currency_id.name))
        return invalid_parameters

    def _tap_form_validate(self, data):
        if data.get('object') == 'charge':
            if self.state == 'done':
                _logger.warning('Tap: trying to validate an already validated tx (ref %s)' % self.reference)
                return True
            status_code = data.get('response').get('code')
            self.write({
                'acquirer_reference': data.get('id'),
                'date': fields.Datetime.now()
            })
            if data.get('source'):
                if data['source'].get('payment_method'):
                    self.write({'tap_payment_method': data['source']['payment_method']})
            if status_code == '000':
                self._set_transaction_done()
            elif status_code == '001':
                self._set_transaction_authorized()
            elif status_code in ['100', '200']:
                self._set_transaction_pending()
            elif status_code in ['301', '302']:
                self._set_transaction_cancel()
            else:
                error = data.get('response').get('message')
                _logger.info(error)
                self.write({
                    'state_message': error,
                })
                self._set_transaction_error(msg=error)
        elif data.get('object') == 'refund':
            if self.state == 'refunded':
                _logger.warning('Tap: trying to refund an already refunded tx (ref %s)' % self.reference)
                return True
            status_code = data.get('response').get('code')
            self.write({
                'refund_acquirer_reference': data.get('id')
            })
            if status_code == '000':
                self.write({'state': 'refunded', 'refund_date': fields.Datetime.now()})
            elif status_code in ['100', '200']:
                self.write({'state': 'refund_initiate', 'refund_initiated_date': fields.Datetime.now()})

    # --------------------------------------------------
    # S2S RELATED METHODS
    # --------------------------------------------------
    def tap_s2s_do_transaction(self, **kwargs):
        acquirer = self.acquirer_id

        if self.currency_id.name not in ["AED", "BHD", "EGP", "EUR", "GBP", "KWD", "OMR", "QAR", "SAR", "USD"]:
            raise ValidationError("Tap payment gateway can not supports '%s' currency !" % self.currency_id.name)

        kwargs.update({
            'currency': self.currency_id.name,
            'customer_id': self.payment_token_id.tap_customer_id,
            'source_id': self.payment_token_id.tap_card_token_id
        })

        saved_card_token_payload = {
            "saved_card": {
                "card_id": self.payment_token_id.acquirer_ref,
                "customer_id": self.payment_token_id.tap_customer_id
            }
        }
        save_card_token_resp = acquirer._tap_requests(saved_card_token_payload, "/v2/tokens", self.partner_id)

        save_card_payload = {
            "source": save_card_token_resp.get('id')
        }
        acquirer._tap_requests(save_card_payload, "/v2/card/%s" % self.payment_token_id.tap_customer_id, self.partner_id)

        headers = {
            'authorization': "Bearer %s" % acquirer.tap_secret_key,
            'content-type': "application/json",
            'lang_code': get_lang(self.env, self.partner_id.lang).iso_code
        }
        url = "https://api.tap.company/v2/charges"
        payload = {
            "amount": self.amount,
            "currency": self.currency_id.name,
            "threeDSecure": False,
            "save_card": True,
            "description": self.reference,
            "statement_descriptor": self.reference,
            "reference": {
                "transaction": self.id,
                "order": self.reference
            },
            "receipt": {
                "email": False,
                "sms": False
            },
            "customer": {
                "id": self.payment_token_id.tap_customer_id
            },
            "source": {"id": save_card_token_resp.get('id')},
            "post": {"url": kwargs.get('return_url', False)},
            "redirect": {"url": kwargs.get('return_url', False)}
        }
        res = requests.request("POST", url, data=json.dumps(payload), headers=headers)
        response = json.loads(res.text)
        return self._tap_form_validate(response)

    def _create_tap_refund(self):
        acquirer = self.acquirer_id
        base_url = acquirer.get_base_url()
        headers = {
            'authorization': "Bearer %s" % acquirer.tap_secret_key,
            'content-type': "application/json",
            'lang_code': get_lang(self.env, self.partner_id.lang).iso_code
        }
        url = "https://api.tap.company/v2/refunds"
        payload = {
            "charge_id": self.acquirer_reference,
            "amount": self.amount,
            "currency": self.currency_id.name,
            "description": self.reference,
            "reason": "requested_by_customer",
            "reference": {
              "merchant": self.reference
            },
            "metadata": {
              "udf1": self.id,
              "udf2": acquirer.id
            },
            "post": {"url": urls.url_join(base_url, TapController._refund_url)},
        }
        response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
        result = response.json()
        return result

    def tap_s2s_do_refund(self, **kwargs):
        self.ensure_one()
        result = self._create_tap_refund()
        return self._tap_form_validate(result)

    def action_refund(self):
        for tx in self:
            result = tx._create_tap_refund()
            tx._tap_form_validate(result)

    @api.model
    def cron_tap_refund(self):
        txs = self.search([('provider', '=', 'tap'), ('state', '=', 'refund_initiate'), ('refund_acquirer_reference', '!=', False)])
        for tx in txs:
            headers = {
                'authorization': "Bearer %s" % tx.acquirer_id.tap_secret_key,
                'content-type': "application/json",
            }
            response = requests.request("GET", "https://api.tap.company/v2/refunds/%s" % tx.refund_acquirer_reference, headers=headers)
            res = response.json()
            tx._tap_form_validate(res)


class PaymentToken(models.Model):
    _inherit = 'payment.token'

    provider = fields.Selection(string='Provider', related='acquirer_id.provider', readonly=False)
    tap_customer_id = fields.Char('Customer ID')
    tap_card_token_id = fields.Char('Card Token ID')

    @api.model
    def tap_create(self, values):
        if values.get('cc_number') and not values.get('acquirer_ref'):
            values['cc_number'] = values['cc_number'].replace(' ', '')
            partner_id = self.env['res.partner'].browse(values.get('partner_id'))
            payment_acquirer = self.env['payment.acquirer'].browse(values.get('acquirer_id'))

            # create customer to tap
            fname = _partner_split_name(partner_id.name)[0]
            lname = _partner_split_name(partner_id.name)[1]
            customer_payload = {
                "first_name": fname,
                "last_name": fname if not lname else lname,
                "email": partner_id.email,
                "phone": {
                    "country_code": partner_id.country_id and partner_id.country_id.phone_code or "965",
                    "number": partner_id.phone
                },
                "metadata": {
                    "udf1": partner_id.id
                }
            }
            cust_resp = payment_acquirer._tap_requests(customer_payload, "/v2/customers")
            # create card to tap
            card_token_payload = {
                "card": {
                    "number": values.get('cc_number'),
                    "exp_month": int(values['cc_expiry'][:2]),
                    "exp_year": int(values['cc_expiry'][-2:]),
                    "cvc": int(values.get('cc_cvc'))
                }
            }
            card_token_resp = payment_acquirer._tap_requests(card_token_payload, "/v2/tokens")
            verify_data = {
                'currency': self.env.company.currency_id.name,
                'customer_id': cust_resp.get('id'),
                'source_id': card_token_resp.get('id')
            }
            verify_resp = payment_acquirer._tap_verify_card(verify_data)
            if verify_resp.get('status') != 'VALID':
                raise ValidationError(_('Tap payment gateway is not able to verify your card, please try after some time or try with new card!'))
            return {
                'verified': True,
                'tap_customer_id': cust_resp.get('id'),
                'tap_card_token_id': card_token_resp.get('id'),
                'acquirer_ref': card_token_resp.get('card').get('id'),
                'name': 'XXXXXXXXXXXX%s - %s' % (values['cc_number'][-4:], values['cc_holder_name'])
            }
        return values
