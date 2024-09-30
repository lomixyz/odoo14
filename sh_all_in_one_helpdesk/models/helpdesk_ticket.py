# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from asyncio.log import logger
from platform import release
from odoo import models, fields, api, _, SUPERUSER_ID
import random
from datetime import datetime, timedelta
from odoo.exceptions import UserError,ValidationError
from odoo.tools import email_re,email_split
import uuid


class HelpdeskSLAStatus(models.Model):
    _inherit = 'helpdesk.sla.status'
    _description = "Helpdesk Ticket SLA Status"
    # _table = 'sh_helpdesk_sla_status'
    # _order = 'id ASC'
    # _rec_name = 'sla_id'

    # ticket_id = fields.Many2one('helpdesk.ticket',
    #                                string='Ticket',
    #                                required=True,
    #                                ondelete='cascade',
    #                                index=True)
    # sla_id = fields.Many2one('helpdesk.sla',
    #                             required=True,
    #                             ondelete='cascade')
    # sh_sla_stage_id = fields.Many2one('helpdesk.stage',
    #                                   related='sla_id.stage_id',
    #                                   store=True)
    # deadline = fields.Datetime("SLA Deadline",
    #                               compute='_compute_deadline',
    #                               compute_sudo=True,
    #                               store=True)
    # status = fields.Selection([('failed', 'Failed'),
    #                               ('reached', 'Reached'),
    #                               ('ongoing', 'Ongoing')],
    #                              string="Status")
    # color = fields.Integer("Color Index", compute='_compute_sh_color')
    sh_done_sla_date = fields.Datetime('SLA Done Date')

    # @api.depends('ticket_id.create_date', 'sla_id',
    #              'ticket_id.stage_id')
    # def _compute_deadline(self):
    #     for rec in self:

    #         if rec.sla_id.target_type == 'assigning' and rec.sh_sla_stage_id == rec.ticket_id.stage_id:
    #             deadline = fields.Datetime.now()
    #         elif rec.sla_id.target_type == 'assigning' and rec.sh_sla_stage_id:
    #             rec.deadline = False
    #             continue
    #         else:
    #             deadline = rec.ticket_id.create_date
    #         working_calendar = rec.ticket_id.team_id.sh_resource_calendar_id
    #         if not working_calendar:
    #             # Normally, having a working_calendar is mandatory
    #             rec.deadline = deadline
    #             continue

    #         time_days = rec.sla_id.sh_days
    #         if time_days and (
    #                 rec.sla_id.target_type == 'stage'
    #                 or rec.sla_id.target_type == 'assigning'
    #                 and not rec.sla_id.stage_id):
    #             deadline = working_calendar.plan_days(time_days + 1,
    #                                                   deadline,
    #                                                   compute_leaves=True)

    #             # We should also depend on ticket creation time, otherwise for 1 day SLA, all tickets
    #             # created on monday will have their deadline filled with tuesday 8:00
    #             create_dt = rec.ticket_id.create_date
    #             deadline = deadline.replace(hour=create_dt.hour,
    #                                         minute=create_dt.minute,
    #                                         second=create_dt.second,
    #                                         microsecond=create_dt.microsecond)

    #         elif time_days and rec.sla_id.target_type == 'assigning' and rec.sh_sla_stage_id == rec.ticket_id.stage_id:
    #             deadline = working_calendar.plan_days(time_days + 1,
    #                                                   deadline,
    #                                                   compute_leaves=True)

    #             reached_stage_dt = fields.Datetime.now()
    #             deadline = deadline.replace(
    #                 hour=reached_stage_dt.hour,
    #                 minute=reached_stage_dt.minute,
    #                 second=reached_stage_dt.second,
    #                 microsecond=reached_stage_dt.microsecond)

    #         sla_hours = rec.sla_id.sh_hours + (rec.sla_id.sh_minutes /
    #                                               60)

    #         if rec.sla_id.target_type == 'stage':

    #             # Except if ticket creation time is later than the end time of the working day
    #             deadline_for_working_cal = working_calendar.plan_hours(
    #                 0, deadline)
    #             if deadline_for_working_cal and deadline.day < deadline_for_working_cal.day:
    #                 deadline = deadline.replace(hour=0,
    #                                             minute=0,
    #                                             second=0,
    #                                             microsecond=0)

    #         # We should execute the function plan_hours in any case because, in a 1 day SLA environment,
    #         # if I create a ticket knowing that I'm not working the day after at the same time, ticket
    #         # deadline will be set at time I don't work (ticket creation time might not be in working calendar).
    #         rec.deadline = working_calendar.plan_hours(sla_hours,
    #                                                       deadline,
    #                                                       compute_leaves=True)

    @api.depends('status')
    def _compute_sh_color(self):
        for rec in self:
            rec._compute_deadline()
            if rec.status == 'failed':
                rec.color = 1
            elif rec.status == 'reached':
                rec.color = 10
            elif rec.status == 'ongoing':
                rec.color = 4
            else:
                rec.color = 0


