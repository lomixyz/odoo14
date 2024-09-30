# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO Open Source Management Solution
#
#    ODOO Addon module by Sprintit Ltd
#    Copyright (C) 2021 Sprintit Ltd (<http://sprintit.fi>).
#
##############################################################################

from odoo import http, _
from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
        
class AuthSignupHome(AuthSignupHome):
    
    @http.route()
    def web_login(self, *args, **kw):
        """
        Method inherited to show messages if user approved or not.
        And also user may be approved once and again inactivate so,
        Message accordingly.
        """
        response = super(AuthSignupHome, self).web_login(*args, **kw)
        if response.qcontext and response.qcontext.get('login',False):
            inactive_user = request.env['res.users'].sudo().search([('login','=',response.qcontext.get('login')),('active','=',False),('approved_date','=',False)])
            if inactive_user:
                response.qcontext.update({'message':_('You can login only after your login get approved..!')})
                del response.qcontext['error']
            reinactive_user = request.env['res.users'].sudo().search([('login','=',response.qcontext.get('login')),('active','=',False),('approved_date','!=',False)])
            if reinactive_user:
                response.qcontext.update({'message':_('Your login will continue after it approved again..!')})
                del response.qcontext['error']    
        return response
    
    def get_contact_vals(self,company, kw):
        return {
            'company_type': 'person',
            'parent_id': company.id, 
            }
    
    @http.route('/web/signup', type='http', auth='public', website=True)
    def web_auth_signup(self, *args, **kw):
        """
        1) Create structure if company is there then create partner under company.
        2) Check if user need approval or not. if needed then notify users on channel.
        3) Also send emails to all users to approval team.
        """
        response = super(AuthSignupHome, self).web_auth_signup(*args, **kw)
        if 'error' not in response.qcontext and request.httprequest.method == 'POST':
            company_ids = request.env['res.partner'].sudo().search([('name', '=', kw['company_name'])])
            company = [company for company in company_ids if company.company_type == 'company']
            if company:
               company = company[0]
            if not company:
                company = request.env['res.partner'].sudo().create({
                    'name': kw['company_name'],
                    'company_type': 'company'
                    })
            request.env.user.partner_id.write(
                       self.get_contact_vals(company,kw) 
                    )
            get_param = request.env['ir.config_parameter'].sudo().get_param
            if get_param('auth_signup.signup_approval', 'False').lower() == 'true':
                request.cr.execute("""update res_users set active = 'f',for_approval_menu ='t' where id =%s"""%(request.uid))
                channel_for_approval = request.env.ref('sprintit_website_signup.channel_for_approval_users').sudo()
                if channel_for_approval:
                    partners = channel_for_approval.mapped('group_ids').mapped('users').mapped('partner_id')
                    partners_to_add = partners - channel_for_approval.channel_partner_ids
                    if partners_to_add:
                        channel_for_approval.write({'channel_last_seen_partner_ids': [(0, 0, {'partner_id': partner_id}) for partner_id in partners_to_add.ids]})
                    channel_for_approval.message_subscribe(partners.ids)
                    channel_for_approval.message_post(
                            body=_("<b>Please review signup request of user %s</b><br/>Find it under Settings -> Users -> To be Approve Users"%(kw['name'])), subject=_('User Approval'),
                            subtype_xmlid='mail.mt_comment',message_type='comment',content_subtype='html')
                    template = request.env.ref('sprintit_website_signup.mail_template_user_signup_approval', raise_if_not_found=False)
                    if template:
                        template.sudo().with_context(
                            lang=request.env.user.lang,
                            email_to=','.join(channel_for_approval.mapped('group_ids').mapped('users').mapped('email'))
                        ).send_mail(request.env.user.id, force_send=True)
                response = request.render('web.login', {'message':_("Thank you, We get your signup request, We will contact you shortly..")})
                response.headers['X-Frame-Options'] = 'DENY'
                request.session.logout(keep_db=True)
        return response
