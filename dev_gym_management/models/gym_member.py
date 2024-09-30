# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models, api, _
from datetime import datetime, date
from odoo.exceptions import ValidationError


class GymMember(models.Model):
    _name = 'gym.member'
    _description = 'Gym Member'

    @api.onchange('user_id')
    def onchange_user_id(self):
        if self.user_id:
            self.name = self.user_id.name

    @api.onchange('trainer_id')
    def onchange_trainer_id(self):
        skills = []
        if self.trainer_id:
            if self.trainer_id.skill_ids:
                skills = self.trainer_id.skill_ids.ids
        self.trainer_skill_ids = skills

    @api.model
    def create(self, vals):
        vals['member_sequence'] = self.env['ir.sequence']. next_by_code('member.sequence') or 'New'
        return super(GymMember, self).create(vals)

    def calculate_member_age(self):
        for member in self:
            age = ''
            if member.dob:
                dob = datetime.strptime(str(member.dob), '%Y-%m-%d')
                today = date.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            member.age = str(age)

    def _is_only_member_status(self):
        for member in self:
            only_member = True
            if member.env.user.has_group('dev_gym_management.gym_trainer'):
                only_member = False
            if member.env.user.has_group('dev_gym_management.gym_manager'):
                only_member = False
            member.is_only_member = only_member

    def member_left(self):
        self.left_date = date.today()
        self.state = 'left'

    def left_to_waiting(self):
        self.join_date = False
        self.left_date = False
        self.state = 'waiting'

    def prepare_invoice(self):
        inv_obj = self.env['account.move']
        account_id = False
        product = self.membership_id.product_id
        if product.id:
            account_id = product.property_account_income_id.id
        if not account_id:
            account_id = product.categ_id.property_account_income_categ_id.id
        if not account_id:
            raise ValidationError(
                _('There is no income account defined for this product: "%s". \
                       You may have to install a chart of account from Accounting \
                       app, settings menu.') % (product.name,))
        if self.membership_id.fees <= 0.00:
            raise ValidationError(
                _('The value of the Membership Fees amount must be positive.'))
        name = product.name
        invoice_id = inv_obj.create({
            'name': self.name,
            'move_type': 'out_invoice',
            'partner_id': self.user_id.partner_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'account_id': account_id,
                'price_unit': self.membership_id.fees,
                'quantity': 1.0,
                'product_uom_id': product.uom_id.id,
                'product_id': product.id,
            })],
        })
        if invoice_id:
            all_invoices = self.invoice_ids.ids
            all_invoices.append(invoice_id.id)
            self.invoice_ids = [(6, 0, all_invoices)]

    def member_joined(self):
        self.join_date = date.today()
        self.state = 'joined'

    @api.onchange('membership_id')
    def onchange_membership_id(self):
        if self.membership_id:
            self.membership_fees = self.membership_id.fees

    def _compute_number_of_invoices(self):
        for member in self:
            invoice = 0
            if member.invoice_ids:
                invoice = len(member.invoice_ids)
            member.number_of_invoices = invoice

    def _compute_number_of_diet_pans(self):
        for member in self:
            diet = 0
            if member.member_diet_line_ids:
                diet = len(member.member_diet_line_ids)
            member.number_of_diet_plans = diet

    def _compute_number_of_workout_pans(self):
        for member in self:
            work = 0
            if member.member_workout_line_ids:
                work = len(member.member_workout_line_ids)
            member.number_of_workout_plans = work

    def view_member_invoices(self):
        invoices = self.mapped('invoice_ids')
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    name = fields.Char(string='Name')
    member_sequence = fields.Char(string='Member ID', default='New')
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip')
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string='State')
    country_id = fields.Many2one('res.country', string='Country')
    gender = fields.Selection(string='Gender', selection=[('male', 'Male'),
                                                          ('female', 'Female'),
                                                          ('other', 'Other')], default='male')
    dob = fields.Date(string='Date of Birth')
    age = fields.Char(string='Age', compute='calculate_member_age')
    mobile = fields.Char(string='Mobile')
    email = fields.Char(string='Email')
    trainer_id = fields.Many2one('gym.trainer', string='Trainer')
    trainer_skill_ids = fields.Many2many('trainer.skill', string='Trainer Skill')
    user_id = fields.Many2one('res.users', string='User')
    member_diet_line_ids = fields.One2many('member.diet.detail', 'member_id',  'Diet Plan')
    member_workout_line_ids = fields.One2many('member.workout.detail', 'member_id',  'Workout Plan')
    is_only_member = fields.Boolean(string='Member Only', compute='_is_only_member_status')
    state = fields.Selection(selection=[('waiting', 'Waiting'),
                                        ('joined', 'Joined'),
                                        ('left', 'Left')], default='waiting', string='Status')
    join_date = fields.Date(string='Join date')
    left_date = fields.Date(string='Left Date')
    membership_id = fields.Many2one('gym.membership', string='Membership')
    invoice_ids = fields.One2many('account.move', 'member_id', string='Invoice')
    membership_fees = fields.Float(string='Fees')
    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.user.company_id)
    photo = fields.Image(string='Photo')
    number_of_invoices = fields.Integer(string='Invoices', compute='_compute_number_of_invoices')

class MemberDietDetail(models.Model):
    _name = 'member.diet.detail'
    _description = 'Member Diet Details'

    member_id = fields.Many2one('gym.member', string='Member')
    diet_plan_id = fields.Many2one('diet.plan', string='Diet Plan')
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')


class MemberWorkoutDetail(models.Model):
    _name = 'member.workout.detail'
    _description = 'Member Workout Details'

    member_id = fields.Many2one('gym.member', string='Member')
    workout_plan_id = fields.Many2one('workout.plan', string='Workout Plan')
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: