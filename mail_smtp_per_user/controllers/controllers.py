# -*- coding: utf-8 -*-
from odoo import http

# class MailSmtpPerUser(http.Controller):
#     @http.route('/mail_smtp_per_user/mail_smtp_per_user/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mail_smtp_per_user/mail_smtp_per_user/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mail_smtp_per_user.listing', {
#             'root': '/mail_smtp_per_user/mail_smtp_per_user',
#             'objects': http.request.env['mail_smtp_per_user.mail_smtp_per_user'].search([]),
#         })

#     @http.route('/mail_smtp_per_user/mail_smtp_per_user/objects/<model("mail_smtp_per_user.mail_smtp_per_user"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mail_smtp_per_user.object', {
#             'object': obj
#         })
