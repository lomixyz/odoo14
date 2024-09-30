# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Home
from datetime import date


class PartnerForm(http.Controller):
    #mention class name
    @http.route(['/customer/form'], type='http', auth="public", website=True)
    #mention a url for redirection.
    #define the type of controller which in this case is ‘http’.
    #mention the authentication to be either public or user.
    def partner_form(self, **post):
    #create method
    #this will load the form webpage
        return request.render("admission_management.tmp_customer_form", {})

    @http.route(['/customer/form/submit'], type='http', auth="public", website=True)
    #next controller with url for submitting data from the form#
    def customer_form_submit(self, **post):
        partner = request.env['res.partner'].sudo().create({
            'name': post.get('name'),
            'email': post.get('email'),
            'comment': "auto comment: created from the website.",
            'is_website_customer': True ,
            'phone': post.get('phone')
        })
        vals = {
            'partner': partner,
        }
        #inherited the model to pass the values to the model from the form#
        return request.render("admission_management.tmp_customer_form_success1", vals)
        #finally send a request to render the thank you page#

   

class Sale(http.Controller):

    @http.route(['/web/post/my_workers_details'], type='http', auth="public", website=True)
    #next controller with url for submitting data from the form#
    def select_submit(self, name="", **post):
        partner = request.env['res.partner'].sudo().search([('is_website_customer', '=', True)],limit=1, order='id DESC')[0]
        rent = request.env['rent.workers.management'].sudo().create({
            'partner_id': partner.id,
            'employee_id': post.get('employee_name'),
	    'identification': "/",
            'note': "request from website",
            'is_from_website': True,
            'total_cost' : 0.00,
            'discount' : 0.00,
            'additions' : 0.00,
            'vat_id' : 1,
            'contract_date_to' : date.today()
        })
        vals = {
            'rent': rent,
        }
        #inherited the model to pass the values to the model from the form#
        return request.render("admission_management.tmp_customer_form_success", vals)
        #finally send a request to render the thank you page#

    @http.route('/web/my_workers_details', type='http', auth='public', website=True)
    def workers_details(self , **kwargs):
        workers_details = request.env['hr.employee'].sudo().search([('is_worker', '=', True),('is_available', '=', True)])
        return request.render('admission_management.workers_details_page', {'my_details': workers_details})

    
class Website(Home):

    @http.route(website=True, auth="public")
    def web_login(self, redirect=None, *args, **kw):
        response = super(Website, self).web_login(redirect=redirect, *args, **kw)
        if not redirect and request.params['login_success']:
            if request.env['res.users'].browse(request.uid).has_group('base.group_user'):
                redirect = b'/web?' + request.httprequest.query_string
            else:
                redirect = '/customer/form'
            return http.redirect_with_hash(redirect)
        return response

  
