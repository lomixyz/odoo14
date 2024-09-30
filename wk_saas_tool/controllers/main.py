# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from werkzeug.exceptions import BadRequest
from odoo.http import request
from odoo import http
from odoo.addons.web.controllers.main import Home, ensure_db
import logging
import base64

_logger = logging.getLogger(__name__)


class SaaSLogin(Home):

    # @http.route('/saas/login', type='http', auth='public', website=True, sitemap=False)
    @http.route('/saas/login', type='http', auth='none', sitemap=False)
    def autologin(self, **kw):
        """login user via Odoo Account provider
        QUERY : SELECT COALESCE(password, '') FROM res_users WHERE id=1;
        import base64
        base64.b64encode(s.encode('utf-8'))
        """
        db = request.params.get('db') and request.params.get('db').strip()
        dbname = kw.pop('db', None)
        redirect_url = kw.pop('redirect_url', '/web')
        login = kw.pop('login', 'admin')
        password = kw.pop('passwd', None)
        if not dbname:
            print("#########RRRRRRRRRRRRRR$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            return BadRequest()
        uid = request.session.authenticate(dbname, login, password)
        request.params['login_success'] = True

        return http.redirect_with_hash(redirect_url)

    @http.route('/saas/update/request', auth='public', type='http', sitemap=False)
    def update_notify(self, **kwargs):

        user_id = int(kwargs.get('uid'))
        token = kwargs.get('token')
        partner = request.env['res.users'].sudo().browse(user_id).partner_id
        partner.sudo().write({'signup_token': token})
        template = request.env.ref('wk_saas_tool.update_req_tmpl')
        template_email = template.sudo().generate_email(res_ids=partner.id, fields=['body_html'])
        partner.sudo().message_post(
            body=template_email.get('body_html'),
            message_type='comment', subtype='mail.mt_comment',
            partner_ids=[partner.id]
        )

    @http.route('/saas/image/update/request', auth='public', type='http', sitemap=False)
    def image_update_notify(self, **kwargs):
        user_id = int(kwargs.get('uid'))
        token = kwargs.get('token')
        partner = request.env['res.users'].sudo().browse(user_id).partner_id
        partner.sudo().write({'signup_token': token})
        template = request.env.ref('wk_saas_tool.image_update_req_tmpl')
        template_email = template.sudo().generate_email(res_ids=partner.id, fields=['body_html'])
        partner.sudo().message_post(
            body=template_email.get('body_html'),
            message_type='comment', subtype='mail.mt_comment',
            partner_ids=[partner.id]
        )
