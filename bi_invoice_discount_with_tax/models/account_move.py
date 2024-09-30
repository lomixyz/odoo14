# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import UserError, ValidationError


class account_move(models.Model):
	_inherit = 'account.move'


	@api.depends('discount_amount')
	def _calculate_discount(self):
		res_config= self.env['res.config.settings'].sudo().search([],order="id desc", limit=1)
		
		if res_config:
			for self_obj in self:
				after_amount_tax = 0.0
				if res_config.tax_discount_policy == 'untax':
					if self_obj.discount_type == 'global':
						if self_obj.discount_method == 'fix':
							sums = 0.0
							before_amount_tax = self_obj.amount_tax
							self_obj.discount_amt = self_obj.discount_amount if self_obj.amount_untaxed > 0 else 0
							if self.invoice_line_ids:
								for line in self.invoice_line_ids:
									if line.tax_ids:
										if self.amount_untaxed:
											final_discount = ((self.discount_amt*line.price_subtotal)/self.amount_untaxed)
											discount = (line.price_unit * line.quantity) - final_discount
											taxes = line.tax_ids.compute_all(discount, self.currency_id, line.quantity,line.product_id,self.partner_id,is_refund=None,handle_price_include=None)
											sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
							after_amount_tax = before_amount_tax - sums
							self.amount_total = sums + self.amount_untaxed - self.discount_amt
       						# self.amount_tax = sums				
							self_obj._recompute_tax_lines(recompute_tax_base_amount=True)
							self_obj._onchange_recompute_dynamic_lines()
											
						elif self_obj.discount_method == 'per':
							
							sums = 0.0
							before_amount_tax = self_obj.amount_tax
							self_obj.discount_amt = self_obj.discount_amount if self_obj.amount_untaxed > 0 else 0
							if self.invoice_line_ids:
								for line in self.invoice_line_ids:
									if line.tax_ids:
										if self.amount_untaxed:
											final_discount = ((self.discount_amount*line.price_subtotal)/100)
											discount = (line.price_unit * line.quantity) - final_discount
											taxes = line.tax_ids.compute_all(discount, self.currency_id, line.quantity,line.product_id,self.partner_id,is_refund=None,handle_price_include=None)
											sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
							after_amount_tax = before_amount_tax - sums
							self.amount_total = sums + self.amount_untaxed - self.discount_amt
       						# self.amount_tax = sums				
							self_obj._recompute_tax_lines(recompute_tax_base_amount=True)
							self_obj._onchange_recompute_dynamic_lines()
							
					else:
						self_obj.discount_amt = 0.0

					if self_obj.discount_type == 'line':
						total=0
						for data in self.invoice_line_ids:

							if data.discount_method == 'fix':
								total += data.discount_amount if self_obj.amount_untaxed > 0 else 0
							elif data.discount_method == 'per':
								total += data.price_subtotal * (data.discount_amount/ 100)
						self_obj.discount_amt_line=total
					else:
						self_obj.discount_amt_line = 0.0
					
					self_obj.amount_total = self_obj.amount_tax + self_obj.amount_untaxed - self_obj.discount_amt - self_obj.discount_amt_line

				elif res_config.tax_discount_policy == 'tax' :
					if self_obj.discount_type == 'global':
						if self_obj.discount_method == 'fix':
							self_obj.discount_amt = self_obj.discount_amount if self_obj.amount_untaxed > 0 else 0
						elif self_obj.discount_method == 'per':
							self_obj.discount_amt = (self.amount_untaxed + self.amount_tax) * (self.discount_amount / 100.0)
					else:
						self_obj.discount_amt = 0.0

					if self_obj.discount_type == 'line':
						total=0
						for data in self.invoice_line_ids:

							if data.discount_method == 'fix':
								total += data.discount_amount if self_obj.amount_untaxed > 0 else 0
							elif data.discount_method == 'per':
								total += data.price_subtotal * (data.discount_amount/ 100)
						self_obj.discount_amt_line=total
					else:
						self_obj.discount_amt_line = 0.0
					
					self_obj.amount_total = self_obj.amount_tax + self_obj.amount_untaxed - self_obj.discount_amt - self_obj.discount_amt_line
				
				else:
					self_obj.amount_total = self_obj.amount_tax + self_obj.amount_untaxed - self_obj.discount_amt - self_obj.discount_amt_line
				
				
				if self.move_type == 'out_invoice' and not res_config.sale_account_id:
					return
				if self.move_type == 'in_invoice' and not res_config.purchase_account_id:
					return
				
				move_line = self.line_ids.filtered(lambda x : x.name == 'Discount')
				if self.is_inbound():
					discount_account = res_config.sale_account_id and res_config.sale_account_id.id
					move_line._origin.price_total = move_line._origin.price_total + after_amount_tax
					move_line._origin.price_subtotal = move_line._origin.price_subtotal + after_amount_tax
					
				else:
					discount_account = res_config.purchase_account_id and res_config.purchase_account_id.id
					
				if move_line:
					move_line.update({
						'account_id' : discount_account,
					})
				else:
					discount_line = {
						'account_id' : discount_account,
						'price_unit' : 0.00,
						'quantity': 1,
						'name': "Discount",
						'exclude_from_invoice_tab': True,
						}
					self.with_context(check_move_validity=False).update({'line_ids' : [(0,0,discount_line)],})
					self._onchange_recompute_dynamic_lines()
	
	@api.onchange('discount_method','discount_type','discount_amount','invoice_line_ids','line_ids')
	def onchange_type(self):
		move_line = self.line_ids.filtered(lambda x : x.name == 'Discount')
		if move_line and move_line.move_id.is_invoice():
			move_id = move_line.move_id
			currency_id = move_id.currency_id
			company_currency = move_id.company_currency_id
			if move_id.move_type == 'entry' or move_id.is_outbound():
				sign = 1
			else:
				sign = -1
			move_id._calculate_discount()
			if self.discount_type == 'global':
				discount_value = self.discount_amt
				
			elif self.discount_type == 'line':
				discount_value = self.discount_amt_line
    		
			if move_id.is_inbound():
				move_line_id = self.line_ids.filtered(lambda x : not x.name == 'Discount' and (x.debit > 0.0 and x.credit == 0.0))
				credit_lines = self.line_ids.filtered(lambda line : line.credit > 0.0)
				total_debit = sum(line.amount_currency for line in credit_lines) 
				
				if currency_id != company_currency:
					move_line_id.update({
						'amount_currency' : (sign * total_debit) - discount_value
					})
					move_line_id
					move_line_id._onchange_amount_currency()
					to_ = currency_id._convert(discount_value, company_currency, move_id.company_id, move_id.date)

					move_line.update({
						'amount_currency' : discount_value,
						'debit' : to_,
					})
				else:
					move_line_id.update({
						'debit' : (sign * total_debit) - discount_value
					})
					move_line.update({
						'debit' : discount_value
					})
			else:
				move_line_id = self.line_ids.filtered(lambda x : not x.name == 'Discount' and (x.debit == 0.0 and x.credit > 0.0))
				debit_lines = self.line_ids.filtered(lambda line : line.debit > 0.0)
				total_credit = sum(line.amount_currency for line in debit_lines) 
				if currency_id != company_currency:
					move_line_id.update({
						'amount_currency' : (sign * total_credit) - discount_value
						})
					
					move_line_id._onchange_amount_currency()
					to_ = currency_id._convert(discount_value, company_currency, move_id.company_id, move_id.date)
					
					move_line.update({
						'amount_currency' : discount_value,
						'credit' : to_,
						})
				else:
					move_line_id.update({
						'credit' : (sign * total_credit) - discount_value
						})
					move_line.update({
						'credit' : discount_value
						})
	
	def _recompute_tax_lines(self, recompute_tax_base_amount=False):
		''' Compute the dynamic tax lines of the journal entry.

		:param lines_map: The line_ids dispatched by type containing:
			* base_lines: The lines having a tax_ids set.
			* tax_lines: The lines having a tax_line_id set.
			* terms_lines: The lines generated by the payment terms of the invoice.
			* rounding_lines: The cash rounding lines of the invoice.
		'''
		self.ensure_one()
		in_draft_mode = self != self._origin

		def _serialize_tax_grouping_key(grouping_dict):
			''' Serialize the dictionary values to be used in the taxes_map.
			:param grouping_dict: The values returned by '_get_tax_grouping_key_from_tax_line' or '_get_tax_grouping_key_from_base_line'.
			:return: A string representing the values.
			'''
			return '-'.join(str(v) for v in grouping_dict.values())

		def _compute_base_line_taxes(base_line):
			''' Compute taxes amounts both in company currency / foreign currency as the ratio between
			amount_currency & balance could not be the same as the expected currency rate.
			The 'amount_currency' value will be set on compute_all(...)['taxes'] in multi-currency.
			:param base_line:   The account.move.line owning the taxes.
			:return:            The result of the compute_all method.
			'''
			move = base_line.move_id

			if move.is_invoice(include_receipts=True):
				handle_price_include = True
				sign = -1 if move.is_inbound() else 1
				quantity = base_line.quantity
				is_refund = move.move_type in ('out_refund', 'in_refund')
				price_unit_wo_discount = sign * base_line.price_unit * (1 - (base_line.discount / 100.0))
			else:
				handle_price_include = False
				quantity = 1.0
				tax_type = base_line.tax_ids[0].type_tax_use if base_line.tax_ids else None
				is_refund = (tax_type == 'sale' and base_line.debit) or (tax_type == 'purchase' and base_line.credit)
				price_unit_wo_discount = base_line.balance

			res_config= self.env['res.config.settings'].sudo().search([],order="id desc", limit=1)
			if res_config:
				for rec in self:
					if res_config.tax_discount_policy == 'untax':
						if rec.discount_type == 'line':
							
							if base_line.discount_method == 'fix':
								price_unit_wo_discount = base_line.price_subtotal - base_line.discount_amount
							elif base_line.discount_method == 'per':
					
								price_unit_wo_discount = base_line.price_subtotal * (1 - (base_line.discount_amount / 100.0))

						elif rec.discount_type == 'global':
							if rec.amount_untaxed != 0.0:
								final_discount = ((rec.discount_amt*base_line.price_subtotal)/rec.amount_untaxed)
								price_unit_wo_discount = base_line.price_subtotal - rec.currency_id.round(final_discount)
							else:
								final_discount = (rec.discount_amt*base_line.price_subtotal)/1.0
								price_unit_wo_discount = base_line.price_subtotal - rec.currency_id.round(final_discount)
					if res_config.tax_discount_policy == 'tax':
						if self._context.get('default_move_type') in ['out_invoice','out_receipt']:
							sign = -(sign)
						else:
							pass		
				price_unit_wo_discount = sign*price_unit_wo_discount 
				

			balance_taxes_res = base_line.tax_ids._origin.compute_all(
				price_unit_wo_discount,
				currency=base_line.currency_id,
				quantity=quantity,
				product=base_line.product_id,
				partner=base_line.partner_id,
				is_refund=is_refund,
				handle_price_include=handle_price_include,
			)
			

			if move.move_type == 'entry':
				repartition_field = is_refund and 'refund_repartition_line_ids' or 'invoice_repartition_line_ids'
				repartition_tags = base_line.tax_ids.mapped(repartition_field).filtered(lambda x: x.repartition_type == 'base').tag_ids
				tags_need_inversion = (tax_type == 'sale' and not is_refund) or (tax_type == 'purchase' and is_refund)
				if tags_need_inversion:
					balance_taxes_res['base_tags'] = base_line._revert_signed_tags(repartition_tags).ids
					for tax_res in balance_taxes_res['taxes']:
						tax_res['tag_ids'] = base_line._revert_signed_tags(self.env['account.account.tag'].browse(tax_res['tag_ids'])).ids
					
			return balance_taxes_res

		taxes_map = {}

		# ==== Add tax lines ====
		to_remove = self.env['account.move.line']
		for line in self.line_ids.filtered('tax_repartition_line_id'):
			grouping_dict = self._get_tax_grouping_key_from_tax_line(line)
			grouping_key = _serialize_tax_grouping_key(grouping_dict)
			if grouping_key in taxes_map:
				# A line with the same key does already exist, we only need one
				# to modify it; we have to drop this one.
				to_remove += line
			else:
				taxes_map[grouping_key] = {
					'tax_line': line,
					'amount': 0.0,
					'tax_base_amount': 0.0,
					'grouping_dict': False,
				}
		self.line_ids -= to_remove

		# ==== Mount base lines ====
		for line in self.line_ids.filtered(lambda line: not line.tax_repartition_line_id):
			# Don't call compute_all if there is no tax.
			if not line.tax_ids:
				line.tax_tag_ids = [(5, 0, 0)]
				continue

			compute_all_vals = _compute_base_line_taxes(line)

			# Assign tags on base line
			line.tax_tag_ids = compute_all_vals['base_tags']

			tax_exigible = True
			for tax_vals in compute_all_vals['taxes']:
				grouping_dict = self._get_tax_grouping_key_from_base_line(line, tax_vals)
				grouping_key = _serialize_tax_grouping_key(grouping_dict)

				tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_vals['tax_repartition_line_id'])
				tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id

				if tax.tax_exigibility == 'on_payment':
					tax_exigible = False

				taxes_map_entry = taxes_map.setdefault(grouping_key, {
					'tax_line': None,
					'amount': 0.0,
					'tax_base_amount': 0.0,
					'grouping_dict': False,
				})
				taxes_map_entry['amount'] += tax_vals['amount']
				taxes_map_entry['tax_base_amount'] += tax_vals['base']
				taxes_map_entry['grouping_dict'] = grouping_dict
			line.tax_exigible = tax_exigible

		# ==== Process taxes_map ====
		for taxes_map_entry in taxes_map.values():
			# The tax line is no longer used in any base lines, drop it.
			if taxes_map_entry['tax_line'] and not taxes_map_entry['grouping_dict']:
				self.line_ids -= taxes_map_entry['tax_line']
				continue

			currency = self.env['res.currency'].browse(taxes_map_entry['grouping_dict']['currency_id'])

			# Don't create tax lines with zero balance.
			if currency.is_zero(taxes_map_entry['amount']):
				if taxes_map_entry['tax_line']:
					self.line_ids -= taxes_map_entry['tax_line']
				continue

			tax_base_amount = (-1 if self.is_inbound() else 1) * taxes_map_entry['tax_base_amount']
			# tax_base_amount field is expressed using the company currency.
			tax_base_amount = currency._convert(tax_base_amount, self.company_currency_id, self.company_id, self.date or fields.Date.context_today(self))

			# Recompute only the tax_base_amount.
			if taxes_map_entry['tax_line'] and recompute_tax_base_amount:
				taxes_map_entry['tax_line'].tax_base_amount = tax_base_amount
				continue

			balance = currency._convert(
				taxes_map_entry['amount'],
				self.journal_id.company_id.currency_id,
				self.journal_id.company_id,
				self.date or fields.Date.context_today(self),
			)
			
			to_write_on_line = {
				'amount_currency': taxes_map_entry['amount'],
				'currency_id': taxes_map_entry['grouping_dict']['currency_id'],
				'debit': balance > 0.0 and balance or 0.0,
				'credit': balance < 0.0 and -balance or 0.0,
				'tax_base_amount': tax_base_amount,
			}

			if taxes_map_entry['tax_line']:
				# Update an existing tax line.
				taxes_map_entry['tax_line'].update(to_write_on_line)
			else:
				create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
				tax_repartition_line_id = taxes_map_entry['grouping_dict']['tax_repartition_line_id']
				tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_repartition_line_id)
				tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id
				taxes_map_entry['tax_line'] = create_method({
					**to_write_on_line,
					'name': tax.name,
					'move_id': self.id,
					'partner_id': line.partner_id.id,
					'company_id': line.company_id.id,
					'company_currency_id': line.company_currency_id.id,
					'tax_base_amount': tax_base_amount,
					'exclude_from_invoice_tab': True,
					'tax_exigible': tax.tax_exigibility == 'on_invoice',
					**taxes_map_entry['grouping_dict'],
				})

			if in_draft_mode:
				taxes_map_entry['tax_line'].update(taxes_map_entry['tax_line']._get_fields_onchange_balance(force_computation=True))




	@api.depends(
		'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
		'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
		'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
		'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
		'line_ids.debit',
		'line_ids.credit',
		'line_ids.currency_id',
		'line_ids.amount_currency',
		'line_ids.amount_residual',
		'line_ids.amount_residual_currency',
		'line_ids.payment_id.state',
		'line_ids.full_reconcile_id','discount_method','discount_type','discount_amount')
	def _compute_amount(self):
		super(account_move, self)._compute_amount()
		for rec in self:
			
			rec._calculate_discount()
			sign = rec.move_type in ['out_refund','in_refund'] and -1 or 1
			rec.amount_total_signed = rec.amount_total * sign
			if rec.state == 'draft' and (rec.move_type == 'in_invoice' or rec.move_type == 'out_invoice'):
				rec.amount_residual = rec.amount_total
				rec.amount_residual_signed = rec.amount_total
				rec.amount_total_signed =  abs(rec.amount_total) if rec.move_type == 'entry' else -rec.amount_total
			if rec.state == 'posted' and (rec.move_type == 'in_invoice' or rec.move_type == 'out_invoice'):
				res_config= self.env['res.config.settings'].sudo().search([],order="id desc", limit=1)
				if res_config.tax_discount_policy == 'untax':
					rec.amount_residual =  rec.amount_total
					rec.amount_residual_signed = rec.amount_total
				
					if rec.payment_state == 'paid':
						rec.amount_residual = 0
				if rec.amount_residual == 0:
					rec.payment_state = 'paid'


		res_config= self.env['res.config.settings'].sudo().search([],order="id desc", limit=1)
		if res_config:
			for rec in self:
				if rec.discount_amt_line or rec.discount_amt:
					if rec.move_type in ['out_invoice','out_receipt','out_refund']:
						if res_config.sale_account_id:
							rec.discount_account_id = res_config.sale_account_id.id
							
						else:
							account_id = False
							account_id = rec.env['account.account'].search([('user_type_id.name','=','Expenses'), ('discount_account','=',True)],limit=1)
							if not account_id:
								raise UserError(_('Please define an sale discount account for this company.'))
							else:
								rec.discount_account_id = account_id.id

					if rec.move_type in ['in_invoice','in_receipt','in_refund']:
						if res_config.purchase_account_id:
							rec.discount_account_id = res_config.purchase_account_id.id
						else:
							account_id = False
							account_id = rec.env['account.account'].search([('user_type_id.name','=','Income'), ('discount_account','=',True)],limit=1)
							if not account_id:
								raise UserError(_('Please define an purchase discount account for this company.'))
							else:
								rec.discount_account_id = account_id.id


			
	discount_method = fields.Selection([('fix', 'Fixed'), ('per', 'Percentage')],'Discount Method')
	discount_amount = fields.Float('Discount Amount')
	discount_amt = fields.Float(string='- Discount', readonly=True,store=True,digits='Discount',compute='_compute_amount')
	amount_untaxed = fields.Float(string='Subtotal', digits='Account',store=True, readonly=True, compute='_compute_amount',track_visibility='always')
	amount_tax = fields.Float(string='Tax', digits='Account',store=True, readonly=True, compute='_compute_amount')
	amount_total = fields.Float(string='Total', digits='Account',store=True, readonly=True, compute='_compute_amount')
	discount_type = fields.Selection([('line', 'Order Line'), ('global', 'Global')], 'Discount Applies to',default='global')
	discount_account_id = fields.Many2one('account.account', 'Discount Account',store=True)
	discount_amt_line = fields.Float(compute='_compute_amount', string='- Line Discount', digits='Discount', store=True, readonly=True)
	discount_amount_line = fields.Float(string="Discount Line")
	is_line = fields.Boolean('Is a line')
    
	
	
	
