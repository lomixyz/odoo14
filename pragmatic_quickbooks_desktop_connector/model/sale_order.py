from odoo import api, fields, models, _
import requests
import ast
import json
from datetime import datetime, timedelta
import time
from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qbd_tax_code = fields.Many2one('qbd.tax.code')

    @api.onchange('product_id')
    def product_id_change(self):

        vals = {}

        #SAMPLE CODE FOR OVERIDE
        result = super(SaleOrderLine, self).product_id_change()

        if self.tax_id:
            self.qbd_tax_code = self.tax_id[0].qbd_tax_code
        self.update(vals)
        return result

    # def _prepare_invoice_line(self, qty):
    #     res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        def _prepare_invoice_line(self):
            res = super(SaleOrderLine, self)._prepare_invoice_line()

        if self.qbd_tax_code:
            res['qbd_tax_code'] = self.qbd_tax_code.id
        return res

    @api.onchange('product_id', 'price_unit', 'product_uom', 'product_uom_qty', 'tax_id')
    def _onchange_discount(self):
        super(SaleOrderLine, self)._onchange_discount()

        if self.tax_id:
            self.qbd_tax_code = self.tax_id[0].qbd_tax_code

    def _compute_tax_id(self):
        for line in self:
            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
            line.tax_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_shipping_id) if fpos else taxes
            line.qbd_tax_code = line.tax_id.qbd_tax_code.id
            # print (" ----------------------------------------------------- ",line.tax_id)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    quickbooks_id = fields.Char("Quickbook id ", copy=False)
    qbd_sale_order_no = fields.Char('QBD SO No.', copy=False)
    qbd_memo = fields.Text('QBD Memo')
    is_updated = fields.Boolean('Is Updated')

    def write(self, vals):
        # print("\n\n in create of sale order", vals)
        if 'is_updated' not in vals and 'quickbooks_id' not in vals and 'state' not in vals and 'date_order' not in vals and 'procurement_group_id' not in vals:
            vals['is_updated'] = True

        return super(SaleOrder, self).write(vals)

    def create_sale_orders(self,sale_orders):
        # print('\nSale order data : \n\n',sale_orders)
        # print('\n\nTotal sale orders : ',len(sale_orders),'\n\n')
        company = self.env['res.users'].search([('id', '=', 2)]).company_id

        for order in sale_orders:
            vals = {}
            if 'quickbooks_id' in order and order.get('quickbooks_id'):
                sale_order_id = self.search([('quickbooks_id','=',order.get('quickbooks_id'))],limit=1)

                if not sale_order_id:
                    #create new SO
                    # print('\nCreate New Sale Order')
                    # print('Order dict : ',order,'\n')
                    vals = self._prepare_sale_order_dict(order)

                    if vals:
                        new_sale_order_id = self.create(vals)

                        if 'order_lines' in order and order.get('order_lines'):
                            order_lines = order.get('order_lines')
                            so_line_id_list = self.create_sale_order_lines(order_lines,new_sale_order_id)

                            if new_sale_order_id and so_line_id_list:
                                self.env.cr.commit()

                                # print('New Sale Order Commited :: ', new_sale_order_id.name)

                                company.write({
                                    'last_imported_qbd_id_for_sale_orders': order.get("last_time_modified")
                                })


                        if 'state' in  order and order.get('state'):
                            if order.get('state') == 'sale':
                                new_sale_order_id.action_confirm()

                                if not new_sale_order_id.order_line:
                                    new_sale_order_id.action_cancel()

                                if 'date_order' in order and order.get('date_order'):
                                    new_sale_order_id.write({'date_order': order.get('date_order')})

                if sale_order_id:
                    vals = self._prepare_sale_order_dict(order)
                    sale_order_id.write(vals)
                    # print('\n\nUpdate existing Sale Order')
                    #update order
                    #create new line if new product in order
                    if 'order_lines' in order and order.get('order_lines'):
                        self.update_order_lines(order.get('order_lines'),sale_order_id)



        return True

    def _prepare_sale_order_dict(self,order):

        vals = {}

        if order:
            vals.update({
                'quickbooks_id': order.get('quickbooks_id') if order.get('quickbooks_id') else '',
                'date_order': order.get('date_order') if order.get('date_order') else '',
                'qbd_sale_order_no': order.get('qbd_sale_order_number') if order.get('qbd_sale_order_number') else '',
                'qbd_memo': order.get('qbd_memo') if order.get('qbd_memo') else '',
            })

            if 'partner_name' in order and order.get('partner_name'):
                partner_id = self.env['res.partner'].search([('quickbooks_id','=',order.get('partner_name'))],limit=1)

                if partner_id:
                    vals.update({'partner_id':partner_id.id})
                else:
                    raise Warning('Partner is not present in Odoo')
                    # raise Warning('Partner is not correctly set for Sale Order {}'%(order.get('quickbooks_id')))


        if vals:
            return vals

    def create_sale_order_lines(self,order_lines,order_id):
        so_line_id_list = []

        if order_lines:
            for line in order_lines:
                vals = {}

                if order_id:
                    vals.update({'order_id': order_id.id})

                if 'product_name' in line and line.get('product_name'):
                    product_id = self.env['product.product'].search([('quickbooks_id','=',line.get('product_name'))])

                    if 'tax_code' in line and line.get('tax_code'):
                        tax_code = self.env['qbd.tax.code'].search([('name', '=', line.get('tax_code'))])
                        if tax_code:
                            vals.update({
                                'qbd_tax_code': tax_code.id
                            })

                        if tax_code.is_taxable:
                            tax_id = self.env['account.tax'].search([('quickbooks_id', '=', line.get('tax_qbd_id'))])
                            vals.update({
                                'tax_id': [(6, 0, [tax_id.id])]
                            })

                        else:
                            vals.update({
                                'tax_id': [(6, 0, [])]
                            })

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
                    'product_uom_qty': float(line.get('product_uom_qty')) if line.get('product_uom_qty') else 0.00,
                    'name': line.get('name') if line.get('name') else '',
                    'qty_invoiced': line.get('qty_invoiced') if line.get('qty_invoiced') else 0.00,
                })


                if vals:
                    so_line_id = self.env['sale.order.line'].create(vals)
                    if so_line_id:
                        so_line_id_list.append(so_line_id)

        if so_line_id_list:
            return so_line_id_list

    def update_order_lines(self,order_lines_data,order_id):
        so_line_id = None
        product_qbd_id_list = []
        if order_id:
            for so_line in order_id.order_line:
                product_qbd_id_list.append(so_line.product_id.quickbooks_id)
            for line in order_lines_data:
                if line.get('product_name') not in product_qbd_id_list :
                    # print('If product not found in line so create new product')
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
                        'product_uom_qty': float(line.get('product_uom_qty')) if line.get('product_uom_qty') else 0.00,
                        'name': line.get('name') if line.get('name') else '',
                        'qty_invoiced': line.get('qty_invoiced') if line.get('qty_invoiced') else 0.00,
                    })

                    if vals:
                        so_line_id = self.env['sale.order.line'].create(vals)

        if so_line_id:
            return True


    def export_sale_orders(self):
        # print('\n\nExport Sale Orders Calleeedd !!!!\n\n')
        order_data_list = []
        loger_dict={}

        company = self.env['res.users'].search([('id', '=', 2)]).company_id

        company.env['qbd.orderinvoice.logger'].search([]).unlink()
        company.check_tax_code_for_order_invoices()

        if not company.qb_default_tax:
            raise Warning('Set Default Tax in Comapny -> QBD Account and Taxes Configuration -> Default Tax')

        if company.export_so_limit:
            limit = int(company.export_so_limit)
        else:
            limit = 0

        if company.export_sales_order_date:
            export_date = company.export_sales_order_date
        else:
            export_date = False

        self.env.cr.execute("SELECT odoo_id FROM qbd_orderinvoice_logger WHERE type='sale'")
        result = self.env.cr.fetchall()
        so_data_list = []
        for rec in result:
            # print ("Rec ---------------------------- ",rec[0])
            so_data_list.append(int(rec[0]))
        # print (so_data_list)

        filters = [('id', 'not in', so_data_list), ('state', 'in', ['sale','done'])]

        if export_date:
            # print("Before ------------------------------ ", type(export_date), export_date)
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

        orders = self.search(filters, limit=limit)


        # print('Orders ::: ',orders)

        if orders:
            for order in orders:
                order_dict = {}
                if company.export_updated_record:
                    order_dict = self.get_order_dict(order,company.export_updated_record)
                else:
                    order_dict = self.get_order_dict(order)

                if order_dict:
                    order_data_list.append(order_dict)

        if order_data_list:
            # print('\n\nOrders data : ',order_data_list)
            # print('\nTotal Orders : ',len(order_data_list))

            company = self.env['res.users'].search([('id', '=', 2)]).company_id
            headers = {'content-type': "application/json"}
            data = order_data_list

            data = {'sale_orders_list': data}

            response = requests.request('POST', company.url + '/export_sale_orders', data=json.dumps(data),
                                        headers=headers,
                                        verify=False)

#             print("Response Text", type(response.text), response.text)

            resp = ast.literal_eval(response.text)

            # print('Resp : ', resp)
            if company.export_updated_record == False:
                for res in resp[0].get('Data'):
                    if 'odoo_id' in res and res.get('odoo_id'):
                        so_id = self.browse(int(res.get('odoo_id')))
                        if so_id:
                            so_id.write({
                                'quickbooks_id': res.get('quickbooks_id'),
                                'qbd_sale_order_no': res.get('qbd_sale_order_no') if res.get('qbd_sale_order_no') else '',
                            })
                    loger_dict.update({'operation': 'Export Partner',
                                       'odoo_id': res.get('odoo_id'),
                                       'qbd_id': res.get('quickbooks_id'),
                                       'message': res.get('messgae')
                                       })
                    qbd_loger_id = self.env['qbd.loger'].create(loger_dict)
                    # company.write({'qbd_loger_id': [(4, qbd_loger_id.id)]})
                    # print("\n\n\n\nDatetime", res.get('last_modified_date'))
                    company.write({
                        'export_sales_order_date': res.get('last_modified_date')
                    })
            else:
                for res in resp[0].get('Data'):
                    if 'odoo_id' in res and res.get('odoo_id'):
                        so_id = self.browse(int(res.get('odoo_id')))
                        if so_id:
                            so_id.write({'is_updated': False})
                    loger_dict.update({'operation': 'Export Partner',
                                       'odoo_id': res.get('odoo_id'),
                                       'qbd_id': res.get('quickbooks_id'),
                                       'message': res.get('messgae')
                                       })
                    qbd_loger_id = self.env['qbd.loger'].create(loger_dict)
                    # company.write({'qbd_loger_id': [(4, qbd_loger_id.id)]})
                    print("\n\n\n\nDatetime",res.get('last_modified_date'))
                    company.write({
                        'export_sales_order_date': res.get('last_modified_date')
                    })

        return True


    def get_order_dict(self,order,export_updated_record=False):
        order_dict = {}

        company = self.env['res.users'].search([('id', '=', 2)]).company_id
        default_tax_on_order = company.qb_default_tax.name

        if export_updated_record:
            order_dict.update({
                'sale_order_qbd_id':order.quickbooks_id,
            })
        else:
            order_dict.update({
                'sale_order_qbd_id': '',
            })

        order_dict['odoo_order_number'] = order.name if len(order.name)<11 else order.id
        order_dict['default_tax_on_order'] = default_tax_on_order

        order_dict.update({
            'odoo_id': order.id,
            'qbd_memo': order.name,
            'partner_name': order.partner_id.quickbooks_id,
            'confirmation_date': order.date_order.strftime('%Y-%m-%d'),
        })

        if order.order_line:
            order_dict.update({
                'order_lines': self.get_order_lines(order)
            })

        if order_dict:
            return order_dict


    def get_order_lines(self,order):
        order_lines= []


        for line in order.order_line:
            line_dict = {}

            description = line.name if line.name else ''
            bad_chars = [';', ':', '!', "*", "$", "'"]
            for i in bad_chars:
                description = description.replace(i, "")

            if line.product_id:
                line_dict.update({
                    'product_name': line.product_id.quickbooks_id if line.product_id else '',
                    'name': description,
                    'product_uom_qty': line.product_uom_qty if line.product_uom_qty else '',
                    'price_unit': line.price_unit if line.price_unit else '',
                    'tax_id': line.tax_id[0].quickbooks_id if line.tax_id else '',
                    'qbd_tax_code': line.qbd_tax_code.name if line.qbd_tax_code.name else '',
                    'price_subtotal': line.price_subtotal if line.price_subtotal else '',
                })

            if line_dict:
                order_lines.append(line_dict)

        if order_lines:
            return order_lines































