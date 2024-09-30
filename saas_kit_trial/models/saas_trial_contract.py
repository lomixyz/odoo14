# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import fields, api, models, tools, _
from dateutil.relativedelta import relativedelta
from werkzeug.urls import url_encode
from odoo.exceptions import UserError, Warning, ValidationError
import random
from odoo.addons.auth_signup.models.res_partner import random_token as generate_token
from . lib import query
import datetime
import logging
_logger = logging.getLogger(__name__)


class SaaSTrialContract(models.Model):
    _inherit = 'saas.contract'

    is_trial_enabled = fields.Boolean(default=False, string="Is Trial", readonly=True)
    purchase_reminder_sent = fields.Boolean(default=False)
    reminder_show = fields.Boolean(default=False, compute="check_trial_expiry")
    state = fields.Selection(selection_add=[('trial_expired', 'Trial Expired'), ('trial_converted', 'Trial Closed')])
    converted_contract_id = fields.Many2one(comodel_name="saas.contract", string="Converted Contract")
    trial_started_date = fields.Date(string="Trial Start Date")
    trial_data_enabled = fields.Boolean(default=False)

    @api.model
    def check_trial_expiry(self):
        today_date = datetime.date.today()
        if self.is_trial_enabled and (self.state not in ['trial_converted', 'hold', 'expired', 'cancel']) and (today_date >= self.start_date):
            self.state = 'trial_expired'
            self.reminder_show = True
            return True
        else:
            self.reminder_show = self.reminder_show

    def purchase_reminder_reminder(self):
        IrDefault = self.env['ir.default'].sudo()
        auto_purchase_reminder = IrDefault.get('res.config.settings', 'auto_purchase_reminder')
        if auto_purchase_reminder:
            if self.check_trial_expiry():
                self.send_reminder()

    def send_reminder(self):
        for obj in self:
            template = self.env.ref('saas_kit_trial.saas_purchase_reminder_template')
            mail_id = template.send_mail(obj.id)
            current_mail = self.env['mail.mail'].browse(mail_id)
            current_mail.send()
            self.purchase_reminder_sent = True
            self.message_post(body="Purchase reminder has been sent to Client", subject="one")

    def get_contract_url(self):
        self.ensure_one()
        return "/my/saas/contracts"

    def create_saas_client(self):
        for obj in self:
            if not obj.domain_name:
                raise UserError("Please select a domain first!")
            if obj.under_process:
                raise UserError("Client Creation Already Under Progress!")
            else:
                domain_name = None
                if obj.use_separate_domain:
                    domain_name = obj.domain_name
                else:
                    domain_name = "{}.".format(obj.domain_name)   # is edited
                obj.under_process = True
                self._cr.commit()
                if obj.is_multi_server:
                    server_id = obj.plan_id.select_server()    # To select the server from multi server
                    if not server_id[0]:
                        obj.under_process = False
                        self._cr.commit()
                        raise UserError(server_id[1])
                    obj.write({
                        'server_id': server_id[1].id,
                        'saas_domain_url': server_id[1].server_domain,
                    })
                    obj._cr.commit()
                else:    
                    if obj.server_id.max_clients <= obj.server_id.total_clients:
                        obj.under_process = False
                        self._cr.commit()
                        raise UserError("Maximum Clients limit reached!")
                contracts = self.sudo().search([('domain_name', '=ilike', obj.domain_name), ('state', '!=', 'cancel')])
                if len(contracts) > 1:
                    _logger.info("---------ALREADY TAKEN--------%r", contracts)
                    obj.under_process = False
                    obj.domain_name = False
                    self._cr.commit()
                    raise UserError("This domain name is already in use! Please try some other domain name!")
                obj.under_process = True
                self._cr.commit()
                if not obj.use_separate_domain:
                    domain_name = domain_name+'{}'.format(obj.saas_domain_url)
                if obj.server_id.max_clients <= obj.server_id.total_clients:
                    obj.under_process = False
                    self._cr.commit()
                    raise UserError("Maximum Clients limit reached!")
                vals = dict(
                    saas_contract_id = obj.id,
                    partner_id = obj.partner_id and obj.partner_id.id or False,
                    server_id = obj.server_id.id,
                )
                client_id = self.env['saas.client'].create(vals)
                obj.attach_modules(client_id)
                obj.write({'saas_client': client_id.id})
                self._cr.commit()
                try:
                    client_id.fetch_client_url(domain_name)
                    _logger.info("--------Client--Created-------%r", client_id)
                except Exception as e:
                    obj.under_process = False
                    self._cr.commit()
                    _logger.info("--------Exception-While-Creating-Client-------%r", e)
                    raise UserError("Exceptionc While Creating Client {}".format(e))
                else:
                    obj.write({'state': 'open'})
                    obj.under_process = False
                    self._cr.commit()
                    if client_id.client_url:
                        try:
                            token = generate_token()
                            _logger.info("--------------%r", token)
                            obj.sudo().set_user_data(token=token)
                            obj.sudo().set_trial_data()
                            self._cr.commit()
                        except Exception as e:
                            _logger.info("--------EXCEPTION-WHILE-UPDATING-DATA-AND-SENDING-INVITE-------%r----", e)
                        else:
                            reset_pwd_url = "{}/web/signup?token={}&db={}".format(client_id.client_url, token, client_id.database_name)
                            client_id.invitation_url = reset_pwd_url
                            template = obj.on_create_email_template
                            mail_id = template.send_mail(client_id.id)
                            current_mail = self.env['mail.mail'].browse(mail_id)
                            res = current_mail.send()
                            obj.write({'state': 'confirm'})
                            self._cr.commit()
                            try:
                                if obj.from_backend:
                                    obj.generate_invoice(first_invoice=True)
                                elif obj.per_user_pricing:
                                    obj.update_billing_history(first=True)
                                    obj.previous_cycle_user = max(obj.min_users, obj.saas_users)
                            except Exception as e:
                                _logger.info("----------------  Exception While creating invoice-----------------")                            
                            return res

    def send_credential_email(self):
        self.ensure_one()
        if not self.saas_client.client_url:
            raise UserError("SaaS Instance Not Found! Please create it from the associated client record for sharing the credentials.")
        template = self.on_create_email_template
        compose_form = self.env.ref('mail.email_compose_message_wizard_form')


        if self.saas_client:
            try:
                token = generate_token()
                self.sudo().set_user_data(token=token)
                self.sudo().set_trial_data()
                self._cr.commit()
                reset_pwd_url = "{}/web/signup?token={}&db={}".format(self.saas_client.client_url, token, self.saas_client.database_name)
                self.saas_client.invitation_url = reset_pwd_url
            except Exception as e:
                _logger.info("--------EXCEPTION-WHILE-UPDATING-DATA-AND-SENDING-INVITE-------%r----", e)

        ctx = dict(
            default_model='saas.client',
            default_res_id=self.saas_client.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def set_trial_data(self):
        web_base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        web_base_url = web_base_url.replace('https://', '').replace('http://', '')
        web_base_url = 'http://'+web_base_url
        for obj in self:
            if hasattr(obj, 'is_trial_enabled'):
                trial_data = dict()
                trial_data['trial.is_trial_enabled'] = str(obj.is_trial_enabled)
                trial_data['trial.trial_period'] = str(obj.plan_id.trial_period)
                trial_data['trial.purchase_link'] = web_base_url+obj.get_contract_url()
                _, db_server = obj.plan_id.server_id.get_server_details()
                database = obj.saas_client and obj.saas_client.database_name or False
                response = query.set_trial_data(database, trial_data, db_server=db_server)
                if response:
                    obj.trial_data_enabled = True
                    self._cr.commit()
                    if not obj.is_trial_enabled:
                        try:
                            obj.saas_client.restart_client()
                        except:
                            raise UserError("Unable To Write Trial Data")
                    _logger.info("------------------  Trial Date Updated ------")
                else:
                    _logger.info("------------------  Trial Date Exception ------")
                    obj.trial_data_enabled = False
                    self._cr.commit()
                    raise UserError("Unable To Write Trial Data")

    def update_trial_data(self):
        """
        Called from The button "Set Trial Data in the Contract Form"
        """
        for obj in self:
            obj.sudo().set_trial_data()
