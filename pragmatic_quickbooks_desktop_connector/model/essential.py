from odoo import api, fields, models, _
import ast
import json
import requests

class ResPartner_Category_Inherit(models.Model):
    _inherit = "res.partner.category"

    quickbooks_id = fields.Char("Quickbook id ", copy=False)
    tag_type = fields.Selection([('customer', 'Customer'), ('vendor', 'Vendor')], string='Tag Type')

    ### Import Res Partner Categories
    def import_vendor_customer_category(self, partner_category_data, tag_type):
        # print('\n\nPartner Category data : ',partner_category_data)
        # print('\n\nTotal count : ',len(partner_category_data))
        #print("tag_type==============",tag_type)
        if partner_category_data:
            for record in partner_category_data:
                vals = {}

                if 'name' in record and record.get('name'):
                    tags_id = self.search([('name','=',record.get('name'))],limit=1)

                    if not tags_id:
                        vals.update({
                            'name': record.get('name'),
                            'quickbooks_id': record.get('quickbooks_id'),
                            'tag_type': tag_type
                        })

                        if vals:
                            self.create(vals)

                    else:
                        vals.update({
                            'quickbooks_id': record.get('quickbooks_id')
                        })
                        tags_id.write(vals)
        return True

class Parnter_Title(models.Model):
    _inherit = "res.partner.title"

    ### Import Partner Title
    def import_partner_title(self,partner_title_data):
        # print('\n\nPartner Title data : ',partner_title_data)
        # print('\n\nTotal count : ',len(partner_title_data))
        if partner_title_data:
            for record in partner_title_data:
                vals = {}

                if 'name' in record and record.get('name'):
                    partner_title_id = self.search([('name','=',record.get('name'))],limit=1)

                    if not partner_title_id:
                        vals.update({
                            'name': record.get('name'),
                        })

                        if vals:
                            self.create(vals)

        return True

class AccountPaymentTerms(models.Model):
    _inherit = "account.payment.term"

    quickbooks_id = fields.Char("Quickbook id ", copy=False)

    ### Import Payment Terms
    def import_payment_terms(self,payment_term_data):
        # print('\n\nPayment Term data : ',payment_term_data)
        # print('\n\nTotal count : ',len(payment_term_data))

        if payment_term_data:
            for record in payment_term_data:
                vals = {}
                if 'name' in record and record.get('name'):
                    payment_term_id = self.search([('name','=',record.get('name'))],limit=1)

                    if not payment_term_id:
                        vals.update({
                            'name': record.get('name'),
                            'quickbooks_id': record.get('quickbooks_id')
                        })

                        if vals:
                            self.create(vals)

                    else:
                        vals.update({
                            'quickbooks_id': record.get('quickbooks_id')
                        })
                        payment_term_id.write(vals)
        return True

    # @api.multi
    # def export_payment_terms(self):
    #     print('Export QBD Payment Terms hereeeeeeeeeeeeeeeeeeeeee')
    #     payment_term_data = []
    #     qbd_payment_terms = self.search([('quickbooks_id','=',None)])
    #
    #     if qbd_payment_terms:
    #         for record in qbd_payment_terms:
    #             payment_term_dict= {}
    #             payment_term_dict.update({
    #                 'odoo_id':record.id,
    #                 'name':record.name
    #             })
    #
    #             if payment_term_dict:
    #                 payment_term_data.append(payment_term_dict)
    #
    #     if payment_term_data:
    #         print('\nPayment Term data : ',payment_term_data)
    #         print('Total Count ',len(payment_term_data))
    #         company = self.env['res.users'].search([('id', '=', 2)]).company_id
    #         headers = {'content-type': "application/json"}
    #         data = payment_term_data
    #
    #         data = {'payment_term_list': data}
    #
    #         response = requests.request('POST', company.url + '/export_payment_terms', data=json.dumps(data),
    #                                     headers=headers,
    #                                     verify=False)
    #
    #         print("Response Text ", type(response.text), response.text)
    #
    #         resp = ast.literal_eval(response.text)
    #
    #         print('\n\nResp: ', resp,'\n\n')
    #
    #         for res in resp[0].get('Data'):
    #
    #             if 'odoo_id' in res and res.get('odoo_id'):
    #                 payment_term_id = self.browse(int(res.get('odoo_id')))
    #
    #                 if payment_term_id:
    #                     payment_term_id.write({'quickbooks_id': res.get('quickbooks_id')})
    #
    #     return True

class AccountTaxes(models.Model):
    _inherit = "account.tax"

    quickbooks_id = fields.Char("Quickbook id", copy=False)
    qbd_tax_code = fields.Many2one('qbd.tax.code')
    desc = fields.Char("Description")

    ### Import Sales Tax
    def import_sales_tax(self,item_tax_data):
        # print('\n\nItem Tax data : ',item_tax_data)
        # print('\n\nTotal count : ',len(item_tax_data))
        if item_tax_data:
            for record in item_tax_data:
                vals = {}

                if 'name' in record and record.get('name'):
                    tax_id = self.search(['&', ('name','=',record.get('name')), ('amount','=',record.get('amount'))],limit=1)

                    if not tax_id:
                        vals.update({
                            'name': record.get('name'),
                            'desc': record.get('desc'),
                            'amount': record.get('amount'),
                            'quickbooks_id': record.get('quickbooks_id'),
                        })

                        if vals:
                            self.create(vals)

                    else:
                        # print ("In Write -------------------------------------------- Tax ID")
                        vals.update({
                            'quickbooks_id': record.get('quickbooks_id'),
                        })
                        tax_id.write(vals)

        return True

class QBDTaxCode(models.Model):
    _name = "qbd.tax.code"
    _description = "QBD Tax Code"

    name = fields.Char('Name')
    is_taxable = fields.Boolean('Is Taxable',)
    quickbooks_id = fields.Char("Quickbook id", copy=False)

    ### Import Tax Code
    def import_tax_code(self,item_tax_code_data):
        # print('\n\nItem Tax Code : ',item_tax_code_data)
        # print('\n\nTotal count : ',len(item_tax_code_data))
        if item_tax_code_data:
            for record in item_tax_code_data:
                vals = {}

                if 'name' in record and record.get('name'):
                    tax_code_id = self.search([('name','=',record.get('name'))],limit=1)


                    if not tax_code_id:
                        vals.update({
                            'name': record.get('name'),
                            'is_taxable': record.get('taxable'),
                            'quickbooks_id': record.get('quickbooks_id'),
                        })

                        if vals:
                            self.create(vals)

                    else:
                        # print ("In Write -------------------------------------------- Tax Code")
                        vals.update({
                            'quickbooks_id': record.get('quickbooks_id'),
                        })
                        tax_code_id.write(vals)
        return True