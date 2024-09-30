# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import werkzeug.urls

from odoo import fields, models, _


class SMSComposer(models.TransientModel):
    _inherit = 'msegat.sms'

    # TODO

