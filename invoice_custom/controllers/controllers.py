# -*- coding: utf-8 -*-
# from odoo import http


# class InvoiceCustom(http.Controller):
#     @http.route('/invoice_custom/invoice_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_custom/invoice_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_custom.listing', {
#             'root': '/invoice_custom/invoice_custom',
#             'objects': http.request.env['invoice_custom.invoice_custom'].search([]),
#         })

#     @http.route('/invoice_custom/invoice_custom/objects/<model("invoice_custom.invoice_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_custom.object', {
#             'object': obj
#         })
