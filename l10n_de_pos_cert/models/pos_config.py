# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError, UserError
import uuid
from random import choice


class PosConfig(models.Model):
    _inherit = 'pos.config'
    # Due to the new broken changes of the Fiskaly API, only the v2 of the api is compliant. This version introduced two new fields that cannot be
    # added in stable. Therefore the `l10n_de_fiskaly_tss_id` will be composed of `tss_id|tss_puk|tss_pin`
    l10n_de_fiskaly_tss_id = fields.Char(string="TSS ID", readonly=True, copy=False, help="The TSS ID at Fiskaly side linked to the pos.config. "
                                         "Due to some new broken changes, this field also includes the tss puk and pin separated by `|`")
    l10n_de_fiskaly_client_id = fields.Char(string="Client ID", readonly=True, copy=False,
                                            help="The Client ID refers to the client at Fiskaly which is mapped to a pos.config.")
    l10n_de_create_tss_flag = fields.Boolean(string="Create TSS", help="This allows to send a request to Fiskaly in order to create and link a TSS to the pos.config")
    is_company_country_germany = fields.Boolean(string="Company located in Germany", related='company_id.is_country_germany')

    def _l10n_de_check_fiskaly_api_key_secret(self):
        if not self.company_id.sudo().l10n_de_fiskaly_api_key or not self.company_id.sudo().l10n_de_fiskaly_api_secret:
            raise UserError(_("You have to set your Fiskaly key and secret in your company settings."))

    def _l10n_de_check_fiskaly_tss_client_ids(self):
        if not self.l10n_de_fiskaly_tss_id or not self.l10n_de_fiskaly_client_id:
            raise UserError(_("You have to set your Fiskaly TSS ID and Client ID in your PoS settings."))

    def _l10n_de_get_tss_id(self):
        return self.l10n_de_fiskaly_tss_id.split('|')[0]

    def open_ui(self):
        if not self.company_id.country_id:
            raise UserError(_("You have to set a country in your company setting."))
        if self.company_id.l10n_de_is_germany_and_fiskaly():
            self._l10n_de_check_fiskaly_api_key_secret()
            self._l10n_de_check_fiskaly_tss_client_ids()
        return super().open_ui()

    @api.model
    def l10n_de_get_fiskaly_urls_and_keys(self, config_id):
        self.check_access_rights('read')
        company = self.browse(config_id).company_id.sudo()
        return {
            'kassensichv_url': self.env['res.company']._l10n_de_fiskaly_kassensichv_url(),
            'dsfinvk_url': self.env['res.company']._l10n_de_fiskaly_dsfinvk_api_url(),
            'api_key': company.l10n_de_fiskaly_api_key,
            'api_secret': company.l10n_de_fiskaly_api_secret
        }

    @api.model
    def create(self, values):
        res = super().create(values)
        if values.get('l10n_de_create_tss_flag') is True:
            res._l10n_de_create_tss_process()
        return res

    def write(self, values):
        res = super().write(values)
        if values.get('l10n_de_create_tss_flag') is True:
            for config in self:
                config._l10n_de_create_tss_process()
        return res

    def unlink(self):
        # Those values are needed when disabling a TSS at Fiskaly, we store them before deleting the configs
        tss_to_disable_data = [(config.company_id, config.l10n_de_fiskaly_tss_id)
                               for config in self if config.l10n_de_create_tss_flag]
        res = super().unlink()

        # We want to first delete them in Odoo in case there's an issue and since we can't rollback with Fiskaly
        for tss_data in tss_to_disable_data:
            pos_config, tss_id_admin_puk_pin = tss_data
            tss_id = tss_id_admin_puk_pin.split('|')[0]
            # We differentiate if the TSS was created under the v2 or v1 api
            if '|' in tss_id_admin_puk_pin:
                admin_pin = tss_id_admin_puk_pin.split('|')[2]
                pos_config._l10n_de_fiskaly_kassensichv_rpc('POST', '/tss/%s/admin/auth' % tss_id, {'admin_pin': admin_pin})
                pos_config._l10n_de_fiskaly_kassensichv_rpc('PATCH', '/tss/%s' % tss_id, {'state': 'DISABLED'})
            else:
                pos_config._l10n_de_fiskaly_kassensichv_rpc('PUT', '/tss/%s' % tss_id, {'state': 'DISABLED'}, version=1)

        return res

    def _l10n_de_create_tss_process(self):
        tss_id = str(uuid.uuid4())
        local_tss = self.search([('company_id', '=', self.company_id.id), ('l10n_de_fiskaly_tss_id', '!=', False)])
        db_uuid = self.env['ir.config_parameter'].sudo().get_param('database.uuid')
        self.company_id._l10n_de_fiskaly_iap_rpc('/tss', {'tss_id': tss_id, 'db_uuid': db_uuid, 'tss': len(local_tss)})
        self._create_tss_v2(tss_id)

    def open_session_cb(self):
        # Due to the new release of the Fiskaly api v2, we need to create the new TSS
        # Here we check if the TSS has been created under V2 otherwise we create it
        if self.is_company_country_germany and self.l10n_de_create_tss_flag and '|' not in self.l10n_de_fiskaly_tss_id:
            # Disable the TSS created under v1
            self.company_id._l10n_de_fiskaly_kassensichv_rpc('PUT', '/tss/%s' % self._l10n_de_get_tss_id(),
                                                             {'state': 'DISABLED'}, version=1)
            self._create_tss_v2()

        # Since we cannot modify fields when there's an open session, we hope that the checks of the parent method
        # pass... If there's a v1 TSS, we can assume that the checks should pass
        return super().open_session_cb()

    def _create_tss_v2(self, tss_id=None):
        # this method shall be deleted along with the override of open_session_cb in v16
        tss_id = tss_id if tss_id else str(uuid.uuid4())
        tss_creation_resp = self.company_id._l10n_de_fiskaly_kassensichv_rpc('PUT', '/tss/%s' % tss_id, {}) # Yes, Fiskaly is asking for a empty object...
        tss_puk = tss_creation_resp.json()['admin_puk']
        self.company_id._l10n_de_fiskaly_kassensichv_rpc('PATCH', '/tss/%s' % tss_id, {'state': 'UNINITIALIZED'})
        tss_pin = ''.join(choice('0123456789') for _ in range(6))
        self.company_id._l10n_de_fiskaly_kassensichv_rpc('PATCH', '/tss/%s/admin' % tss_id,
                                                         {'admin_puk': tss_puk, 'new_admin_pin': tss_pin})
        self.company_id._l10n_de_fiskaly_kassensichv_rpc('POST', '/tss/%s/admin/auth' % tss_id, {'admin_pin': tss_pin})
        self.company_id._l10n_de_fiskaly_kassensichv_rpc('PATCH', '/tss/%s' % tss_id, {'state': 'INITIALIZED'})

        # Client
        client_id = str(uuid.uuid4())
        self.company_id._l10n_de_fiskaly_kassensichv_rpc('PUT', '/tss/%s/client/%s' % (tss_id, client_id), {'serial_number': self.uuid})
        self.company_id._l10n_de_fiskaly_kassensichv_rpc('POST', '/tss/%s/admin/logout' % tss_id, {'admin_pin': tss_pin})

        self.write({'l10n_de_fiskaly_tss_id': '|'.join([tss_id, tss_puk, tss_pin]), 'l10n_de_fiskaly_client_id': client_id})
