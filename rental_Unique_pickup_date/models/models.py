# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class CustomRent(models.Model):
    _inherit = 'sale.order.line'

    @api.constrains('pickup_date', 'return_date')
    def _check_reservation(self):
        for rec in self:
            orders = self.env['sale.order'].search([('rental_status', 'in', ['pickup', 'return'])])
            print(orders.ids)
            order_lines = orders.order_line.search(
                [('product_id', '=', self.product_id.id), ('pickup_date', '>=', self.pickup_date),
                 ('return_date', '<=', self.return_date)])
            print(order_lines.ids)
            if order_lines:
                raise UserError(_('The {} Product in Rental.'.format(self.product_id.name)))
