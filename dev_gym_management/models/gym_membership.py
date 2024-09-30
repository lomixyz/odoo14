

# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models


class GymMembership(models.Model):
    _name = 'gym.membership'
    _description = 'Gym Membership'

    name = fields.Char('Name')
    months = fields.Integer(string='Number of Months')
    fees = fields.Float(string='Fees')
    product_id = fields.Many2one('product.product', string='Membership Product')
    details = fields.Text(string='Details')

# vim:expandtab:smartindent:tabsto  p=4:softtabstop=4:shiftwidth=4: