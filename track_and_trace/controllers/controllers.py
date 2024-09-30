# -*- coding: utf-8 -*-
# from odoo import http


# class TrackAndTrack(http.Controller):
#     @http.route('/track_and_trace/track_and_trace/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/track_and_trace/track_and_trace/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('track_and_trace.listing', {
#             'root': '/track_and_trace/track_and_trace',
#             'objects': http.request.env['track_and_trace.track_and_trace'].search([]),
#         })

#     @http.route('/track_and_trace/track_and_trace/objects/<model("track_and_trace.track_and_trace"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('track_and_trace.object', {
#             'object': obj
#         })
