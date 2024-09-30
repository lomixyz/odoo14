# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class CustomRent(models.Model):
    _inherit = 'sale.order.line'

    @api.constrains('pickup_date', 'return_date')
    # @api.onchange('return_date','pickup_date')
    def _check_reservation(self):
        orders = self.env['sale.order'].search(
            [('rental_status', 'in', ['pickup', 'return']), ('is_rental_order', '=', True)])
        products = []
        print("*****************************",self.ids)
        for rec in self:
            print(rec.id)
            if rec.product_id.rent_ok:
                start = orders.order_line.search([
                    ('is_rental', '=', True),
                    ('product_id', 'in', [rec.product_id.id]), ('order_id', 'in', orders.ids),
                    ('pickup_date', '<=', rec.pickup_date),
                    ('pickup_date', '>=', rec.return_date)
                    ]).ids
                end = orders.order_line.search([
                    ('is_rental', '=', True),
                    ('product_id', 'in', [rec.product_id.id]), ('order_id', 'in', orders.ids),
                    ('return_date', '<=', rec.return_date),
                    ('return_date', '>=', rec.pickup_date)
                    ]).ids
                if (end or start):
                    raise UserError(_('The  {} Product in Rental.'.format(rec.product_id.name)))


#                 order_lines = orders.order_line.search([
#                     ('is_rental', '=', True),
#                     ('product_id', 'in', [rec.product_id.id]), ('order_id', 'in', orders.ids),
#                 ])
#                 print(rec.pickup_date)
#                 print(rec.return_date)
#                 print(start)
# # (rec.pickup_date,'>','pickup_date'),(rec.pickup_date ,'<','return_date')
#                 print(end)
#                 for o in order_lines:
#                     print(o.pickup_date)
#                     print(o.return_date)
#                     datarang = [o.pickup_date.date() + timedelta(days=x) for x in
#                                 range((o.return_date - o.pickup_date).days + 1)]
#                     if (rec.pickup_date.date() in datarang):
#                         raise UserError(_('The Start Date {} Product in Rental.'.format(o.product_id.name)))

#                     if (rec.return_date.date() in datarang):
#                         raise UserError(_('The End Date {} Product in Rental.'.format(o.product_id.name)))

                    
