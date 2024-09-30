# -*- coding: utf-8 -*-
# from odoo import http


# class CustomRent(http.Controller):
#     @http.route('/custom_rent/custom_rent/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_rent/custom_rent/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_rent.listing', {
#             'root': '/custom_rent/custom_rent',
#             'objects': http.request.env['custom_rent.custom_rent'].search([]),
#         })

#     @http.route('/custom_rent/custom_rent/objects/<model("custom_rent.custom_rent"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_rent.object', {
#             'object': obj
#         })
