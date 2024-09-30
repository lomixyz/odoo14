# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class TicketsStore(models.Model):
    _name = 'tickets.store'
    _description = 'TicketStore main model'
    _inherit = ['portal.mixin', 'mail.thread.cc', 'mail.activity.mixin']

    name = fields.Char(string='Ticket Reference', required=True, copy=False, readonly=True,
                       state={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    date_ticket = fields.Date(string='Date', required=True)
    description_ticket = fields.Html(string='Description')
    first_ticket = fields.Char(string='First Ticket', required=True,)
    last_ticket = fields.Char(string='Last Ticket', required=True, )
    number_of_ticket = fields.Float(string='Number OF Tickets', compute='_compute_count_ticket', digits=(32, 0))
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('done', 'Generate Tickets')], string='State',
                             default="draft", store=True, readonly=True ,tracking=True)
    ticket_ids = fields.One2many('tickets.tickets', 'ticket_store')

    @api.depends('ticket_ids')
    def _compute_count_ticket(self):
        obj = self.env['tickets.tickets']
        for tic in self:
            tic.number_of_ticket = obj.search_count([('ticket_store', '=', tic.id)])

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            date_ticket = None
            if 'date_ticket' in vals:
                date_ticket = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_ticket']))
            vals['name'] = self.env['ir.sequence'].next_by_code('tickets.store', sequence_date=date_ticket) or _('New')
            result = super(TicketsStore, self).create(vals)
        return result

    def create_ticket(self):
        result = []
        for ticket in range(int(self.first_ticket), int(self.last_ticket)):
            result.append((0, 0, {'ticket': str(int(ticket)).zfill(4), 'date_ticket': self.date_ticket,
                                  'ticket_store': self.id}))
        self.ticket_ids = result
        self.state = 'done'

    def action_confirm(self):
        self.state = 'confirm'

    def unlink(self):
        for re in self:
            if re.state in ['confirm', 'done']:
                raise UserError(
                    _('You can not delete Ticket Store in Confirm or Done states.'))
        return super(TicketsStore, self).unlink()


class TicketsTickets(models.Model):
    _name = 'tickets.tickets'
    _description = 'TicketTickets'
    _inherit = ['portal.mixin', 'mail.thread.cc', 'mail.activity.mixin']
    _rec_name = 'ticket'

    ticket = fields.Char(string='Ticket', readonly=True)
    purchase_id = fields.Many2one('purchase.order', string="Purchase",
                                  domain="")
    sale_id = fields.Many2one('sale.order', string="Sale")
    bill_id = fields.Many2one('account.move', string="Bill", readonly=True)
    invoice_id = fields.Many2one('account.move', string="Invoice", readonly=True)
    ticket_store = fields.Many2one('tickets.store', string="Ticket Store")
    from_ticket = fields.Many2one('res.country.state', string="From")
    to_ticket = fields.Many2one('res.country.state', string="To")
    date_ticket = fields.Datetime(string='Date OF Ticket')
    is_purchase = fields.Boolean(string="Is Purchase", compute='_compute_is_purchase', store=True)
    is_sale = fields.Boolean(string="Is Sale", compute='_compute_is_sale', store=True)

    @api.depends('purchase_id')
    def _compute_is_purchase(self):
        if self.purchase_id:
            self.is_purchase = True
        else:
            self.is_purchase = False

    @api.depends('sale_id')
    def _compute_is_sale(self):
        if self.sale_id:
            self.is_sale = True
        else:
            self.is_sale = False

    @api.onchange('purchase_id')
    def onchange_purchase(self):
        if self:
            for rec in self:
                if len(rec.ids) > 0:
                    purchase = self.env['purchase.order'].search([('ticket_id', '=', rec.ids[0])])
                    for record in purchase:
                        record.ticket_id = False
                        record.is_ticket = False
                        rec.bill_id = False
                    rec.purchase_id.ticket_id = rec.ids[0]
                    rec.purchase_id.is_ticket = True
                    rec.bill_id= rec.bill_id.invoice_ids.ids[0] if rec.bill_id.invoice_ids.ids else False 

    @api.onchange('sale_id')
    def onchange_sale(self):
        if self.ids:
            for rec in self:
                if len(rec.ids) > 0:
                    sale = self.env['sale.order'].search([('ticket_id', '=', rec.ids[0])])
                    for record in sale:
                        record.ticket_id = False
                        record.is_ticket = False
                        rec.invoice_id = False
                    rec.sale_id.ticket_id = rec.ids[0]
                    rec.sale_id.is_ticket = True
                    rec.invoice_id=rec.sale_id.invoice_ids.ids[0] if rec.sale_id.invoice_ids.ids else False 

