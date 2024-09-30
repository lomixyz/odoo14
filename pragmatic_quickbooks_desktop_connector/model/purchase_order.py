from odoo import api, fields, models, _
import requests
import ast
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError

import logging
from datetime import datetime
import json
_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    quickbooks_id = fields.Char("Quickbook id ", copy=False)
    qbd_purchase_order_no = fields.Char('QBD PO No.', copy=False)
    qbd_memo = fields.Text('QBD Memo')
    is_updated = fields.Boolean('Is Updated')

    def write(self, vals):

        if 'is_updated' not in vals and 'quickbooks_id' not in vals:
            vals['is_updated'] = True

        return super(PurchaseOrder, self).write(vals)

    def create_purchase_orders(self, purchase_orders):

#         print('\npurchase_orders order data : \n\n', purchase_orders)
#         print('\n\nTotal purchase_orders orders : ', len(purchase_orders), '\n\n')
        company = self.env['res.users'].search([('id', '=', 2)]).company_id

        for order in purchase_orders:
            vals = {}
            if 'quickbooks_id' in order and order.get('quickbooks_id'):
                purchase_order_id = self.search([('quickbooks_id', '=', order.get('quickbooks_id'))], limit=1)

                if not purchase_order_id:
                    # create new PO
#                     print('\nCreate New Purchase Order')
#                     print('Order dict : ', order, '\n')

                    vals = self._prepare_purchase_order_dict(order)

#                     print('\nValssssssss: ', vals)

                    if vals:
                        new_purchase_order_id = self.create(vals)

                        if 'purchase_order_lines' in order and order.get('purchase_order_lines'):
                            order_lines = order.get('purchase_order_lines')
                            po_line_id = self.create_purchase_order_lines(order_lines, new_purchase_order_id)

                        new_purchase_order_id.write({'state':'draft'})

                        if new_purchase_order_id:
                            self.env.cr.commit()
#                             print('New Purchase Order Commited :: ', new_purchase_order_id.name)
                            company.write({
                                'last_imported_qbd_id_for_purchase_orders': order.get("last_time_modified")
                            })

                        # if 'state' in order and order.get('state'):
                        #     if order.get('state') == 'draft':
                        #         new_purchase_order_id.write({'state': 'sale'})
                        #
                        #         if 'confirmation_date' in order and order.get('confirmation_date'):
                        #             new_purchase_order_id.write({'confirmation_date': order.get('confirmation_date')})

                if purchase_order_id:
#                     print('\n\nUpdate existing Purchase Order')
                    # update order
                    vals = self._prepare_purchase_order_dict(order)
                    purchase_order_id.write(vals)
                    # create new line if new product in order
                    if 'purchase_order_lines' in order and order.get('purchase_order_lines'):
                        self.update_order_lines(order.get('purchase_order_lines'), purchase_order_id)

        return True

    def _prepare_purchase_order_dict(self, order):

        vals = {}

        if order:
            vals.update({
                'quickbooks_id': order.get('quickbooks_id') if order.get('quickbooks_id') else False,
                'date_order': order.get('date_order') if order.get('date_order') else '',
                'qbd_purchase_order_no': order.get('qbd_purchase_order_number') if order.get('qbd_purchase_order_number') else '',
                'qbd_memo': order.get('qbd_memo') if order.get('qbd_memo') else '',

            })

            if 'partner_name' in order and order.get('partner_name'):
                partner_id = self.env['res.partner'].search([('quickbooks_id', '=', order.get('partner_name')),('supplier_rank','=',1)],
                                                            limit=1)

                if partner_id:
                    vals.update({'partner_id': partner_id.id})
                else:
                    raise Warning('Vendor is not correctly set for Purchase Order {}' % (order.get('quickbooks_id')))

        if vals:
            return vals

    def create_purchase_order_lines(self, order_lines, order_id):
        po_line_id_list = []

        if order_lines:
            for line in order_lines:
                vals = {}

                if order_id:
                    vals.update({'order_id': order_id.id})

                if 'product_name' in line and line.get('product_name'):
                    product_id = self.env['product.product'].search([('quickbooks_id', '=', line.get('product_name'))])

                    if product_id:
                        vals.update({
                            'product_id': product_id.id
                        })
                    else:
                        raise Warning('Product Not found for QBD id :'+line.get('product_name'))

                else:
                    continue

                vals.update({
                    'price_unit': float(line.get('price_unit')) if line.get('price_unit') else 0.00,
                    'product_qty': float(line.get('product_qty')) if line.get('product_qty') else 1,
                    'name': line.get('name') if line.get('name') else '',
                    'qty_invoiced': line.get('qty_invoiced') if line.get('qty_invoiced') else 0.00,
                    'date_planned': line.get('date_planned') if line.get('date_planned') else datetime.today(),
                    'product_uom':1,
                })

                if vals:
                    po_line_id = self.env['purchase.order.line'].create(vals)
                    if po_line_id:
                        po_line_id_list.append(po_line_id)

        if po_line_id_list:
            return po_line_id_list

    def update_order_lines(self,order_lines_data,order_id):
#         print(' !! In Update method !!!!',order_id.name)
        po_line_id = None
        product_qbd_id_list = []
        if order_id:
            for po_line in order_id.order_line:
                product_qbd_id_list.append(po_line.product_id.quickbooks_id)
            for line in order_lines_data:
                if line.get('product_name') not in product_qbd_id_list :
#                     print('If product not found in line so create new product')
                    vals = {}

                    vals.update({'order_id': order_id.id})

                    if 'product_name' in line and line.get('product_name'):
                        product_id = self.env['product.product'].search(
                            [('quickbooks_id', '=', line.get('product_name'))])

                        if product_id:
                            vals.update({
                                'product_id': product_id.id
                            })
                        else:
                            continue
                    else:
                        continue

                    vals.update({
                        'price_unit': float(line.get('price_unit')) if line.get('price_unit') else 0.00,
                        'product_qty': float(line.get('product_qty')) if line.get('product_qty') else 1,
                        'name': line.get('name') if line.get('name') else '',
                        'qty_invoiced': line.get('qty_invoiced') if line.get('qty_invoiced') else 0.00,
                        'date_planned': line.get('date_planned') if line.get('date_planned') else datetime.today(),
                        'product_uom': 1,
                    })

                    if vals:
                        po_line_id = self.env['purchase.order.line'].create(vals)

        if po_line_id:
            return True


    def export_purchase_order(self):
#         print('Export Purchase Ordr !!!!!')
        loger_dict={}
        company = self.env['res.users'].search([('id', '=', 2)]).company_id

        po_order_data_list = []

        if company.export_po_limit:
            limit = int(company.export_po_limit)
        else:
            limit = 0

        if company.export_purchase_order_date:
            export_date = company.export_purchase_order_date
        else:
            export_date = False

        filters = [('state', 'in', ['purchase','done'])]

        if export_date:
            # print ("Before ------------------------------ ", type(export_date), export_date)
            export_date_start = datetime(export_date.year, export_date.month, export_date.day)
            # print ("After ------------------------------ ",type(export_date), export_date_start)
            export_date_end = export_date_start + timedelta(hours=23, minutes=59, seconds=59)
            # print ("After ------------------------------ ",type(export_date), export_date_end)

            filters.append(('date_order', '>=', export_date_start.strftime("%Y-%m-%d %H:%M:%S")))
            filters.append(('date_order', '<=', export_date_end.strftime("%Y-%m-%d %H:%M:%S")))

        if company.export_updated_record:
            filters.append(('quickbooks_id', '!=', False))
            filters.append(('is_updated', '=', True))
        else:
            filters.append(('quickbooks_id', '=', False))

        po_orders = self.search(filters, limit=limit)

        # print('PO Orders ::: ', po_orders)

        if po_orders:
            for order in po_orders:
                order_dict = {}
                if company.export_updated_record:
                    order_dict = self.get_order_dict(order,company.export_updated_record)
                else:
                    order_dict = self.get_order_dict(order)


                if order_dict:
                    po_order_data_list.append(order_dict)

        if po_order_data_list:
            # print('\n\n  PO Orders data : ', po_order_data_list)
            # print('\nTotal Orders : ', len(po_order_data_list))

            company = self.env['res.users'].search([('id', '=', 2)]).company_id
            headers = {'content-type': "application/json"}
            data = po_order_data_list

            data = {'purchase_orders_list': data}

            response = requests.request('POST', company.url + '/export_purchase_orders', data=json.dumps(data),
                                        headers=headers,
                                        verify=False)

            # print("Response Text", type(response.text), response.text)

            resp = ast.literal_eval(response.text)

            # print('Resp : ', resp)
            if company.export_updated_record == False:
                for res in resp[0].get('Data'):
                    if 'odoo_id' in res and res.get('odoo_id'):
                        so_id = self.browse(int(res.get('odoo_id')))
                        if so_id:
                            so_id.write({
                                'quickbooks_id': res.get('quickbooks_id'),
                                'qbd_purchase_order_no': res.get('qbd_purchase_order_no') if res.get('qbd_purchase_order_no') else '',
                            })
                    loger_dict.update({'operation': 'Export Purchase Order',
                                       'odoo_id': res.get('odoo_id'),
                                       'qbd_id': res.get('quickbooks_id'),
                                       'message': res.get('messgae')
                                       })
                    qbd_loger_id = self.env['qbd.loger'].create(loger_dict)
                    # company.write({'qbd_loger_id': [(4, qbd_loger_id.id)]})
                    company.write({
                        'export_purchase_order_date': res.get('last_modified_date')
                    })
            else:
                for res in resp[0].get('Data'):
                    if 'odoo_id' in res and res.get('odoo_id'):
                        so_id = self.browse(int(res.get('odoo_id')))
                        if so_id:
                            so_id.write({
                                'is_updated':False
                            })
                    loger_dict.update({'operation': 'Export Purchase Order',
                                       'odoo_id': res.get('odoo_id'),
                                       'qbd_id': res.get('quickbooks_id'),
                                       'message': res.get('messgae')
                                       })
                    qbd_loger_id = self.env['qbd.loger'].create(loger_dict)
                    # company.write({'qbd_loger_id': [(4, qbd_loger_id.id)]})

        return True

    def get_order_dict(self,order,export_updated_record=False):
        order_dict = {}

        if export_updated_record:
            order_dict.update({
                'qbd_purchase_order_id':order.quickbooks_id
            })
        else:
            order_dict.update({
                'qbd_purchase_order_id': '',
            })

        order_dict['odoo_purchase_order_number'] = order.name if len(order.name) < 11 else order.id

        order_dict.update({
            'odoo_id': order.id,
            'qbd_memo': order.name,
            'partner_name': order.partner_id.quickbooks_id,
            'date_order': order.date_order.strftime('%Y-%m-%d'),
        })

        if order.order_line:
            order_dict.update({
                'order_lines': self.get_order_lines(order)
            })

        if order_dict:
            return order_dict

    def get_order_lines(self, order):
        order_lines = []

        for line in order.order_line:
            line_dict = {}

            description = line.name if line.name else ''
            bad_chars = [';', ':', '!', "*", "$", "'"]
            for i in bad_chars:
                description = description.replace(i, "")

            line_dict.update({
                'product_name': line.product_id.quickbooks_id if line.product_id else '',
                'name': description,
                'product_qty': line.product_qty if line.product_qty else '',
                'price_unit': line.price_unit if line.price_unit else '',
                # 'tax_id': line.tax_id if line.tax_id else '',
                'price_subtotal': line.price_subtotal if line.price_subtotal else '',
            })

            if line_dict:
                order_lines.append(line_dict)

        if order_lines:
            return order_lines


