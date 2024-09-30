from odoo import fields, models, api, _


class ReturnInvoiceQty(models.TransientModel):
    _name = 'return.invoice.qty'
    _description = 'Return Invoice Qty'

    invoice_id = fields.Many2one('account.move', 'Invoice')
    line_ids = fields.One2many('return.invoice.qty.line', 'wizard_id', 'Lines')

    @api.model
    def _prepare_picking(self, move, picking_type_id, origin_picking):
        location_id = origin_picking.location_dest_id.id
        location_dest_id = origin_picking.location_id.id
        return {
            'picking_type_id': picking_type_id.id,
            'partner_id': move.partner_id.id,
            'date': move.invoice_date,
            'location_dest_id': location_dest_id,
            'location_id': location_id,
            'company_id': move.company_id.id,
            'invoice_id': move.id,
            'move_type': 'direct'
        }

    def _prepare_stock_moves(self, move, line, picking_type_id, picking, origin_picking):
        res = []
        if line.product_id.type not in ['product', 'consu']:
            return res
        qty = line.quantity
        price_unit = line.price_unit
        location_id = origin_picking.location_dest_id.id
        location_dest_id = origin_picking.location_id.id
        template = {
            'name': line.name,
            'product_id': line.product_id.id,
            'product_uom': line.product_uom_id.id,
            'product_uom_qty': qty,
            'quantity_done': qty,
            'date': move.invoice_date or fields.Datetime.now(),
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'picking_id': picking.id,
            'partner_id': move.partner_id.id,
            'state': 'draft',
            'company_id': move.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': picking_type_id.id,
            'route_ids': picking_type_id.warehouse_id and [(6, 0, [x.id for x in picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id': picking_type_id.warehouse_id.id,
        }
        res.append(template)
        return res

    def create_returns(self):
        pickings = self.invoice_id.picking_ids.filtered(lambda x: x.state == 'done')
        if pickings:
            picking_type_id = self.env['stock.picking.type'].search([('code', '=', 'incoming')], limit=1)
            res = self._prepare_picking(self.invoice_id, picking_type_id, pickings[-1])
            picking = self.env['stock.picking'].create(res)
            self.invoice_id.picking_ids = [(4, picking.id)]
            for line in self.line_ids:
                move_vals = self._prepare_stock_moves(self.invoice_id, line, picking_type_id, picking, pickings[-1])
                for move_val in move_vals:
                    self.env['stock.move']\
                        .create(move_val)\
                        ._action_confirm()\
                        ._action_assign()
            self.env.cr.commit()
            try:
                res = picking.button_validate()
                if res:
                    if res.get('res_model') == 'stock.immediate.transfer':
                        wizard = self.env['stock.immediate.transfer'].browse(res.get('res_id'))
                        wizard.process()
                        return True
                return res
            except Exception:
                pass
        return True


class ReturnInvoiceQtyLine(models.TransientModel):
    _name = 'return.invoice.qty.line'
    _description = 'Return Invoice Qty Line'

    name = fields.Char()
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    product_id = fields.Many2one("product.product", "Product")
    quantity = fields.Float(string='Quantity', default=1.0, digits='Product Unit of Measure')
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    line_id = fields.Many2one('account.move.line', 'Invoice Line')
    wizard_id = fields.Many2one('return.invoice.qty', 'Wizard')
