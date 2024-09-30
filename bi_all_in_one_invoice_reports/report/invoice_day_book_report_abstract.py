# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, _
from odoo.exceptions import UserError


class InvoiceDayBookReportAbstract(models.AbstractModel):
    _name = 'report.bi_all_in_one_invoice_reports.invoice_book_report'
    _description = 'Sale Day Book Report Abstract'


    def _get_report_values(self, docids, data=None):
        docs = self.env['invoice.day.book.report'].browse(docids)

        data  = { 'start_date': docs.start_date, 'end_date': docs.end_date}

        return {
                   'doc_ids': self.ids,
                   'doc_model': 'invoice.day.book.report',
                   'docs': docs,
                   'data' : data,
                   'get_header' : self._get_header,
                   'get_detail' : self._get_details,
                   'get_data' : self._get_data,
                   'get_ref' : self._get_ref,
                   'get_total' : self._get_total,
                   'get_inv_tot' : self._get_inv_total,
                   'get_total_tax' : self._get_total_tax
                   }

    def _get_header(self):
        head_list = ['DATE','INVOICE NUMBER','ACCOUNT CODE','CUSTOMER','DESCRIPTION','TOTAL']
        prod_cat = self.env['product.category'].search([])
        for a in prod_cat:
            head_list.append(a.name)
        head_list.append('Tax')
        return head_list

    def _get_data(self,obj):

        final_dict = {}
        name = []
        acc_code = []
        tmp_name = ""
        tmp_acc_code = ""
        ref = self._get_ref()

        if obj.amount_total > 0:
          for temp in ref:
              final_dict.update({
                             temp:0
                             })

          if obj.name[0:3] == 'INV':
            final_dict.update({
             'date':obj.invoice_date,
             'number':obj.name or '',
             'customer':obj.partner_id.name,
             'total':obj.amount_total,
             'tax':obj.amount_tax
            })


          for a in obj.invoice_line_ids:
              name.append(a.product_id.default_code) 
              if a.account_id.code not in acc_code:
                  acc_code.append(a.account_id.code)
              for r in ref:
                  if a.product_id.categ_id.name == r:
                      tmp_price = final_dict.get(r) + a.price_subtotal
                      final_dict.update({
                                         r:tmp_price
                                         })
          if len(name) > 0:
            tmp_name = ",".join(str(bit) for bit in name)
          if len(acc_code) > 0:
            tmp_acc_code = ",".join(str(bit) for bit in acc_code)

          final_dict.update({
                         'name':tmp_name or '',
                         'acc_code':tmp_acc_code or '',
                         })
          
          return [final_dict]

    def _get_ref(self):
        head_list = []
        prod_cat = self.env['product.category'].search([])
        for a in prod_cat:
            head_list.append(a.name)
        return head_list

    def _get_details(self, obj):
        start_date = obj['start_date']
        end_date = obj['end_date']
        invoice_ids = self.env['account.move'].search([('invoice_date','>=',start_date),('invoice_date','<=',end_date),('move_type','=','out_invoice'),('state','=','posted')])
        return invoice_ids

    def _get_total(self, obj):
        inv_ids = self._get_details(obj)
        ref = self._get_ref()
        total = {}
        for r in ref:
            total.update({r:0})

        for invoice in inv_ids:
            for line in  invoice.invoice_line_ids:
                tmp_amt = total.get(line.product_id.categ_id.name)
                total_amt = tmp_amt + line.price_subtotal
                total.update({line.product_id.categ_id.name : total_amt})

        return total

    def _get_inv_total(self, obj):
        inv_ids = self._get_details(obj)
        total = 0
        for invoice in inv_ids:
            total += invoice.amount_total
        return total

    def _get_total_tax(self):
      lst = list(ids.id for ids in self.env['invoice.day.book.report'].search([]))
      start_date = self.env['invoice.day.book.report'].browse(max(lst)).start_date
      end_date = self.env['invoice.day.book.report'].browse(max(lst)).end_date
      
      total = 0.0
      invoice_ids = self.env['account.move'].search([('invoice_date','>=',start_date),('invoice_date','<=',end_date),('move_type','=','out_invoice'),('state','=','posted')])
      for ids in invoice_ids:
        result = self._get_data(ids)        
        total += result[0].get('tax',0.0)
      
      return total


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: