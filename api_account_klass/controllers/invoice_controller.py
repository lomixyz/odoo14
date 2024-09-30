# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request, Response
import json


class InvoiceController(http.Controller):

    @http.route('/api/invoices', type='http', auth='none', methods=['GET'], csrf=False)
    def get_invoices(self, **kwargs):
        # Get the API key from the request headers
        api_key = request.httprequest.headers.get('X-Api-Key')
        
        # Validate API key (replace 'your_secret_api_key' with your actual key)
        if api_key != 'KROJER!@!123KROJER':
            return Response(
                json.dumps({'error': 'Unauthorized'}),
                content_type='application/json',
                status=401
            )

        # Search for sale invoices
        invoices = request.env['account.move'].sudo().search([('company_id', '=', 5), ('move_type', '=', 'out_invoice')])

        # Prepare the response data
        invoice_data = []
        for invoice in invoices:
            # Fetch the invoice lines
            # invoice_lines = request.env['account.move.line'].sudo().search([('move_id', '=', invoice.id)])
            
            # Prepare invoice lines data
            lines_data = []
            for line in invoice.invoice_line_ids:
                lines_data.append({
                    'product_id': line.product_id.read(['name']),
                    'quantity': line.quantity,
                    'price_unit': line.price_unit,
                    'price_subtotal': line.price_subtotal,
                    'price_total': line.price_total,
                    # 'account_id': line.account_id.name if line.account_id else 'N/A',
                })

            # Add invoice and lines data
            invoice_data.append({
                'id': invoice.id,
                'name': invoice.name,
                'invoice_date': str(invoice.invoice_date),
                'amount_total': invoice.amount_total,
                'state': invoice.state,
                'partner_id': invoice.partner_id.read(['name']),
                # 'partner_name': invoice.partner_id.name,
                'lines': lines_data
            })

        # Return the data as JSON
        return Response(json.dumps(invoice_data), content_type='application/json', status=200)
