# -*- coding: utf-8 -*-

import babel
import datetime
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
import math


class HrBank(models.Model):
	_inherit = 'res.bank'

	main_bank = fields.Boolean(string='Main Bank', default=False, store=True)

	@api.constrains('main_bank')
	def _check_true_value(self):
		records = self.env['res.bank'].search([('main_bank', '=', True)])

		if len(records) > 1:
			raise UserError(_("You can't have more than one Main Bank!"))


class ResPartnerBank(models.Model):
	_inherit = 'res.partner.bank'

	payment_account = fields.Boolean(string='Payment Account', default=False, store=True)

	@api.constrains('payment_account')
	def _check_true_value(self):
		records = self.env['res.partner.bank'].search([('payment_account', '=', True)])

		if len(records) > 1:
			raise UserError(_("You can't have more than one Payment Account!"))
