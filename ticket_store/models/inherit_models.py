# -*- coding: utf-8 -*-
import odoo.api
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    ticket_id = fields.Many2one('tickets.tickets', string='Ticket')
    is_ticket = fields.Boolean(compute='_compute_is_ticket', store=True)

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for record in self:
            tickets = self.env["tickets.tickets"].search([('purchase_id', '=', record.id)])
            if not tickets:
                record.ticket_id.purchase_id = record.id
                record.is_ticket = True
        return res

    @api.depends('ticket_id')
    def _compute_is_ticket(self):
        if self.ticket_id:
            self.is_ticket = True
        else:
            self.is_ticket = False

    @api.onchange('ticket_id','invoice_ids')
    def onchange_method(self):
        if self.ids :
            for purchase in self:
                tickets = self.env['tickets.tickets'].search([('purchase_id', '=', purchase.ids[0])])
                for rec in tickets:
                    rec.purchase_id = False
                    rec.is_purchase = False
                    rec.bill_id=False
                purchase.ticket_id.purchase_id = purchase.ids[0]
                purchase.is_ticket = True
                purchase.ticket_id.bill_id= purchase.invoice_ids.ids[0] if purchase.invoice_ids.ids else False 

    def _prepare_invoice(self):
        """Prepare the dict of values to create the new invoice for a purchase order.
        """
        invoice_vals = super(PurchaseOrder, self)._prepare_invoice()
        invoice_vals['ticket_id'] = self.ticket_id.id
        return invoice_vals
        
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ticket_id = fields.Many2one('tickets.tickets', string='Ticket')
    is_ticket = fields.Boolean(compute='_compute_is_ticket', store=True)

    @api.depends('ticket_id')
    def _compute_is_ticket(self):
        if self.ticket_id:
            self.is_ticket = True
        else:
            self.is_ticket = False


    @api.onchange('ticket_id','invoice_ids')
    def onchange_ticket(self):
        if self.ids :
            for sale in self:
                tickets = self.env['tickets.tickets'].search([('sale_id', '=', sale.ids[0])])
                for rec in tickets:
                    rec.sale_id = False
                    rec.is_sale = False
                    rec.invoice_id=False
                sale.ticket_id.sale_id = sale.ids[0]
                sale.is_ticket = True
                sale.ticket_id.invoice_id=sale.invoice_ids.ids[0] if sale.invoice_ids.ids else False 

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for record in self:
            tickets = self.env["tickets.tickets"].search([('sale_id', '=', record.id)])
            if not tickets:
                record.ticket_id.sale_id = record.id
                record.is_ticket = True
        return res

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['ticket_id'] = self.ticket_id.id
        return invoice_vals
        

class AccountMove(models.Model):
    _inherit = "account.move"

    ticket_id = fields.Many2one('tickets.tickets', string='Ticket')

    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self.move_type == 'out_invoice':
            self.ticket_id.invoice_id = self.ids[0]
        elif self.move_type == 'in_invoice':
            self.ticket_id.bill_id = self.ids[0]
        return res
