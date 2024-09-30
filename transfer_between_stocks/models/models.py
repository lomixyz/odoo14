# # -*- coding: utf-8 -*-

from odoo import models, fields


class Transfer(models.Model):
    _inherit = 'stock.picking'

    is_transfer = fields.Boolean('Transfer to another Stocks')
    picking_type_transfer_id = fields.Many2one("stock.picking.type", string="Another stock Operation")

    def button_validate(self):
        res = super(Transfer, self).button_validate()
        if self.is_transfer:
            move_line_ids = []
            src_loction = self.picking_type_id.default_location_dest_id.id
            for line_id in self.move_ids_without_package:
                move_line_ids.append((0, 0, {'product_id': line_id.product_id.id,
                                             'quantity_done': line_id.quantity_done,
                                             'product_uom': line_id.product_uom,
                                             'description_picking': line_id.description_picking,
                                             'lot_ids': line_id.lot_ids,
                                             'date_deadline': line_id.date_deadline,
                                             'name': line_id.name
                                             })),

            self.create({
                'partner_id': self.partner_id.id,
                'state': 'assigned',
                'picking_type_id': self.picking_type_transfer_id.id,
                'scheduled_date': self.scheduled_date,
                'location_dest_id': self.picking_type_transfer_id.default_location_dest_id.id,
                'location_id': self.location_dest_id.id,
                'origin': self.origin,
                'move_ids_without_package': move_line_ids,
            })
            return res