class HelpdeskTicket(models.Model):
    # _inherit = 'helpdesk.ticket'
    _inherit = ['helpdesk.ticket']#,'portal.mixin', 'mail.thread', 'mail.activity.mixin']
    # _description = "Helpdesk Ticket"
    # _order = 'id DESC'
    # _rec_name = 'name'
    # _primary_email = ['email']

    def action_helpdesk_ticket_merge(self):
        
        get_tickets = self.env['helpdesk.ticket'].browse(self.env.context.get('active_ids'))
        if len(get_tickets.ids) < 2:
            raise ValidationError(_('You should select minium two ticket for merge !!'))
        result = all(rec == get_tickets.mapped('partner_id').ids[0] for rec in get_tickets.mapped('partner_id').ids)
        if not result:
            raise ValidationError(_('Partner Must be same !!'))

        return {
            'name':'Merge Ticket',
            'res_model':'helpdesk.ticket.merge.ticket.wizard',
            'view_mode':'form',
            'context': {
              'default_sh_helpdesk_ticket_ids' : [(6, 0, self.env.context.get('active_ids'))],
              'default_sh_partner_id' : get_tickets.mapped('partner_id').ids[0],
            },
            'view_id':self.env.ref('sh_all_in_one_helpdesk.sh_helpdesk_ticket_merge_ticket_wizard_form_view').id,
            'target':'new',
            'type':'ir.actions.act_window'
        }

    def get_deafult_company(self):
        company_id = self.env.company
        return company_id

    @api.model
    def get_default_stage(self):
        company_id = self.env.company
        stage_id = self.env['helpdesk.stage'].sudo().search(
            [('id', '=', company_id.new_stage_id.id)], limit=1)
        return stage_id.id

    @api.model
    def default_due_date(self):
        return fields.Datetime.now()

    company_id = fields.Many2one('res.company',
                                 string="Company",
                                 default=get_deafult_company)
    done_stage_boolean = fields.Boolean('Done Stage',
                                        compute='_compute_stage_booleans',
                                        store=True)
    cancel_stage_boolean = fields.Boolean('Cancel Stage',
                                          compute='_compute_stage_booleans',
                                          store=True)
    reopen_stage_boolean = fields.Boolean('Reopened Stage',
                                          compute='_compute_stage_booleans',
                                          store=True)
    closed_stage_boolean = fields.Boolean('Closed Stage',
                                          compute='_compute_stage_booleans',
                                          store=True)
    open_boolean = fields.Boolean('Open Ticket',
                                  compute='_compute_stage_booleans',
                                  store=True)
    cancel_button_boolean = fields.Boolean(
        "Cancel Button",
        compute='_compute_cancel_button_boolean',
        search='_search_cancel_button_boolean')
    done_button_boolean = fields.Boolean(
        "Done Button",
        compute='_compute_done_button_boolean',
        search='_search_done_button_boolean')
    state = fields.Selection([('customer_replied', 'Customer Replied'),
                              ('staff_replied', 'Staff Replied')],
                             string="Replied Status",
                             default='customer_replied',
                             required=True,
                             tracking=True)
    
    ticket_from_website = fields.Boolean('Ticket From Website')
    ticket_from_portal = fields.Boolean('Ticket From Portal')
    cancel_reason = fields.Char("Cancel Reason", tracking=True, translate=True)
    priority_id = fields.Many2one('helpdesk.priority',
                               string='Priority',
                               tracking=True)
    stage_id = fields.Many2one(
        'helpdesk.stage', string='Stage', compute='_compute_user_and_stage_ids', store=True,
        readonly=False, ondelete='restrict', tracking=True, group_expand='_read_group_stage_ids',
        copy=False, index=True, domain="[('team_ids', '=', team_id)]")
    # stage_id = fields.Many2one('helpdesk.stage',
    #                            string="Stage",
    #                            default=get_default_stage,
    #                            tracking=True,
    #                            index=True,
    #                            group_expand='_read_group_stage_ids')
    ticket_type_id = fields.Many2one('helpdesk.ticket.type',
                                  string='Ticket Type',
                                    domain="[('category_id', '=', category_id)]",)
    # team_id = fields.Many2one('helpdesk.team', string='Team', tracking=True)
    team_head = fields.Many2one('res.users', "Team Head", tracking=True ,default=lambda self: self.team_id.team_head,related='team_id.team_head',store=True)
    # user_id = fields.Many2one('res.users',
    #                           string="Assigned User",
    #                           tracking=True)
    subject_id = fields.Many2one('helpdesk.sub.type',
                                 string='Ticket Subject Type',
                                 tracking=True)
    category_id = fields.Many2one('helpdesk.category',
                                  string="Category",
                                #   related='ticket_type_id.category_id',
                                  default=lambda self: self.ticket_type_id.category_id,
                                  store=True,
                                  tracking=True)
    sub_category_id = fields.Many2one('helpdesk.subcategory',
                                      string="Sub Category")
    # partner_id = fields.Many2one('res.partner',
    #                              string='Partner',
    #                              tracking=True,
    #                              required=True)
    person_name = fields.Char(string='Person Name', tracking=True)
    # email = fields.Char(string='Email', tracking=True)
    # close_date = fields.Datetime(string='Close Date', tracking=True)
    close_by = fields.Many2one('res.users', string='Closed By', tracking=True)
    cancel_date = fields.Datetime(string='Cancelled Date', tracking=True)
    cancel_by = fields.Many2one('res.users',
                                string='Cancelled By',
                                tracking=True)
    replied_date = fields.Datetime('Replied Date', tracking=True)
    product_ids = fields.Many2many('product.product', string='Products')

    comment = fields.Text(string="Comment", tracking=True, translate=True)
    # description = fields.Html('Description', tracking=True)
    # color = fields.Integer(string='Color Index')
    priority_new = fields.Selection([('1', 'Very Low'), ('2', 'Low'),
                                     ('3', 'Normal'), ('4', 'High'),
                                     ('5', 'Very High'), ('6', 'Excellent')],
                                    string="Customer Rating",
                                    tracking=True)
    customer_comment = fields.Text("Customer Comment", tracking=True)

    attachment_ids = fields.Many2many('ir.attachment', string="Attachments")
    form_url = fields.Char('Form Url', compute='_compute_form_url')
    category_bool = fields.Boolean(string='Category Setting',
                                   related='company_id.category',
                                   store=True)
    sub_category_bool = fields.Boolean(string='Sub Category Setting',
                                       related='company_id.sub_category',
                                       store=True)
    rating_bool = fields.Boolean(string='Rating Setting',
                                 related='company_id.customer_rating',
                                 store=True)
    ticket_allocated = fields.Boolean("Allocated")
    # domain_user_ids = fields.Many2many('res.users', string="Assign Multi Users")
    sh_display_multi_user = fields.Boolean(
        compute="_compute_sh_display_multi_user")
    sh_display_product = fields.Boolean(compute='_compute_sh_display_product')
    status = fields.Selection([('failed', 'Failed'),
                                  ('reached', 'Reached'),
                                  ('ongoing', 'Ongoing')],
                                 string="Status")
    # sla_ids = fields.Many2many('helpdesk.sla',
    #                                      'sh_helpdesk_sla_status',
    #                                      'ticket_id',
    #                                      'sla_id',
    #                                      string="Helpdesk SLA Policies",
    #                                      copy=False)
    # sla_status_ids = fields.One2many('helpdesk.sla.status',
    #                                     'ticket_id',
    #                                     string="Helpdesk SLA Status")
    # sla_deadline = fields.Datetime('SLA Deadline',
    #                                   compute='_compute_sla_deadline',
    #                                   store=True)
    sh_status_boolean = fields.Boolean(compute='_compute_state_boolean')
    sh_days_to_reach = fields.Float(string='SLA reached duration',
                                    compute='_compute_days_to_reach',
                                    store=True)
    sh_days_to_late = fields.Float(string='SLA late duration',
                                   compute='_compute_days_to_late',
                                   store=True)
    sh_due_date = fields.Datetime('Reminder Due Date',
                                  default=default_due_date)
    sh_ticket_alarm_ids = fields.Many2many('sh.ticket.alarm',
                                           string='Ticket Reminders')
    sh_ticket_report_url = fields.Char(compute='_compute_report_url')
    report_token = fields.Char("Access Token")
    portal_ticket_url_wp = fields.Char(compute='_compute_ticket_portal_url_wp')
    mobile_no = fields.Char('Mobile')
    name = fields.Char('Email Subject')

    sh_merge_ticket_ids = fields.Many2many('helpdesk.ticket',relation='model_merge_helpdesk_ticket',column1="helpdesk", column2="ticket", string='Merge Tickets')

    sh_merge_ticket_count = fields.Integer(compute="_compute_count_merge_ticket")

    
    def _compute_count_merge_ticket(self):
        for record in self:
            record.sh_merge_ticket_count = len(record.sh_merge_ticket_ids) if record.sh_merge_ticket_ids else 0
    
    def get_merge_tickets(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Merged Tickets",
            "view_mode": "tree,form",
            "res_model": "helpdesk.ticket",
            "domain": [("id", "in", self.sh_merge_ticket_ids.ids)],
        }

    # <-- MULTI ACTION FOR MASS UPDATE ASSIGN-TO,MULTI-USER & STATE -->

    def action_mass_update_wizard(self):
        return {
            'name':
            'Mass Update Ticket',
            'res_model':
            'helpdesk.ticket.mass.update.wizard',
            'view_mode':
            'form',
            'context': {
                'default_helpdesks_ticket_ids':
                [(6, 0, self.env.context.get('active_ids'))],
                'default_check_sh_display_multi_user':
                self.env.user.company_id.sh_display_multi_user
            },
            'view_id':
            self.env.ref(
                'sh_all_in_one_helpdesk.sh_helpdesk_ticket_mass_update_wizard_form_view'
            ).id,
            'target':
            'new',
            'type':
            'ir.actions.act_window'
        }

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        all_stages = self.env['helpdesk.stage'].sudo().search([])
        search_domain = [('id', 'in', all_stages.ids)]

        # perform search
        stage_ids = stages._search(search_domain,
                                   order=order,
                                   access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    def _search_done_button_boolean(self, operator, value):
        not_done_ids = []
        done_ids = []
        for record in self.search([]):
            if record.stage_id.is_done_button_visible:
                done_ids.append(record.id)
            else:
                not_done_ids.append(record.id)
        if operator == '=':
            return [('id', 'in', done_ids)]
        elif operator == '!=':
            return [('id', 'in', not_done_ids)]
        else:
            return []

    def _search_cancel_button_boolean(self, operator, value):
        not_cancel_ids = []
        cancel_ids = []
        for record in self.search([]):
            if record.stage_id.is_cancel_button_visible:
                cancel_ids.append(record.id)
            else:
                not_cancel_ids.append(record.id)
        if operator == '=':
            return [('id', 'in', cancel_ids)]
        elif operator == '!=':
            return [('id', 'in', not_cancel_ids)]
        else:
            return []

    def _compute_ticket_portal_url_wp(self):
        for rec in self:
            rec.portal_ticket_url_wp = False
            if rec.company_id.sh_pdf_in_message:
                base_url = self.env['ir.config_parameter'].sudo().get_param(
                    'web.base.url')
                ticket_url = base_url + rec.get_portal_url()
                self.sudo().write({'portal_ticket_url_wp': ticket_url})

    def _get_token(self):
        """ Get the current record access token """
        if self.report_token:
            return self.report_token
        else:
            report_token = str(uuid.uuid4())
            self.write({'report_token': report_token})
            return report_token

    def get_download_report_url(self):
        url = ''
        if self.id:
            self.ensure_one()
            url = '/download/ht/' + '%s?access_token=%s' % (self.id,
                                                            self._get_token())
        return url

    def _compute_report_url(self):
        for rec in self:
            rec.sh_ticket_report_url = False
            if rec.company_id.sh_pdf_in_message:
                base_url = self.env['ir.config_parameter'].sudo().get_param(
                    'web.base.url')
                ticket_url = "%0A%0A Click here to download Ticket Document : %0A" + \
                    base_url+rec.get_download_report_url()
                self.sudo().write({
                    'sh_ticket_report_url':
                    base_url + rec.get_download_report_url()
                })

    def action_send_whatsapp(self):
        self.ensure_one()
        if not self.partner_id.mobile:
            raise UserError(_("Partner Mobile Number Not Exist !"))
        template = self.env.ref(
            'sh_all_in_one_helpdesk.sh_send_whatsapp_email_template')

        ctx = {
            'default_model': 'helpdesk.ticket',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template.id),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'default_is_wp': True,
        }
        attachment_ids = self.env['ir.attachment'].sudo().search([
            ('res_model', '=', 'helpdesk.ticket'),
            ('res_id', '=', str(self.id))
        ])
        if attachment_ids:
            ctx.update({'attachment_ids': [(6, 0, attachment_ids.ids)]})
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def _compute_days_to_reach(self):
        if self:
            for rec in self:
                sh_days_to_reach = 0.0
                if rec.sla_status_ids:
                    for line in rec.sla_status_ids:
                        if line.deadline and line.sh_done_sla_date:
                            delta = line.sh_done_sla_date - line.deadline
                            sh_days_to_reach += delta.days
                rec.sh_days_to_reach = sh_days_to_reach

    def _compute_days_to_late(self):
        if self:
            for rec in self:
                sh_days_to_late = 0.0
                if rec.sla_status_ids:
                    for line in rec.sla_status_ids:
                        if line.deadline and line.sh_done_sla_date:
                            delta = line.sh_done_sla_date - line.deadline
                            sh_days_to_late += delta.days
                rec.sh_days_to_late = sh_days_to_late

    def _compute_state_boolean(self):
        if self:
            for rec in self:
                rec.sh_status_boolean = False
                reached = rec.sla_status_ids.filtered(
                    lambda x: x.status == 'reached')
                failed = rec.sla_status_ids.filtered(
                    lambda x: x.status == 'failed')
                if reached and failed:
                    rec.status = 'ongoing'

    # @api.depends('sla_status_ids.deadline')
    # def _compute_sla_deadline(self):
    #     for rec in self:
    #         deadline = False
    #         status_ids = rec.sla_status_ids.filtered(
    #             lambda x: x.status == False)
    #         rec.sla_deadline = min(status_ids.mapped(
    #             'deadline')) if status_ids else deadline

    @api.model
    def change_sh_status(self):
        self.ensure_one()
        if self.sla_status_ids:
            for line in self.sla_status_ids:
                if line.sla_id and line.sla_id.target_type == 'stage': #stage
                    if line.sla_id.stage_id.id == self.stage_id.id:
                        line.sh_done_sla_date = fields.Datetime.now()
                        line.status = False
                        self.status = False
                        if line.sh_done_sla_date and line.deadline:
                            line.status = 'reached' if line.sh_done_sla_date < line.deadline else 'failed'
                            self.status = 'reached' if line.sh_done_sla_date < line.deadline else 'failed'
                        else:
                            line.status = False if (
                                not line.deadline or line.deadline >
                                fields.Datetime.now()) else 'failed'
                            self.status = False if (
                                not line.deadline or line.deadline >
                                fields.Datetime.now()) else 'failed'
                elif line.sla_id and line.sla_id.target_type == 'assigning': # assigning
                    if self.user_id or self.domain_user_ids:
                        line.sh_done_sla_date = fields.Datetime.now()
                        line.status = False
                        self.status = False
                        if line.sh_done_sla_date and line.deadline:
                            line.status = 'reached' if line.sh_done_sla_date < line.deadline else 'failed'
                            self.status = 'reached' if line.sh_done_sla_date < line.deadline else 'failed'
                        else:
                            line.status = False if (
                                not line.deadline or line.deadline >
                                fields.Datetime.now()) else 'failed'
                            self.status = False if (
                                not line.deadline or line.deadline >
                                fields.Datetime.now()) else 'failed'

    @api.onchange('team_id', 'ticket_type_id')
    def _onchange_sh_helpdesk_policy_ids(self):
        if self:
            for rec in self:
                rec.sla_ids = [
                    (6, 0,
                     rec.helpdesk_sla_create(rec.team_id.id,
                                             rec.ticket_type_id.id))
                ]

    @api.depends('company_id')
    def _compute_sh_display_multi_user(self):
        if self:
            for rec in self:
                rec.sh_display_multi_user = False
                if rec.company_id and rec.company_id.sh_display_multi_user:
                    rec.sh_display_multi_user = True

    @api.depends('company_id')
    def _compute_sh_display_product(self):
        if self:
            for rec in self:
                rec.sh_display_product = False
                if rec.company_id and rec.company_id.sh_configure_activate:
                    rec.sh_display_product = True

    @api.model
    # def message_new(self, msg_dict, custom_values=None):
    #     """ Overrides mail_thread message_new that is called by the mailgateway
    #         through message_process.
    #         This override updates the document according to the email.
    #     """
    #     partner_ids = []

    #     get_ourgoing_server_all = self.env['ir.mail_server'].search([('active','=',True)])

    #     if 'to' in msg_dict:
    #             if ',' in msg_dict.get('to'):
    #                 email_to = msg_dict.get('to').split(",")
    #                 if email_to:
    #                     for to_email in email_to:
    #                         email_address = to_email.strip()
    #                         email_address = email_split(email_address)[0]
    #                         # if get_ourgoing_server_all and email_address.lower() not in get_ourgoing_server_all.mapped('smtp_user'):
    #                         if email_address:
    #                             partner_id = self.env['res.partner'].search([
    #                                 ('email', '=', email_address)
    #                             ], limit=1)
    #                             if partner_id:
    #                                 partner_ids.append(partner_id.id)
    #                             else:
    #                                 p_name = self.env['res.partner']._parse_partner_name(to_email)[0] if to_email else email_address
    #                                 partner_id = self.env['res.partner'].sudo().create({
    #                                     'name': p_name or email_address,
    #                                     'email': email_address,
    #                                 })
    #                                 partner_ids.append(partner_id.id)
    #             else:
    #                 email_address = email_split(msg_dict.get('to'))[0]
    #                 # if get_ourgoing_server_all and email_address.lower() not in get_ourgoing_server_all.mapped('smtp_user'):
    #                 if email_address:
    #                     partner_id = self.env['res.partner'].search([
    #                             ('email', '=', email_address)
    #                         ], limit=1)
    #                     if partner_id:
    #                         partner_ids.append(partner_id.id)
    #                     else:
    #                         p_name = self.env['res.partner']._parse_partner_name(msg_dict.get('to'))[0] if msg_dict.get('to') else email_address
    #                         partner_id = self.env['res.partner'].sudo().create({
    #                             'name': p_name or email_address,
    #                             'email': email_address,
    #                         })
    #                         partner_ids.append(partner_id.id)


    #     if 'cc' in msg_dict and msg_dict.get('cc') != '':
    #             if ',' in msg_dict.get('cc'):
    #                 email_cc = msg_dict.get('cc').split(",")
                    
    #                 if email_cc:
    #                     for cc_email in email_cc:
    #                         email_address = cc_email.strip()
    #                         email_address = email_split(email_address)[0]
    #                         p_name = self.env['res.partner']._parse_partner_name(cc_email)[0] if cc_email else email_address
    #                         # if get_ourgoing_server_all and email_address.lower() not in get_ourgoing_server_all.mapped('smtp_user'):
    #                         if email_address:
    #                             partner_id = self.env['res.partner'].search([
    #                                 ('email', '=', email_address)
    #                             ], limit=1)
    #                             if partner_id:
    #                                 partner_ids.append(partner_id.id)
    #                             else:
    #                                 partner_id = self.env['res.partner'].sudo().create({
    #                                     'name': p_name or email_address,
    #                                     'email': email_address,
    #                                 })
    #                                 partner_ids.append(partner_id.id)
    #             else:
    #                 email_address = email_split(msg_dict.get('cc'))[0]
    #                 # if get_ourgoing_server_all and email_address.lower() not in get_ourgoing_server_all.mapped('smtp_user'):
    #                 if email_address:
    #                     partner_id = self.env['res.partner'].search([
    #                             ('email', '=', email_address)
    #                         ], limit=1)
                    
    #                     if partner_id:
    #                         partner_ids.append(partner_id.id)
    #                     else:
    #                         p_name = self.env['res.partner']._parse_partner_name(msg_dict.get('cc'))[0] if msg_dict.get('cc') else email_address
    #                         partner_id = self.env['res.partner'].sudo().create({
    #                             'name': p_name or email_address,
    #                             'email': email_address,
    #                         })
    #                         partner_ids.append(partner_id.id)
        
            
    #     defaults = {
    #         'name': msg_dict.get('subject') or _("No Subject"),
    #         'email': msg_dict.get('from'),
    #         'partner_id': msg_dict.get('author_id', False),
    #         'description': msg_dict.get('body'),
    #         'name': msg_dict.get('subject') or _("No Subject"),
    #         'state': 'customer_replied',
    #         'replied_date': msg_dict.get('date')
    #     }

    #     res = super(HelpdeskTicket, self).message_new(msg_dict,
    #                                                    custom_values=defaults)

    #     if partner_ids:
    #         res.message_subscribe(partner_ids=partner_ids)        
        
    #     return res

    def _message_post_after_hook(self, message, msg_vals):
        if self.email and not self.partner_id:
            # we consider that posting a message with a specified recipient (not a follower, a specific one)
            # on a document without customer means that it was created through the chatter using
            # suggested recipients. This heuristic allows to avoid ugly hacks in JS.
            new_partner = message.partner_ids.filtered(
                lambda partner: partner.email == self.email)
            if new_partner:
                self.search([
                    ('partner_id', '=', False),
                    ('email', '=', new_partner.email),
                ]).write({'partner_id': new_partner.id})

        return super(HelpdeskTicket,
                     self)._message_post_after_hook(message, msg_vals)

    def _compute_form_url(self):
        if self:
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            url_str = ''
            action = self.env.ref(
                'sh_all_in_one_helpdesk.helpdesk_ticket_action').id
            if base_url:
                url_str += str(base_url) + '/web#'
            for rec in self:
                url_str += 'id='+str(rec.id)+'&action='+str(action) + \
                    '&model=helpdesk.ticket&view_type=form'
                rec.form_url = url_str

    def _compute_access_url(self):
        super(HelpdeskTicket, self)._compute_access_url()
        for ticket in self:
            ticket.access_url = '/my/tickets/%s' % (ticket.id)

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % ('Ticket', self.name)

    @api.model
    def helpdesk_sla_create(self, team_id, ticket_type_id):
        self.ensure_one()
        sla_policy_ids_list = []
        if self.sla_status_ids:
            self.sla_status_ids.unlink()
        if team_id:
            sla_policy_ids = self.env['helpdesk.sla'].sudo().search([
                ('team_id', '=', team_id)
            ])
            if sla_policy_ids:
                for policy_id in sla_policy_ids:
                    if policy_id.id not in sla_policy_ids_list:
                        sla_policy_ids_list.append(policy_id.id)
        if ticket_type_id:
            if team_id:
                sla_policy_ids = self.env['helpdesk.sla'].sudo().search([
                    ('ticket_type_id', '=', ticket_type_id),
                    ('team_id', '=', team_id)
                ])
                if sla_policy_ids:
                    for policy_id in sla_policy_ids:
                        if policy_id.id not in sla_policy_ids_list:
                            sla_policy_ids_list.append(policy_id.id)
            elif not team_id:
                sla_policy_ids = self.env['helpdesk.sla'].sudo().search([
                    ('ticket_type_id', '=', ticket_type_id)
                ])
                if sla_policy_ids:
                    for policy_id in sla_policy_ids:
                        if policy_id.id not in sla_policy_ids_list:
                            sla_policy_ids_list.append(policy_id.id)
        return sla_policy_ids_list

    # @api.model
    # def create(self, vals):
    #     if vals.get('partner_id') == False and vals.get('email', False):
    #         emails = email_re.findall(vals.get('email') or '')
    #         email = emails and emails[0] or ''
    #         name = str(vals.get('email')).split('"')
    #         partner_id = self.env['res.partner'].create({
    #             'name':
    #             name[1],
    #             'email':
    #             email,
    #             'company_type':
    #             'person',
    #         })
    #         vals.update({
    #             'partner_id': partner_id.id,
    #             'email': email,
    #             'person_name': partner_id.name,
    #         })
    #     if self.env.company.sh_default_team_id and not vals.get(
    #             'team_id') and not vals.get('user_id'):
    #         vals.update({
    #             'team_id':
    #             self.env.company.sh_default_team_id.id,
    #             'team_head':
    #             self.env.company.sh_default_team_id.team_head.id,
    #             'user_id':
    #             self.env.company.sh_default_user_id.id,
    #         })
    #     number = random.randrange(1, 10)
    #     company_id = self.env.company
    #     if 'company_id' in vals:
    #         self = self.with_company(vals['company_id'])
    #     vals['name'] = self.env['ir.sequence'].next_by_code(
    #         'helpdesk.ticket') or _('New')
    #     if company_id.new_stage_id:
    #         vals['stage_id'] = company_id.new_stage_id.id

    #     vals['color'] = number
    #     res = super(HelpdeskTicket, self).create(vals)
    #     if res.sla_status_ids:
    #         for line in res.sla_status_ids:
    #             line.status = res.status
    #     if res.ticket_from_website and res.company_id.new_stage_id.mail_template_ids and res.partner_id:
    #         for template in res.company_id.new_stage_id.mail_template_ids:
    #             template.sudo().send_mail(res.id, force_send=True)
    #     else:
    #         if not res.ticket_from_website and res.company_id.new_stage_id.mail_template_ids and res.partner_id:
    #             for template in res.company_id.new_stage_id.mail_template_ids:
    #                 template.sudo().send_mail(res.id, force_send=True)
    #     if res.team_id and res.team_head and res.user_id and res.domain_user_ids:
    #         allocation_template = res.company_id.allocation_mail_template_id
    #         email_formatted = []
    #         if res.team_head.partner_id.email_formatted not in email_formatted:
    #             email_formatted.append(
    #                 res.team_head.partner_id.email_formatted)
    #         if res.user_id.partner_id.email_formatted not in email_formatted:
    #             email_formatted.append(res.user_id.partner_id.email_formatted)
    #         for user in res.domain_user_ids:
    #             if user.id != res.user_id.id:
    #                 if user.partner_id.email_formatted not in email_formatted:
    #                     email_formatted.append(user.partner_id.email_formatted)
    #         email_formatted_str = ','.join(email_formatted)
    #         email_values = {
    #             'email_from': str(res.team_head.partner_id.email_formatted),
    #             'email_to': email_formatted_str
    #         }
    #         if allocation_template:
    #             allocation_template.sudo().send_mail(res.id,
    #                                                  force_send=True,
    #                                                  email_values=email_values)
    #             res.ticket_allocated = True
    #     elif res.team_id and res.team_head and res.user_id and not res.domain_user_ids:
    #         allocation_template = res.company_id.allocation_mail_template_id
    #         email_formatted = []
    #         if res.team_head.partner_id.email_formatted not in email_formatted:
    #             email_formatted.append(
    #                 res.team_head.partner_id.email_formatted)
    #         if res.user_id.partner_id.email_formatted not in email_formatted:
    #             email_formatted.append(res.user_id.partner_id.email_formatted)
    #         email_formatted_str = ','.join(email_formatted)
    #         email_values = {
    #             'email_from': str(res.team_head.partner_id.email_formatted),
    #             'email_to': email_formatted_str
    #         }
    #         if allocation_template:
    #             allocation_template.sudo().send_mail(res.id,
    #                                                  force_send=True,
    #                                                  email_values=email_values)
    #             res.ticket_allocated = True
    #     elif res.team_id and res.team_head and not res.user_id and res.domain_user_ids:
    #         allocation_template = res.company_id.allocation_mail_template_id
    #         email_formatted = []
    #         for user in res.domain_user_ids:
    #             if user.partner_id.email_formatted not in email_formatted:
    #                 email_formatted.append(user.partner_id.email_formatted)
    #         email_formatted_str = ','.join(email_formatted)
    #         email_values = {
    #             'email_from': str(res.team_head.partner_id.email_formatted),
    #             'email_to': email_formatted_str
    #         }
    #         if allocation_template:
    #             allocation_template.sudo().send_mail(res.id,
    #                                                  force_send=True,
    #                                                  email_values=email_values)
    #             res.ticket_allocated = True
    #     elif not res.team_id and not res.team_head and res.user_id and res.domain_user_ids:
    #         allocation_template = res.company_id.allocation_mail_template_id
    #         email_formatted = []
    #         if res.user_id.partner_id.email_formatted not in email_formatted:
    #             email_formatted.append(res.user_id.partner_id.email_formatted)
    #         for user in res.domain_user_ids:
    #             if user.id != res.user_id.id:
    #                 if user.partner_id.email_formatted not in email_formatted:
    #                     email_formatted.append(user.partner_id.email_formatted)
    #         email_formatted_str = ','.join(email_formatted)
    #         email_values = {
    #             'email_from': str(res.company_id.partner_id.email_formatted),
    #             'email_to': email_formatted_str
    #         }
    #         if allocation_template:
    #             allocation_template.sudo().send_mail(res.id,
    #                                                  force_send=True,
    #                                                  email_values=email_values)
    #             res.ticket_allocated = True
    #     elif not res.team_id and not res.team_head and res.user_id and not res.domain_user_ids:
    #         allocation_template = res.company_id.allocation_mail_template_id
    #         allocation_template.sudo().write({
    #             'email_from':
    #             str(res.company_id.partner_id.email_formatted),
    #             'email_to':
    #             str(res.user_id.partner_id.email_formatted),
    #             'partner_to':
    #             str(res.user_id.partner_id.id)
    #         })
    #         email_values = {
    #             'email_from': str(res.company_id.partner_id.email_formatted),
    #             'email_to': str(res.user_id.partner_id.email_formatted)
    #         }
    #         if allocation_template:
    #             allocation_template.sudo().send_mail(res.id,
    #                                                  force_send=True,
    #                                                  email_values=email_values)
    #             res.ticket_allocated = True
    #     elif not res.team_id and not res.team_head and not res.user_id and res.domain_user_ids:
    #         allocation_template = res.company_id.allocation_mail_template_id
    #         email_formatted = []
    #         for user in res.domain_user_ids:
    #             if user.partner_id.email_formatted not in email_formatted:
    #                 email_formatted.append(user.partner_id.email_formatted)
    #         email_formatted_str = ','.join(email_formatted)
    #         email_values = {
    #             'email_from': str(res.company_id.partner_id.email_formatted),
    #             'email_to': email_formatted_str
    #         }
    #         if allocation_template:
    #             allocation_template.sudo().send_mail(res.id,
    #                                                  force_send=True,
    #                                                  email_values=email_values)
    #             res.ticket_allocated = True
    #     if self.env.company.sh_auto_add_customer_as_follower:
    #         res.message_subscribe(partner_ids=res.partner_id.ids)
    #     return res

    # def write(self, vals):

    #     if vals.get('state'):
    #         if vals.get('state') == 'customer_replied':
    #             if self.env.user.company_id.sh_customer_replied:
    #                 for rec in self:
    #                     if rec.stage_id.id != self.env.user.company_id.new_stage_id.id:
    #                         vals.update({
    #                             'stage_id':
    #                             self.env.user.company_id.
    #                             sh_customer_replied_stage_id.id
    #                         })
    #         elif vals.get('state') == 'staff_replied':
    #             if self.env.user.company_id.sh_staff_replied:
    #                 for rec in self:
    #                     if rec.stage_id.id != self.env.user.company_id.new_stage_id.id:
    #                         vals.update({
    #                             'stage_id':
    #                             self.env.user.company_id.
    #                             sh_staff_replied_stage_id.id
    #                         })

    #     user_groups = self.env.user.groups_id.ids
    #     if vals.get('stage_id'):
    #         stage_id = self.env['helpdesk.stage'].sudo().search(
    #             [('id', '=', vals.get('stage_id'))], limit=1)
    #         if stage_id and stage_id.sh_group_ids:
    #             is_group_exist = False
    #             list_user_groups = user_groups
    #             list_stage_groups = stage_id.sh_group_ids.ids
    #             for item in list_stage_groups:
    #                 if item in list_user_groups:
    #                     is_group_exist = True
    #                     break
    #             if not is_group_exist:
    #                 raise UserError(
    #                     _('You have not access to edit this support request.'))

    #     if vals.get('partner_id'
    #                 ) and self.env.company.new_stage_id.mail_template_ids:
    #         for rec in self:
    #             for template in rec.company_id.new_stage_id.mail_template_ids:
    #                 template.sudo().send_mail(rec.id, force_send=True)
    #     res = super(HelpdeskTicket, self).write(vals)
    #     if vals.get('team_id') and vals.get('team_head') and vals.get(
    #             'user_id') and vals.get(
    #                 'domain_user_ids') and not vals.get('ticket_allocated'):
    #         allocation_template = self.env.company.allocation_mail_template_id
    #         team_head = self.env['res.users'].sudo().browse(
    #             vals.get('team_head'))
    #         user_id = self.env['res.users'].sudo().browse(vals.get('user_id'))
    #         email_formatted = []
    #         if team_head.partner_id.email_formatted not in email_formatted:
    #             email_formatted.append(team_head.partner_id.email_formatted)
    #         if user_id.partner_id.email_formatted not in email_formatted:
    #             email_formatted.append(user_id.partner_id.email_formatted)
    #         users = vals.get('domain_user_ids')[0][2]
    #         user_ids = self.env['res.users'].sudo().browse(users)
    #         for user in user_ids:
    #             if user.id != user_id.id:
    #                 if user.partner_id.email_formatted not in email_formatted:
    #                     email_formatted.append(user.partner_id.email_formatted)
    #         email_formatted_str = ','.join(email_formatted)
    #         email_values = {
    #             'email_from': str(team_head.partner_id.email_formatted),
    #             'email_to': email_formatted_str
    #         }
    #         if allocation_template:
    #             for rec in self:
    #                 allocation_template.sudo().send_mail(
    #                     rec.id, force_send=True, email_values=email_values)
    #                 rec.ticket_allocated = True
    #     elif vals.get('team_id') and vals.get('team_head') and vals.get(
    #             'user_id'
    #     ) and not vals.get('domain_user_ids') and not vals.get('ticket_allocated'):
    #         allocation_template = self.env.company.allocation_mail_template_id
    #         team_head = self.env['res.users'].sudo().browse(
    #             vals.get('team_head'))
    #         user_id = self.env['res.users'].sudo().browse(vals.get('user_id'))
    #         email_formatted = []
    #         if team_head.partner_id.email_formatted not in email_formatted:
    #             email_formatted.append(team_head.partner_id.email_formatted)
    #         if user_id.partner_id.email_formatted not in email_formatted:
    #             email_formatted.append(user_id.partner_id.email_formatted)
    #         email_formatted_str = ','.join(email_formatted)
    #         email_values = {
    #             'email_from': str(team_head.partner_id.email_formatted),
    #             'email_to': email_formatted_str
    #         }
    #         if allocation_template:
    #             for rec in self:
    #                 allocation_template.sudo().send_mail(
    #                     rec.id, force_send=True, email_values=email_values)
    #                 rec.ticket_allocated = True
    #     elif vals.get('team_id') and vals.get(
    #             'team_head') and not vals.get('user_id') and vals.get(
    #                 'domain_user_ids') and not vals.get('ticket_allocated'):
    #         allocation_template = self.env.company.allocation_mail_template_id
    #         email_formatted = []
    #         users = vals.get('domain_user_ids')[0][2]
    #         user_ids = self.env['res.users'].sudo().browse(users)
    #         team_head = self.env['res.users'].sudo().browse(
    #             vals.get('team_head'))
    #         for user in user_ids:
    #             if user.partner_id.email_formatted not in email_formatted:
    #                 email_formatted.append(user.partner_id.email_formatted)
    #         email_formatted_str = ','.join(email_formatted)
    #         email_values = {
    #             'email_from': str(team_head.partner_id.email_formatted),
    #             'email_to': email_formatted_str
    #         }
    #         if allocation_template:
    #             for rec in self:
    #                 allocation_template.sudo().send_mail(
    #                     rec.id, force_send=True, email_values=email_values)
    #                 rec.ticket_allocated = True
    #     elif not vals.get('team_id') and not vals.get(
    #             'team_head') and vals.get('user_id') and vals.get(
    #                 'domain_user_ids') and not vals.get('ticket_allocated'):
    #         allocation_template = self.env.company.allocation_mail_template_id
    #         email_formatted = []
    #         user_id = self.env['res.users'].sudo().browse(vals.get('user_id'))
    #         users = vals.get('domain_user_ids')[0][2]
    #         user_ids = self.env['res.users'].sudo().browse(users)
    #         if user_id.partner_id.email_formatted not in email_formatted:
    #             email_formatted.append(user_id.partner_id.email_formatted)
    #         for user in user_ids:
    #             if user.id != user_id.id:
    #                 if user.partner_id.email_formatted not in email_formatted:
    #                     email_formatted.append(user.partner_id.email_formatted)
    #         email_formatted_str = ','.join(email_formatted)
    #         email_values = {
    #             'email_from': str(self.env.company.partner_id.email_formatted),
    #             'email_to': email_formatted_str
    #         }
    #         if allocation_template:
    #             for rec in self:
    #                 allocation_template.sudo().send_mail(
    #                     rec.id, force_send=True, email_values=email_values)
    #                 rec.ticket_allocated = True
    #     elif not vals.get('team_id') and not vals.get(
    #             'team_head') and vals.get('user_id') and not vals.get(
    #                 'domain_user_ids') and not vals.get('ticket_allocated'):
    #         allocation_template = self.env.company.allocation_mail_template_id
    #         user_id = self.env['res.users'].sudo().browse(vals.get('user_id'))
    #         email_values = {
    #             'email_from': str(self.env.company.partner_id.email_formatted),
    #             'email_to': str(user_id.partner_id.email_formatted)
    #         }
    #         if allocation_template:
    #             for rec in self:
    #                 allocation_template.sudo().send_mail(
    #                     rec.id, force_send=True, email_values=email_values)
    #                 rec.ticket_allocated = True
    #     elif not vals.get('team_id') and not vals.get(
    #             'team_head') and not vals.get('user_id') and vals.get(
    #                 'domain_user_ids') and not vals.get('ticket_allocated'):
    #         allocation_template = self.env.company.allocation_mail_template_id
    #         users = vals.get('domain_user_ids')[0][2]
    #         user_ids = self.env['res.users'].sudo().browse(users)
    #         email_formatted = []
    #         for user in user_ids:
    #             if user.partner_id.email_formatted not in email_formatted:
    #                 email_formatted.append(user.partner_id.email_formatted)
    #         email_formatted_str = ','.join(email_formatted)
    #         email_values = {
    #             'email_from': str(self.env.company.partner_id.email_formatted),
    #             'email_to': email_formatted_str
    #         }
    #         if allocation_template:
    #             for rec in self:
    #                 allocation_template.sudo().send_mail(
    #                     rec.id, force_send=True, email_values=email_values)
    #                 rec.ticket_allocated = True
    #     return res

    def preview_ticket(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }

    @api.depends('stage_id')
    def _compute_stage_booleans(self):
        if self:
            for rec in self:
                rec.cancel_stage_boolean = False
                rec.done_stage_boolean = False
                rec.reopen_stage_boolean = False
                rec.closed_stage_boolean = False
                rec.open_boolean = False
                if rec.stage_id.id == rec.company_id.cancel_stage_id.id:
                    rec.cancel_stage_boolean = True
                    rec.open_boolean = True
                elif rec.stage_id.id == rec.company_id.done_stage_id.id:
                    rec.done_stage_boolean = True
                    rec.open_boolean = True
                elif rec.stage_id.id == rec.company_id.reopen_stage_id.id:
                    rec.reopen_stage_boolean = True
                    rec.open_boolean = False
                elif rec.stage_id.id == rec.company_id.close_stage_id.id:
                    rec.closed_stage_boolean = True
                    rec.open_boolean = True

    @api.depends('stage_id')
    def _compute_cancel_button_boolean(self):
        if self:
            for rec in self:
                rec.cancel_button_boolean = False
                if rec.stage_id.is_cancel_button_visible:
                    rec.cancel_button_boolean = True

    @api.depends('stage_id')
    def _compute_done_button_boolean(self):
        if self:
            for rec in self:
                rec.done_button_boolean = False
                if rec.stage_id.is_done_button_visible:
                    rec.done_button_boolean = True

    def action_approve(self):
        self.ensure_one()
        if self.stage_id.sh_next_stage:
            self.stage_id = self.stage_id.sh_next_stage.id
            self.change_sh_status()
            self._compute_sla_deadline()
            if self.stage_id.mail_template_ids:
                for template in self.stage_id.mail_template_ids:
                    template.sudo().send_mail(self.id, force_send=True)

    def aciton_draft(self):
        self.ensure_one()
        if self.company_id and self.company_id.new_stage_id:
            self.stage_id = self.company_id.new_stage_id.id

    def action_done(self):
        self.ensure_one()
        if self.company_id and self.company_id.done_stage_id and self.company_id.done_stage_id.mail_template_ids:
            for template in self.company_id.done_stage_id.mail_template_ids:
                template.sudo().send_mail(self.id, force_send=True)
            self.stage_id = self.company_id.done_stage_id.id

    def action_reply(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        template_id = self.company_id.reply_mail_template_id.id
        try:
            compose_form_id = ir_model_data.get_object_reference(
                'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'helpdesk.ticket',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def action_closed(self):
        self.ensure_one()
        if self.company_id and self.company_id.close_stage_id and self.company_id.close_stage_id.mail_template_ids:
            for template in self.company_id.close_stage_id.mail_template_ids:
                template.sudo().send_mail(self.id, force_send=True)
            self.write({
                'close_date': fields.Datetime.now(),
                'close_by': self.env.user.id,
                'closed_stage_boolean': True,
                'stage_id': self.company_id.close_stage_id.id
            })

    def action_cancel(self):
        self.ensure_one()
        logger.info("****************************************")
        logger.info(self.company_id.cancel_stage_id.name)
        if self.company_id and self.company_id.cancel_stage_id and self.company_id.cancel_stage_id.mail_template_ids:
            logger.info("****************************************")
            logger.info(self.company_id.cancel_stage_id.name)
            for template in self.company_id.cancel_stage_id.mail_template_ids:
                template.sudo().send_mail(self.id, force_send=True)
            stage_id = self.company_id.cancel_stage_id
            self.stage_id = stage_id.id
            self.cancel_date = fields.Datetime.now()
            self.cancel_by = self.env.user.id
            self.cancel_stage_boolean = True

    def action_open(self):
        if self.company_id and self.company_id.reopen_stage_id and self.company_id.reopen_stage_id.mail_template_ids:
            for template in self.company_id.reopen_stage_id.mail_template_ids:
                template.sudo().send_mail(self.id, force_send=True)
            self.write({
                'stage_id': self.company_id.reopen_stage_id.id,
                'open_boolean': True,
            })

    @api.onchange('team_id')
    def onchange_team(self):
        if self.team_id:
            self.team_head = self.team_id.team_head
            user_ids = self.env['helpdesk.team'].sudo().search([
                ('id', '=', self.team_id.id)
            ])
            return {
                'domain': {
                    'user_id': [('id', 'in', user_ids.member_ids.ids)],
                    'domain_user_ids': [('id', 'in', user_ids.member_ids.ids)]
                }
            }
        else:
            self.team_head = False

    @api.onchange('category_id')
    def onchange_category(self):
        if self.category_id:
            sub_category_ids = self.env['helpdesk.subcategory'].sudo().search([
                ('parent_category_id', '=', self.category_id.id)
            ]).ids
            return {
                'domain': {
                    'sub_category_id': [('id', 'in', sub_category_ids)]
                }
            }
        else:
            self.sub_category_id = False

    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     if self.partner_id:
    #         self.person_name = self.partner_id.name
    #         self.email = self.partner_id.email
    #         self.mobile_no = self.partner_id.mobile
    #     else:
    #         self.person_name = False
    #         self.email = False
    #         self.mobile_no = False

    @api.model
    def _run_auto_close_ticket(self):
        company_ids = self.env['res.company'].sudo().search([])
        if company_ids:
            for company in company_ids:
                if company.auto_close_ticket:
                    tikcet_ids = self.env['helpdesk.ticket'].sudo().search([
                        ('company_id','=',company.id),
                        ('stage_id','not in',[company.close_stage_id.id]),
                    ])
                    if tikcet_ids:
                        for ticket in tikcet_ids:
                            replied_date = ticket.replied_date
                            if replied_date and ticket.company_id.auto_close_ticket == True:
                                no_of_days = ticket.company_id.close_days
                                end_date = replied_date + timedelta(days=no_of_days)
                                if end_date < fields.Datetime.now() and ticket.state == 'staff_replied':
                                    ticket.action_closed()
