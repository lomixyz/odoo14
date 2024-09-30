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


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    member_id = fields.Many2one('gym.member', string='Member')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: