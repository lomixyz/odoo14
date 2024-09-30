# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models, api
from datetime import date, datetime


class Trainer(models.Model):
    _name = 'gym.trainer'
    _description = 'Gym Trainer'

    @api.model
    def create(self, vals):
        vals['trainer_sequence'] = self.env['ir.sequence']. next_by_code('trainer.sequence') or 'New'
        return super(Trainer, self).create(vals)

    @api.onchange('user_id')
    def onchange_user_id(self):
        if self.user_id:
            self.name = self.user_id.name

    def trainer_joined(self):
        self.join_date = date.today()
        self.state = 'joined'

    def trainer_left(self):
        self.left_date = date.today()
        self.state = 'left'

    def left_to_waiting(self):
        self.join_date = False
        self.left_date = False
        self.state = 'waiting'

    def calculate_trainer_age(self):
        for trainer in self:
            age = ''
            if trainer.dob:
                dob = datetime.strptime(str(trainer.dob), '%Y-%m-%d')
                today = date.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            trainer.age = str(age)

    name = fields.Char('Name')
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip')
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string='State')
    country_id = fields.Many2one('res.country', string='Country')
    trainer_sequence = fields.Char(string='Trainer ID', default='New')
    user_id = fields.Many2one('res.users', string='User')
    skill_ids = fields.Many2many('trainer.skill', string='Skill')
    state = fields.Selection(selection=[('waiting', 'Waiting'),
                                        ('joined', 'Joined'),
                                        ('left', 'Left')], default='waiting', string='Status')
    gender = fields.Selection(string='Gender', selection=[('male', 'Male'),
                                                          ('female', 'Female'),
                                                          ('other', 'Other')], default='male')
    dob = fields.Date(string='Date of Birth')
    age = fields.Char(string='Age', compute='calculate_trainer_age')
    join_date = fields.Date(string='Join date')
    left_date = fields.Date(string='Left Date')
    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.user.company_id)
    photo = fields.Image(string='Photo')
    mobile = fields.Char('Mobile')
    email = fields.Char('Email')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: