# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import AccessDenied, AccessError
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    traccar_server_url = fields.Char(string='Traccar server URL', help='Enter the URL of a Traccar server, this must be a valid http address.')
    traccar_username = fields.Char(string='Traccar username', help='Enter the username used to connect to Traccar.')
    traccar_password = fields.Char(string='Traccar password', help='Enter the password of a user used to connect to Traccar.')
    # gmaps_api_key = fields.Char(string='Google Maps API Key')
    # gmaps_theme = fields.Selection(
    #     selection=[('default', 'Default'),
    #                ('aubergine', 'Aubergine'),
    #                ('night', 'Night'),
    #                ('dark', 'Dark'),
    #                ('retro', 'Retro'),
    #                ('silver', 'Silver')],
    #     string='Map theme')
    add_to_odometer = fields.Boolean(string='Automatically increase vehicle odometer from GPS data')

    inactivity_period_duration = fields.Char(string='Inactivity Period Duration (min)',
                                  help='Enter a time interval which will be a threshold for the inactivity of a vehicle (in minutes).')
    do_reverse_geocoding = fields.Boolean(string='Retrieve an address after every location change (reverse geocoding - beware that this consumes a lot of GMaps API calls)', default=False)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            traccar_server_url=get_param('traccar_server_url'),
            traccar_username=get_param('traccar_username'),
            traccar_password=get_param('traccar_password'),
            # gmaps_api_key=get_param('google.api_key_geocode'),
            # gmaps_theme=get_param('google.maps_theme'),
            add_to_odometer=get_param('add_to_odometer'),
            inactivity_period_duration=get_param('inactivity_period_duration'),
            do_reverse_geocoding=get_param('do_reverse_geocoding'),
        )
        return res

    def set_values(self):
        if not self.user_has_groups('fleet.fleet_group_manager'):
            raise AccessDenied()
        super(ResConfigSettings, self).set_values()
        traccar_server_url = (self.traccar_server_url or '').strip()
        if traccar_server_url.endswith('/'):
            traccar_server_url = traccar_server_url[:-1]
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('traccar_server_url', traccar_server_url)
        set_param('traccar_username', (self.traccar_username or '').strip())
        set_param('traccar_password', (self.traccar_password or '').strip())
        # set_param('google.api_key_geocode', (self.gmaps_api_key or '').strip())
        # set_param('google.maps_theme', (self.gmaps_theme or '').strip())
        set_param('add_to_odometer', (self.add_to_odometer or False))
        set_param('inactivity_period_duration', (self.inactivity_period_duration or '30').strip())
        set_param('do_reverse_geocoding', (self.do_reverse_geocoding or False))

    def execute(self): # over-ride because of the warning 'Only administrators can change the settings'
        self.ensure_one()
        if not self.env.user._is_superuser() and not self.env.user.has_group('base.group_system')\
                and not self.env.user.has_group('fleet.fleet_group_manager'):
            raise AccessError(_("Only administrators can change the settings"))

        self = self.with_context(active_test=False)
        classified = self._get_classified_fields()

        # default values fields
        IrDefault = self.env['ir.default'].sudo()
        for name, model, field in classified['default']:
            if isinstance(self[name], models.BaseModel):
                if self._fields[name].type == 'many2one':
                    value = self[name].id
                else:
                    value = self[name].ids
            else:
                value = self[name]
            IrDefault.set(model, field, value)

        # # group fields: modify group / implied groups
        # with self.env.norecompute():
        #     for name, groups, implied_group in classified['group']:
        #         if self[name]:
        #             groups.write({'implied_ids': [(4, implied_group.id)]})
        #         else:
        #             groups.write({'implied_ids': [(3, implied_group.id)]})
        #             implied_group.write({'users': [(3, user.id) for user in groups.mapped('users')]})
        # self.recompute()

        # other fields: execute method 'set_values'
        # Methods that start with `set_` are now deprecated
        for method in dir(self):
            if method.startswith('set_') and method is not 'set_values':
                _logger.warning(_(
                    'Methods that start with `set_` are deprecated. Override `set_values` instead (Method %s)') % method)
        self.set_values()

        # module fields: install/uninstall the selected modules
        to_install = []
        to_uninstall_modules = self.env['ir.module.module']
        lm = len('module_')
        for name, module in classified['module']:
            if self[name]:
                to_install.append((name[lm:], module))
            else:
                if module and module.state in ('installed', 'to upgrade'):
                    to_uninstall_modules += module

        if to_uninstall_modules:
            to_uninstall_modules.button_immediate_uninstall()

        self._install_modules(to_install)

        if to_install or to_uninstall_modules:
            # After the uninstall/install calls, the registry and environments
            # are no longer valid. So we reset the environment.
            self.env.reset()
            self = self.env()[self._name]

        # pylint: disable=next-method-called
        config = self.env['res.config'].next() or {}
        if config.get('type') not in ('ir.actions.act_window_close',):
            return config

        # force client-side reload (update user menu and current view)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
