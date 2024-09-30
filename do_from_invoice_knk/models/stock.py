from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    invoice_id = fields.Many2one('account.move', 'Invoice')

    def action_view_invoice(self):
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        form_view = [(self.env.ref('account.invoice_form').id, 'form')]
        if self.invoice_id.type == 'out_refund':
            action = self.env.ref('account.action_invoice_out_refund').read()[0]
        elif self.invoice_id.type == 'in_invoice':
            action = self.env.ref('account.action_vendor_bill_template').read()[0]
            form_view = [(self.env.ref('account.invoice_supplier_form').id, 'form')]
        elif self.invoice_id.type == 'in_refund':
            action = self.env.ref('account.action_invoice_in_refund').read()[0]
            form_view = [(self.env.ref('account.invoice_supplier_form').id, 'form')]
        if 'views' in action:
            action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        else:
            action['views'] = form_view
        action['res_id'] = self.invoice_id.id
        return action
