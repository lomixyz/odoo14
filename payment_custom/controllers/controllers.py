# -*- coding: utf-8 -*-
# from odoo import http


# class PaymentCustom(http.Controller):
#     @http.route('/payment_custom/payment_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payment_custom/payment_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('payment_custom.listing', {
#             'root': '/payment_custom/payment_custom',
#             'objects': http.request.env['payment_custom.payment_custom'].search([]),
#         })

#     @http.route('/payment_custom/payment_custom/objects/<model("payment_custom.payment_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payment_custom.object', {
#             'object': obj
#         })
