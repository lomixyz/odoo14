from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare

MAGIC_COLUMNS = ('id', 'create_uid', 'create_date', 'write_uid', 'write_date')


class AccountMove(models.Model):
    _inherit = "account.move"

    delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_picking_invoice', copy=False)
    picking_ids = fields.Many2many('stock.picking', string="Pickings", copy=False)

    @api.depends('invoice_line_ids')
    def _compute_picking_invoice(self):
        for move in self:
            move.delivery_count = len(move.picking_ids)

    @api.model
    def _prepare_picking(self, move, picking_type_id):
        location_id = picking_type_id.default_location_src_id.id
        location_dest_id = move.partner_id.property_stock_customer.id
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

    def _prepare_stock_moves(self, move, line, picking_type_id, picking):
        res = []
        if line.product_id.type not in ['product', 'consu']:
            return res
        qty = line.quantity - line.delivered_qty
        price_unit = line.price_unit
        location_id = picking_type_id.default_location_src_id.id
        location_dest_id = move.partner_id.property_stock_customer.id
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

    def button_create_picking(self):
        domain = [('code', '=', 'outgoing')]
        picking_type_id = self.env['stock.picking.type'].search(domain, limit=1)
        if any([ptype in ['product'] for ptype in self.invoice_line_ids.mapped('product_id.type')]):
            res = self._prepare_picking(self, picking_type_id)
            picking = self.env['stock.picking'].create(res)
            self.picking_ids = [(4, picking.id)]
            for line in self.invoice_line_ids:
                move_vals = self._prepare_stock_moves(self, line, picking_type_id, picking)
                line.delivered_qty = line.quantity
                for move_val in move_vals:
                    self.env['stock.move']\
                        .create(move_val)\
                        # ._action_confirm()\
                        # ._action_assign()
            self.env.cr.commit()
            # try:
            #     res = picking.button_validate()
            #     if res:
            #         if res.get('res_model') == 'stock.immediate.transfer':
            #             wizard = self.env['stock.immediate.transfer'].browse(res.get('res_id'))
            #             wizard.process()
            #             return True
            #     return res
            # except Exception:
            #     pass
        return True

    def button_create_return_picking(self):
        action_rec = self.env.ref("do_from_invoice_knk.draft_validate_wizard_id")
        line_ids = []
        for line in self.invoice_line_ids.filtered(lambda x: x.product_id.type == 'product'):
            line_ids.append((0, 0, {
                    'product_id': line.product_id.id, 'quantity': line.delivered_qty, 'line_id': line.id,
                    'name': line.name, 'product_uom_id': line.product_uom_id.id, 'price_unit': line.price_unit
                }))
        if action_rec:
            action = action_rec.read([])[0]
            action['context'] = dict(self.env.context, default_line_ids=line_ids, default_invoice_id=self.id)
            return action
        return True

    def action_delivery_invoice(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        pickings = self.mapped('picking_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id
        # Prepare the context.
        picking_id = pickings.filtered(lambda l: l.picking_type_id.code == 'outgoing')
        if picking_id:
            picking_id = picking_id[0]
        else:
            picking_id = pickings[0]
        action['context'] = dict(self._context, default_partner_id=self.partner_id.id,
                                 default_picking_id=picking_id.id, default_picking_type_id=picking_id.picking_type_id.id, default_origin=self.name, default_group_id=picking_id.group_id.id)
        return action


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    delivered_qty = fields.Float(string="Delivered Qty", digits='Product Unit of Measure', copy=False)

    def _update_line_quantity(self, values):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        line_products = self.filtered(lambda l: l.product_id.type in ['product', 'consu'])
        if line_products.mapped('delivered_qty') and float_compare(values['quantity'], max(line_products.mapped('delivered_qty')), precision_digits=precision) == -1:
            raise UserError(_('You cannot decrease the ordered quantity below the delivered quantity.'))

    def write(self, values):
        if 'quantity' in values:
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            self.filtered(
                lambda r: float_compare(r.quantity, values['quantity'], precision_digits=precision) != 0)._update_line_quantity(values)
        result = super(AccountMoveLine, self).write(values)
        return result

