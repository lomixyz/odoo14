# -*- coding: utf-8 -*-
# from odoo import http


# class CustomerUniquePhone(http.Controller):
#     @http.route('/customer_unique_phone/customer_unique_phone/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customer_unique_phone/customer_unique_phone/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('customer_unique_phone.listing', {
#             'root': '/customer_unique_phone/customer_unique_phone',
#             'objects': http.request.env['customer_unique_phone.customer_unique_phone'].search([]),
#         })

#     @http.route('/customer_unique_phone/customer_unique_phone/objects/<model("customer_unique_phone.customer_unique_phone"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customer_unique_phone.object', {
#             'object': obj
#         })
