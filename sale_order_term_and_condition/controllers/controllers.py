# -*- coding: utf-8 -*-
# from odoo import http


# class SaleOrderTermAndCondition(http.Controller):
#     @http.route('/sale_order_term_and_condition/sale_order_term_and_condition/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_order_term_and_condition/sale_order_term_and_condition/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_order_term_and_condition.listing', {
#             'root': '/sale_order_term_and_condition/sale_order_term_and_condition',
#             'objects': http.request.env['sale_order_term_and_condition.sale_order_term_and_condition'].search([]),
#         })

#     @http.route('/sale_order_term_and_condition/sale_order_term_and_condition/objects/<model("sale_order_term_and_condition.sale_order_term_and_condition"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_order_term_and_condition.object', {
#             'object': obj
#         })
