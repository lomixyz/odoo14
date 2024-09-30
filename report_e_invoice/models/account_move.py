import qrcode
import base64
from io import BytesIO
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('line_ids.sale_line_ids')
    def _get_sale_orders(self):
        for move in self:
            if move.move_type == 'out_invoice':
                orders = move.line_ids.sale_line_ids.order_id
                move.sale_ids = orders

    @api.depends('line_ids.purchase_line_id')
    def _get_purchase_orders(self):
        for move in self:
            if move.move_type == 'in_invoice':
                orders = move.line_ids.mapped('purchase_line_id.order_id')
                move.purchase_ids = orders

    sale_ids = fields.Many2many("sale.order",
                                string='Invoices', compute="_get_sale_orders",
                                readonly=True,
                                copy=False)

    purchase_ids = fields.Many2many("purchase.order",
                                    string='Invoices', compute="_get_purchase_orders",
                                    readonly=True,
                                    copy=False)

    reversal_reason = fields.Char("Reason")
    qr_image = fields.Binary("QR Code", compute='_generate_qr_code')
    picking_delivery_date = fields.Date("Picking Delivery Date", compute="_compute_picking_delivery_date")

    def _compute_picking_delivery_date(self):
        for move in self:
            move.picking_delivery_date = False
            if move.move_type == 'out_invoice':
                if len(move.sale_ids) > 0 and len(move.sale_ids[-1].picking_ids) > 0:
                    move.picking_delivery_date = move.sale_ids[-1].picking_ids[-1].scheduled_date
            elif move.move_type == 'in_invoice':
                if len(move.purchase_ids) > 0 and len(move.purchase_ids[-1].picking_ids) > 0:
                    move.picking_delivery_date = move.purchase_ids[-1].picking_ids[-1].scheduled_date

    def _generate_qr_code(self):
        if self.move_type in ['out_invoice', 'in_refund']:
            partner_name = self.company_id.partner_id.name
        if self.move_type in ['in_invoice', 'out_refund']:
            partner_name = self.partner_id.name
        partner_name = str(_('اسم المورد: \t \t ' + partner_name))
        if self.move_type in ['out_invoice', 'in_refund']:
            if not self.company_id.partner_id.vat:
                raise UserError(_('Please define the Company Tax ID'))
            else:
                partner_vat = self.company_id.partner_id.vat
        if self.move_type in ['in_invoice', 'out_refund']:
            if not self.partner_id.vat:
                raise UserError(_('Please define the Partner Tax ID'))
            else:
                partner_vat = self.partner_id.vat
        partner_vat = str(_('رقم تسجيل ضريبة: \t \t ' + partner_vat))

        currency_total = ''.join([self.currency_id.name, str(self.amount_total)])
        total = str(_('إجمالي الفاتورة:  \t \t ' + currency_total))
        currency_tax = ''.join([self.currency_id.name, str(self.amount_tax)])
        tax = str(_('إجمالي ضريبة القيمة المضافة:  \t \t ' + currency_tax))
        date_invoice = self.invoice_date.strftime("%Y/%m/%d")
        date = str(_('الطابع الزمني للفاتورة:  \t \t ' + date_invoice))
        lf = '\n\n'
        ibanqr = lf.join([partner_name, partner_vat, date, total, tax])
        self.qr_image = generate_qr_code(ibanqr)


def generate_qr_code(value):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=20,
        border=4,
    )
    qr.add_data(value)
    qr.make(fit=True)
    img = qr.make_image()
    temp = BytesIO()
    img.save(temp, format="PNG")
    qr_img = base64.b64encode(temp.getvalue())
    return qr_img
