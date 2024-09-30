# -*- coding: utf-8 -*-

import json
import pytz

from odoo import http
from odoo.addons.http_routing.models.ir_http import url_for
from odoo.http import request
from odoo.tools import ustr
from odoo.modules.module import get_module_resource


class KsPwaController(http.Controller):

    @http.route('/ks_curved_backend_theme/get_manifest', type='http', auth='public', methods=['GET'],
                sitemap=False)
    def ks_get_pwa_manifest(self):
        ks_enable_pwa_app = request.env['ir.config_parameter'].sudo().get_param(
            'ks_curved_backend_theme.ks_enable_pwa_app')
        if not ks_enable_pwa_app:
            return False
        ks_pwa_name = request.env['ir.config_parameter'].sudo().get_param('ks_curved_backend_theme.ks_pwa_name')
        ks_pwa_background_color = request.env['ir.config_parameter'].sudo().get_param(
            'ks_curved_backend_theme.ks_pwa_background_color')
        ks_pwa_theme_color = request.env['ir.config_parameter'].sudo().get_param(
            'ks_curved_backend_theme.ks_pwa_theme_color')

        ks_global_config_id = request.env.ref('ks_curved_backend_theme.ks_global_config_single_rec').sudo()

        manifest = {'name': ks_pwa_name, 'short_name': ks_pwa_name, 'description': ks_pwa_name,
                    'start_url': url_for('/web/'), 'display': 'standalone', 'background_color': ks_pwa_background_color,
                    'theme_color': ks_pwa_theme_color, 'icons': self.ks_get_image_url()}
        body = json.dumps(manifest, default=ustr)
        response = request.make_response(body, [
            ('Content-Type', 'application/manifest+json'),
        ])
        return response

    @http.route('/ks_curved_backend_theme/get/sw.js', type='http', auth='public', methods=['GET'], sitemap=False)
    def ks_get_service_worker(self):
        sw_file = get_module_resource('ks_curved_backend_theme', 'static/src/js/sw.js')
        with open(sw_file, 'r') as fp:
            body = fp.read()
        response = request.make_response(body, [
            ('Content-Type', 'text/javascript'),
            ('Service-Worker-Allowed', url_for('/web/')),
        ])
        return response

    def ks_get_image_url(self):
        ks_icons = []
        for size in [(72, 72), (96, 96), (128, 128), (144, 144), (152, 152), (192, 192), (256, 256), (384, 384),
                     (512, 512)]:
            ks_url = '/ks_curved_backend_theme/logo/icon_' + str(size[0])
            ks_pwa_icons = request.env["ir.attachment"].sudo().search(
                [('url', 'like', ks_url)], limit=1)
            if ks_pwa_icons:
                ks_icons.append({
                    "src": ks_pwa_icons.url,
                    "sizes": str(size[0]) + 'x' + str(size[1]),
                    "type": "image/png"
                })
        return ks_icons
