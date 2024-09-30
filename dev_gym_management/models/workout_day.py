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


class WorkoutDay(models.Model):
    _name = 'workout.day'
    _description = 'Workout Day'

    name = fields.Char('Name')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: