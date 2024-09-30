# -*- coding: utf-8 -*-
# from odoo import http


# class FleetHrEmployee(http.Controller):
#     @http.route('/fleet_hr_employee/fleet_hr_employee/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fleet_hr_employee/fleet_hr_employee/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fleet_hr_employee.listing', {
#             'root': '/fleet_hr_employee/fleet_hr_employee',
#             'objects': http.request.env['fleet_hr_employee.fleet_hr_employee'].search([]),
#         })

#     @http.route('/fleet_hr_employee/fleet_hr_employee/objects/<model("fleet_hr_employee.fleet_hr_employee"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fleet_hr_employee.object', {
#             'object': obj
#         })
