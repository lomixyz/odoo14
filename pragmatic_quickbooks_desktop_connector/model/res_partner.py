from odoo import api, fields, models, _
import requests
import ast
import json
import logging
import re
from odoo.exceptions import UserError, ValidationError, Warning

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    quickbooks_id = fields.Char("Quickbook id ", copy=False)
    is_updated = fields.Boolean('Is Updated')
    qbd_date_created = fields.Date()
    
#     @api.model
#     def default_get(self, fields):
#         
#         vals = super(ResPartner, self).default_get(fields)
#         if 'res_partner_search_mode' in self._context and self._context['res_partner_search_mode'] == 'customer':
#             category_ids = self.env['res.partner.category'].search([('tag_type', '=', 'customer')])
#             if category_ids:
#                 vals['category_id'] = [(6, 0, category_ids.ids)]
#         if 'res_partner_search_mode' in self._context and self._context['res_partner_search_mode'] == 'supplier' :
#             category_ids = self.env['res.partner.category'].search([('tag_type', '=', 'customer')])
#             print("\n\ncategory_ids==============",category_ids)
#             if category_ids:
#                 vals['category_id'] = [(6, 0, category_ids.ids)]
# 
#         return vals
    
    @api.onchange('category_id')
    def item_delivered_ids_onchange(self):
        cat_list = []
        if 'res_partner_search_mode' in self._context and self._context['res_partner_search_mode'] == 'customer':
            category_ids = self.env['res.partner.category'].search([('tag_type', '=', 'customer')])
            if category_ids:
                for category_id in category_ids :
                    cat_list.append(category_id.id)
                    
        if 'res_partner_search_mode' in self._context and self._context['res_partner_search_mode'] == 'supplier':
            category_ids = self.env['res.partner.category'].search([('tag_type', '=', 'vendor')])
            if category_ids:
                for category_id in category_ids :
                    cat_list.append(category_id.id)
                    
        return {'domain': {'category_id': [('id', 'in', cat_list)]}}


    @api.model
    def create(self, vals):
        try:
            if 'vat' in vals:
                if vals['vat']:
                    if vals['customer_rank']:
                        if len(vals['vat'])>15:
                            raise Warning ("Tax ID should be not more than 15 characters for Customers.")
                    elif vals['supplier_rank']:
                        data = vals['vat']
                        match = re.search("^[0-9]{3}-[0-9]{2}-[0-9]{4}$|^[0-9]{2}-[0-9]{7}$", data)
                        if not match:
                            raise Warning("Tax ID should be exactly of 10 characters in form of 12-3456789 or 123-45-6789 for Vendors, and only Integer format is supported in Quickbooks.")

            partner_id = super(ResPartner, self).create(vals)
            return partner_id

        except Exception as e:
            pass

    def write(self_vals, vals):
        for self in self_vals:
            if 'vat' in vals:
                if vals['vat']:
                    if 'customer_rank' not in vals and 'supplier_rank' not in vals:
                        if self.customer_rank:
                                if len(vals['vat']) > 15:
                                    raise Warning("Tax ID should be not more than 15 characters for Customers.")

                        elif self.supplier_rank:
                            data = vals['vat']
                            match = re.search("^[0-9]{3}-[0-9]{2}-[0-9]{4}$|^[0-9]{2}-[0-9]{4}$", data)
                            if not match:
                                raise Warning("Tax ID should be exactly of 10 characters in form of 12-3456789 or 123-45-6789 for Vendors, and only Integer format is supported in Quickbooks.")

                    if 'customer_rank' in vals and 'supplier_rank' in vals:
                        if vals['customer_rank']:
                            if len(vals['vat']) > 15:
                                raise Warning("Tax ID should be not more than 15 characters for Customers.")

                        if vals['supplier_rank']:
                            if len(vals['vat']) > 15:
                                data = vals['vat']
                                match = re.search("^[0-9]{3}-[0-9]{2}-[0-9]{4}$|^[0-9]{2}-[0-9]{4}$", data)
                                if not match:
                                    raise Warning("Tax ID should be exactly of 10 characters in form of 12-3456789 or 123-45-6789 for Vendors, and only Integer format is supported in Quickbooks.")

            if 'is_updated' not in vals and 'quickbooks_id' not in vals and 'is_company' not in vals:
                # print("\n\nin write of partner", self._context.get('dont_update_is_update'), vals)
                vals['is_updated'] = True

            return super(ResPartner, self).write(vals)

    def create_customers(self,partners):
        # print('\n\nTotal Partners : ',len(partners),'\n\n')
        company = self.env['res.users'].search([('id', '=', 2)]).company_id

        for partner in partners:
            vals = {}
            if partner.get('is_active'):
                if 'quickbooks_id' in partner and partner.get('quickbooks_id'):
                    partner_id = self.search([('quickbooks_id','=',partner.get('quickbooks_id'))],limit=1)

                    if not partner_id:
                        _logger.info("Create Customer")
                        # print('Parnter dict in if : ',partner)
                        #create new partners
                        if 'parent_qbd_id' in partner and partner.get('parent_qbd_id'):
                            parent_id = self.search([('quickbooks_id','=',partner.get('parent_qbd_id'))],limit=1)
                            if parent_id:
                                vals = self._prepare_partner_dict(partner,parent_id)
                            else:
                                parent_id = self.create_parent_data(partner.get('parent_ref_qbd_id'))
                                if parent_id:
                                    vals = self._prepare_partner_dict(partner, parent_id=parent_id)

                            if vals:
                                new_partner_id = self.create(vals)

                                if new_partner_id:
                                    self.env.cr.commit()
                                    # print('New Partner Commited :: ',new_partner_id.name)
                                    company.write({
                                        'last_imported_qbd_id_for_partners': partner.get("last_time_modified")
                                    })


                        else:
                            vals = self._prepare_partner_dict(partner)
                            if vals:
                                new_partner_id = self.create(vals)

                                if new_partner_id:
                                    self.env.cr.commit()

                                    # print('New Partner Commited :: ', new_partner_id.name)
                                    company.write({
                                        'last_imported_qbd_id_for_partners': partner.get("last_time_modified")
                                    })

                    else:
                        # print('Parnter dict in else : ',partner)
                        #update existing partner record
                        _logger.info("Update Customer")
                        if partner_id.parent_id:
                            vals = self._prepare_partner_dict(partner,partner_id.parent_id)
                        else:
                            vals = self._prepare_partner_dict(partner)

                        partner_id.write(vals)
                        company.write({
                            'last_imported_qbd_id_for_partners': partner.get("last_time_modified")
                        })

        return True

    def create_parent_data(self,quickbook_id=False):
        parent_id = None
        company = self.env['res.users'].search([('id', '=', 2)]).company_id
        if quickbook_id:
            headers = {'content-type': "application/json"}
            params = {'fetch_record': 'one', 'quickbooks_id': quickbook_id, 'to_execute_account':4}

            response = requests.request('GET', company.url + '/import_customer', params=params, headers=headers,
                                        verify=False)
            formatted_data = ast.literal_eval(response.text)
            for record in ast.literal_eval(formatted_data[1]):
                data = record

            if data:
                # print('QBD ID of parent : ',quickbook_id)
                # print('\n\nParnter dict of parent :: ',data,'\n')
                vals = self._prepare_partner_dict(data)
                if vals:
                    parent_id = self.create(vals)

        if parent_id:
            return parent_id


    def _prepare_partner_dict(self,partner,parent_id=False):
        vals = {}
        state = None
        country = None
        
        # 0 ListId (36 varchar) quickbooks_id  --Done
        # 1 ParentRefListID (36 varchar) parent_qbd_id --Done
        # 2 Name (41 varchar) name --Done
        # 3 Salutation (15 varchar) title
        # 4 JobTitle (41 varchar) function --Done
        # 5 Phone (21 varchar) phone --Done
        # 6 AltPhone (21 varchar) mobile --Done
        # 7 Email (1023 varchar) email --Done
        # 8 Notes (4095 varchar) comment --Done
        # 9 BillAddressCity (31 varchar) city --Done
        # 10 BillAddressPostalCode (13 varchar) zip --Done
        # 11 BillAddressState (21 varchar) state_id --Done
        # 12 BillAddressCountry (31 varchar) country_id --Done
        # 13 BillAddressAddr1 (41 varchar) street --Done
        # 14 BillAddressAddr2 (41 varchar)street2 --Done
        # 15 TermsRefListId (36 varchar) terms_qbd_id
        # 16 TimeModified  last_time_modified
        # 17 ResaleNumber vat
        # 18 AccountNumber ref
        # 19 CustomerTypeRefFullName category_name
        # 20 TimeCreated time_created
        # 21 SalesRepFullName

        if parent_id:
            vals.update({
                'parent_id': parent_id.id,
                'company_type':'person',
            })
        else:
            vals.update({'company_type':'company'})

        vals.update({
            'customer_rank':1,
            'quickbooks_id': partner.get('quickbooks_id') if partner.get('quickbooks_id') else '',
            'name': partner.get('name') if partner.get('name') else '',
            'function': partner.get('function') if partner.get('function') else '',
            'phone': partner.get('phone') if partner.get('phone') else '',
            'mobile': partner.get('mobile') if partner.get('mobile') else '',
            'email': partner.get('email') if partner.get('email') else '',
            'comment': partner.get('comment') if partner.get('comment') else '',
            'city': partner.get('city') if partner.get('city') else '',
            'zip': partner.get('zip') if partner.get('zip') else '',
            'street': partner.get('street') if partner.get('street') else '',
            'street2': partner.get('street2') if partner.get('street2') else '',
            'vat': partner.get('vat') if partner.get('vat') else '',
            'ref': partner.get('ref') if partner.get('ref') else '',
            'qbd_date_created': partner.get('time_created') if partner.get('time_created') else False,
        })

        if 'category_name' in partner and partner.get('category_name'):
            category_name = partner.get('category_name')
            if category_name:
                category_id = self.env['res.partner.category'].search([('name', '=', category_name)], limit=1)
                if category_id:
                    vals.update({'category_id': [(6, 0, [category_id.id])]})

        if 'title' in partner and partner.get('title'):
            title = partner.get('title')
            if title:
                title_id = self.env['res.partner.title'].search([('name', '=', title)], limit=1)
                if title_id:
                    vals.update({'title': title_id.id})


        if 'terms_qbd_id' in partner and partner.get('terms_qbd_id'):
            terms_qbd_id = partner.get('terms_qbd_id')
            if terms_qbd_id:
                terms_id = self.env['account.payment.term'].search([('quickbooks_id', '=', terms_qbd_id)], limit=1)
                if terms_id:
                    vals.update({'property_payment_term_id': terms_id.id})

        if 'state' in partner and partner.get('state'):
            state = partner.get('state')
        if 'country' in partner and partner.get('country'):
            country= partner.get('country')
        if state and country:
            country_id = self.env['res.country'].search(['|',('name','=',country),('code','=',country)],limit=1)
            if country_id:
                vals.update({'country_id': country_id.id})
                state_id = self.env['res.country.state'].search(['|',('name','=',state),('code','=',state)],limit=1)
                if state_id :
                    if state_id.country_id.id == country_id.id:
                        vals.update({'state_id':state_id.id})
                else:
                    state_id = self.env['res.country.state'].create({'name': state, 'code': state, 'country_id': country_id.id})
                    vals.update({'state_id': state_id.id})
            else:
                country_id = self.env['res.country'].create({'name':country})
                vals.update({'country_id': country_id.id})
                state_id = self.env['res.country.state'].create({'name': state, 'code': state, 'country_id':country_id.id})
                vals.update({'state_id': state_id.id})

        if not state and country:
            country_id = self.env['res.country'].search(['|', ('name', '=', country), ('code', '=', country)], limit=1)
            if country_id:
                vals.update({'country_id': country_id.id})

        if 'user_name' in partner and partner.get('user_name'):
            user_name = partner.get('user_name')
            if user_name:
                user_id = self.env['res.users'].search([('name', '=', user_name)], limit=1)
                if user_id:
                    vals.update({'user_id': user_id.id})

        if vals:
            return vals


    def create_vendors(self,vendors):
        # print('\nVendors count : ',len(vendors))
        company = self.env['res.users'].search([('id', '=', 2)]).company_id

        for vendor in vendors:
            vals = {}
            if 'quickbooks_id' in vendor and vendor.get('quickbooks_id'):
                vendor_id = self.search([('quickbooks_id','=',vendor.get('quickbooks_id')),('customer_rank','=',0)],limit=1)

                if not vendor_id:
                    _logger.info("Create Vendor")
                    # print('\n\nVendor dict in ifffffff : ',vendor,'\n')
                    #create new vendor
                    vals = self._prepare_vendor_dict(vendor)
                    if vals:
                        new_vendor_id = self.create(vals)

                        if new_vendor_id:
                            self.env.cr.commit()

                            company.write({
                                'last_imported_qbd_id_for_vendors': vendor.get("last_time_modified")
                            })

                else:
                    _logger.info("Update Vendor")
                    # print('\n\nVendor dict in elseeeee : ',vendor,'\n\n')
                    #update existing vendor record
                    vals = self._prepare_vendor_dict(vendor)
                    vendor_id.write(vals)

                    company.write({
                        'last_imported_qbd_id_for_vendors': vendor.get("last_time_modified")
                    })

        return True


    def _prepare_vendor_dict(self,vendor):
        vals = {}
        state = None
        country = None

        #0 ListId (36 varchar) quickbooks_id --DONE
        #1 Name (41 varchar) name --DONE
        #2 Salutation (15 varchar) title --DONE
        #3 Phone (21 varchar) phone --DONE
        #4 AltPhone (21 varchar) mobile --DONE
        #5 Email (1023 varchar) email --DONE
        #6 Notes (4095 varchar) comment --DONE
        #7 VendorAddressCity (31 varchar) city --DONE
        #8 VendorAddressPostalCode (13 varchar) zip --DONE
        #9 VendorAddressState (21 varchar) state_id --DONE
        #10 VendorAddressCountry (31 varchar) country_id --DONE
        #11 VendorAddressAddr1 (41 varchar) street --DONE
        #12 VendorAddressAddr2 (41 varchar)street2 --DONE
        #13 TermsRefListId (36 varchar) terms_qbd_id --DONE
        #14 TimeModified  last_time_modified --DONE
        #15 ResaleNumber vat
        #16 AccountNumber ref
        #17 VendorTypeRefFullName category_name

        vals.update({
            'company_type': 'person',
            'supplier_rank': 1,
            'customer_rank': 0,
            'quickbooks_id': vendor.get('quickbooks_id') if vendor.get('quickbooks_id') else '',
            'name': vendor.get('name') if vendor.get('name') else '',
            'phone': vendor.get('phone') if vendor.get('phone') else '',
            'mobile': vendor.get('mobile') if vendor.get('mobile') else '',
            'email': vendor.get('email') if vendor.get('email') else '',
            'comment': vendor.get('comment') if vendor.get('comment') else '',
            'city': vendor.get('city') if vendor.get('city') else '',
            'zip': vendor.get('zip') if vendor.get('zip') else '',
            'street': vendor.get('street') if vendor.get('street') else '',
            'street2': vendor.get('street2') if vendor.get('street2') else '',
            'vat': vendor.get('vat') if vendor.get('vat') else '',
            'ref': vendor.get('ref') if vendor.get('ref') else '',
        })
        if 'category_name' in vendor and vendor.get('category_name'):
            category_name = vendor.get('category_name')
            if category_name:
                category_id = self.env['res.partner.category'].search([('name', '=', category_name)], limit=1)
                if category_id:
                    vals.update({'category_id': [(6, 0, [category_id.id])]})

        if 'title' in vendor and vendor.get('title'):
            title = vendor.get('title')
            if title:
                title_id = self.env['res.partner.title'].search([('name', '=', title)], limit=1)
                if title_id:
                    vals.update({'title': title_id.id})

        if 'state' in vendor and vendor.get('state'):
            state = vendor.get('state')
        if 'country' in vendor and vendor.get('country'):
            country = vendor.get('country')

        if 'terms_qbd_id' in vendor and vendor.get('terms_qbd_id'):
            terms_qbd_id = vendor.get('terms_qbd_id')
            if terms_qbd_id:
                terms_id = self.env['account.payment.term'].search([('quickbooks_id', '=', terms_qbd_id)], limit=1)
                if terms_id:
                    vals.update({'property_supplier_payment_term_id': terms_id.id})

        if state and country:
            country_id = self.env['res.country'].search(['|', ('name', '=', country), ('code', '=', country)], limit=1)
            if country_id:
                vals.update({'country_id': country_id.id})
                state_id = self.env['res.country.state'].search(['|', ('name', '=', state), ('code', '=', state)],
                                                                limit=1)
                if state_id:
                    if state_id.country_id.id == country_id.id:
                        vals.update({'state_id': state_id.id})
                else:
                    state_id = self.env['res.country.state'].create({'name': state, 'code': state, 'country_id': country_id.id})
                    vals.update({'state_id': state_id.id})
            else:
                country_id = self.env['res.country'].create({'name': country})
                vals.update({'country_id': country_id.id})
                state_id = self.env['res.country.state'].create({'name': state, 'code': state, 'country_id': country_id.id})
                vals.update({'state_id': state_id.id})

        if not state and country:
            country_id = self.env['res.country'].search(['|', ('name', '=', country), ('code', '=', country)], limit=1)
            if country_id:
                vals.update({'country_id': country_id.id})

        if vals:
            # print('Valsssssssssssssssssss : ',vals)

            return vals


    ### Export Partners

    def export_partners(self):
        # print('IN ITTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT')
        loger_dict={}
        partner_data_list = []
        company = self.env['res.users'].search([('id', '=', 2)]).company_id
        partners = None
        limit = 0
        # ctx = self._context or {}
        #
        # ctx.update({'dont_update_is_update': False})
        if company.export_cus_limit:
            limit=int(company.export_cus_limit)

        if company.export_updated_record == False:
            # print('\n\nExport Newly Created Partners\n\n')
            partners = self.search([('quickbooks_id','=',None),('customer_rank','=',1), ('is_company', '=', True)],limit=limit)
            if partners:
                # print ("Length of partnerssssssssssssssssssssssssssss --------------------------------", len(partners))
                # print ("Length of partnerssssssssssssssssssssssssssss --------------------------------", limit)
                #send records having comapny_type = Company
                if partners:
                    for partner in partners:
                        partner_dict = {}
                        if partner.company_type == 'company':
                            partner_dict = self.get_partner_dict(partner)

                            if partner_dict:
                                partner_data_list.append(partner_dict)

                if partner_data_list:
                    # print('\n\nPartner data List for Company : ',partner_data_list,'\n\n')
                    # print('Total Count : ', len(partner_data_list))
                    company = self.env['res.users'].search([('id', '=', 2)]).company_id
                    headers = {'content-type': "application/json"}
                    data = partner_data_list

                    data = {'customers_list': data}

                    response = requests.request('POST', company.url + '/export_customers', data=json.dumps(data),
                                                headers=headers,
                                                verify=False)

                    # print("Response Text", type(response.text), response.text)

                    resp = ast.literal_eval(response.text)

                    # print('Resp : ',resp)

                    for res in resp[0].get('Data'):

                        if 'odoo_id' in res and res.get('odoo_id'):
                            partner_id = self.browse(int(res.get('odoo_id')))

                            if partner_id:
                                if res.get('quickbooks_id'):
                                    partner_id.write({'quickbooks_id': res.get('quickbooks_id')})
                        loger_dict.update({'operation': 'Export Partner',
                                           'odoo_id': res.get('odoo_id'),
                                           'qbd_id': res.get('quickbooks_id'),
                                           'message': res.get('messgae')
                                           })
                        qbd_loger_id = self.env['qbd.loger'].create(loger_dict)
                        # company.write({'qbd_loger_id': [(4, qbd_loger_id.id)]})

            # print (" --------------------------------------------------- ")
            # print (len(partners))
            # print (limit)
            # print (len(partners) < limit)

            if len(partners) < limit:
                limit = limit - len(partners)
                partners = None
                partner_data_list = []
                # send records having comapny_type = Person
                partners = self.search([('quickbooks_id', '=', None), ('customer_rank', '=', 1), ('is_company', '=', False)], limit=limit)
                print ("Length of partnerssssssssssssssssssssssssssss --------------------------------", len(partners))
                print ("Length of partnerssssssssssssssssssssssssssss --------------------------------", limit)

                if partners:
                    for partner in partners:
                        partner_dict = {}
                        if partner.company_type == 'person':
                            partner_dict = self.get_partner_dict(partner,is_send_parent_ref=True)

                            if partner_dict:
                                partner_data_list.append(partner_dict)

                if partner_data_list:
                    # print('\n\nPartner data List for Persons: ', partner_data_list, '\n\n')
                    # print('Total Count : ',len(partner_data_list))
                    company = self.env['res.users'].search([('id', '=', 2)]).company_id
                    headers = {'content-type': "application/json"}
                    data = partner_data_list

                    data = {'customers_list': data}

                    response = requests.request('POST', company.url + '/export_customers', data=json.dumps(data),
                                                headers=headers,
                                                verify=False)

                    # print("Response Text of person", type(response.text), response.text)

                    resp = ast.literal_eval(response.text)

                    # print('Resp of person: ', resp)

                    for res in resp[0].get('Data'):

                        if 'odoo_id' in res and res.get('odoo_id'):
                            partner_id = self.browse(int(res.get('odoo_id')))

                            if partner_id:
                                if res.get('quickbooks_id'):
                                    partner_id.write({'quickbooks_id': res.get('quickbooks_id')})
                    loger_dict.update({'operation': 'Export Partner',
                                       'odoo_id': res.get('odoo_id'),
                                       'qbd_id': res.get('quickbooks_id'),
                                       'message': res.get('messgae')
                                       })
                    qbd_loger_id = self.env['qbd.loger'].create(loger_dict)
                    # company.write({'qbd_loger_id': [(4, qbd_loger_id.id)]})


        else:
            # print('\n\nExport Only Updated Records\n')
            partners = self.search([('quickbooks_id', '!=', False), ('customer_rank', '=', 1),('is_updated','=',True)],limit=limit)
            # print('Parnters',partners)
            if partners:
                for partner in partners:
                    partner_dict = {}
                    partner_dict = self.get_partner_dict(partner, company.export_updated_record,is_send_parent_ref=True,)

                    if partner_dict:
                        partner_data_list.append(partner_dict)

            if partner_data_list:
                # print('\n\nPartner data List : ', partner_data_list, '\n\n')
                # print('Total Count : ', len(partner_data_list))
                company = self.env['res.users'].search([('id', '=', 2)]).company_id
                headers = {'content-type': "application/json"}
                data = partner_data_list

                data = {'customers_list': data}

                response = requests.request('POST', company.url + '/export_customers', data=json.dumps(data),
                                            headers=headers,
                                            verify=False)
                

                # print("Response Text of person", type(response.text), response.text)

                resp = ast.literal_eval(response.text)

                for res in resp[0].get('Data'):

                    if 'odoo_id' in res and res.get('odoo_id'):
                        partner_id = self.browse(int(res.get('odoo_id')))

                        if partner_id:
                            partner_id.write({'is_updated': False})

                    loger_dict.update({'operation': 'Export Partner',
                                       'odoo_id': res.get('odoo_id'),
                                       'qbd_id': res.get('quickbooks_id'),
                                       'message': res.get('messgae')
                                       })
                    qbd_loger_id = self.env['qbd.loger'].create(loger_dict)
                    # company.write({'qbd_loger_id': [(4, qbd_loger_id.id)]})

        return True

    def get_partner_dict(self,partner,is_send_updated=False,is_send_parent_ref=False):
        # print('Hereeeeeeeeeeeeeeeeeeeeeeeeee')

        partner_dict = {}

        if is_send_updated:
            partner_dict.update({
                'partner_qbd_id':partner.quickbooks_id # partner_qbd_id (varchar 36) Only for Update Query
            })
        else:
            partner_dict.update({
                'partner_qbd_id': '' # partner_qbd_id (varchar 36) Only for Update Query
            })


        if is_send_parent_ref:
            partner_dict.update({
                'parent_ref': partner.parent_id.quickbooks_id if partner.parent_id else '', # parent_ref (36 varchar)
                'company': False,
            })
        else:
            partner_dict.update({
                'company': True,
            })

        # name (41 varchar) Needs Validation
        # title (15 varchar)
        # first_name (25 varchar) Needs Validation
        # last_name (25 varchar) Needs Validation
        # function (41 varchar)
        # phone (21 varchar)
        # mobile (21 varchar)
        # email (1023 varchar)
        # comment (4095 varchar)
        # city (31 varchar)
        # zip (13 varchar)
        # state_id (21 varchar)
        # country_id (31 varchar)
        # terms_qbd_id (36 varchar)
        # vat
        # ref
        # tags_id

        bad_chars = [';', ':', '!', "*", "$", "'"]
        name = partner.name
        for i in bad_chars:
            name = name.replace(i,"")

        if len(name) > 40:
            name = name[:40]

        full_name = name.split(' ',1)
        first_name = full_name[0][:24]
        if len(full_name) > 1:
            last_name = full_name[1][:24]
        else:
            last_name = ''

        if partner.comment:
            bad_chars = [';', ':', '!', "*", "$", "'"]
            comment = partner.comment
            for i in bad_chars:
                comment = comment.replace(i,"")
        else:
            comment = ''

        # print (" ----------------- ",partner.parent_id,partner.parent_id.name)

        partner_dict.update({
            'odoo_id': partner.id,
            'name': name,
            'company_ref_name': partner.parent_id.name if partner.parent_id else name,
            'title': partner.title.name if partner.title.name else '',
            'first_name': first_name,
            'last_name': last_name,
            'function': partner.function if partner.function else '',
            'phone': partner.phone if partner.phone else '',
            'mobile': partner.mobile if partner.mobile else '',
            'email': partner.email if partner.email else '',
            'comment': comment,
            'city': partner.city if partner.city else '',
            'zip': partner.zip if partner.zip else '',
            'state_id': partner.state_id.code if partner.state_id else '',
            'country_id': partner.country_id.code if partner.country_id else '',
            'terms_qbd_id':partner.property_payment_term_id.quickbooks_id if partner.property_payment_term_id.quickbooks_id else '',
            'vat': partner.vat if partner.vat else '',
            'ref': partner.ref if partner.ref else '',
            'category_name': partner.category_id.name if partner.category_id.name else '',
            # 'website': partner.website if partner.website else '',
        })

        if partner.street:
            bad_chars = [';', ':', '!', "*", "$", "'"]
            street = partner.street
            for i in bad_chars:
                street = street.replace(i, "")
            data = street # street (41 varchar)
            partner_dict.update({'street': (data[:40]) if len(data) > 40 else data})

        if partner.street2:
            bad_chars = [';', ':', '!', "*", "$", "'"]
            street2 = partner.street2
            for i in bad_chars:
                street2 = street2.replace(i, "")
            data = street2 # street2 (41 varchar)
            partner_dict.update({'street2': (data[:40]) if len(data) > 40 else data})

        return partner_dict

    #Export Vendors
    def export_vendors(self):
        # print('\nIn Export Vendorsssssssss\n')
        vendor_data_list = []
        loger_dict={}
        # ctx = self._context or {}
        #
        # ctx.update({'dont_update_is_update': False})
        company = self.env['res.users'].search([('id', '=', 2)]).company_id
        if company.export_ven_limit:
            limit = int(company.export_ven_limit)
        else:
            limit = 0

        if company.export_updated_record:
            vendors = self.search(['|',('quickbooks_id', '!=', None),('quickbooks_id', '!=', ''), ('supplier_rank', '=', 1),('is_updated','=',True)],limit=limit)
        else:
            vendors = self.search(['|',('quickbooks_id', '=', None),('quickbooks_id', '=', ''), ('supplier_rank', '=', 1)],limit=limit)

        if vendors:
            for vendor in vendors:
                vendor_dict = {}
                if company.export_updated_record:
                    vendor_dict = self.get_vendor_dict(vendor,company.export_updated_record)
                else:
                    vendor_dict = self.get_vendor_dict(vendor)

                if vendor_dict:
                    vendor_data_list.append(vendor_dict)

        if vendor_data_list:
            # print('\n\nVendor data List : ', vendor_data_list, '\n\n')
            # print('Total Count : ', len(vendor_data_list))
            company = self.env['res.users'].search([('id', '=', 2)]).company_id
            headers = {'content-type': "application/json"}
            data = vendor_data_list

            data = {'vendors_list': data}

            response = requests.request('POST', company.url + '/export_vendors', data=json.dumps(data),
                                        headers=headers,
                                        verify=False)

            # print("Response Text ", type(response.text), response.text)

            resp = ast.literal_eval(response.text)

            print('\n\nResp  : ', resp,'\n\n')
            if company.export_updated_record == False:
                for res in resp[0].get('Data'):

                    if 'odoo_id' in res and res.get('odoo_id'):
                        vendor_id = self.browse(int(res.get('odoo_id')))

                        if vendor_id:
                            if res.get('quickbooks_id'):
                                vendor_id.write({'quickbooks_id': res.get('quickbooks_id')})
                    loger_dict.update({'operation': 'Export Vendor',
                                       'odoo_id': res.get('odoo_id'),
                                       'qbd_id': res.get('quickbooks_id'),
                                       'message': res.get('messgae')
                                       })
                    qbd_loger_id = self.env['qbd.loger'].create(loger_dict)
                    # company.write({'qbd_loger_id': [(4, qbd_loger_id.id)]})

            else:
                for res in resp[0].get('Data'):

                    if 'odoo_id' in res and res.get('odoo_id'):
                        vendor_id = self.browse(int(res.get('odoo_id')))

                        if vendor_id:
                            vendor_id.write({'is_updated': False})
                    loger_dict.update({'operation': 'Export Vendor',
                                       'odoo_id': res.get('odoo_id'),
                                       'qbd_id': res.get('quickbooks_id'),
                                       'message': res.get('messgae')
                                       })
                    qbd_loger_id = self.env['qbd.loger'].create(loger_dict)
                    # company.write({'qbd_loger_id': [(4, qbd_loger_id.id)]})

        return True


    def get_vendor_dict(self,vendor,is_send_only_updated=False):

        vendor_dict = {}

        if is_send_only_updated:
            vendor_dict.update({
                    'vendor_qbd_id': vendor.quickbooks_id
                })
        else:
            vendor_dict.update({
                'vendor_qbd_id': ''
            })

        # name (41 varchar) Needs Validation
        # title (15 varchar)
        # first_name (25 varchar) Needs Validation
        # last_name (25 varchar) Needs Validation
        # phone (21 varchar)
        # mobile (21 varchar)
        # email (1023 varchar)
        # comment (4095 varchar)
        # city (31 varchar)
        # zip (13 varchar)
        # state_id (21 varchar)
        # country_id (31 varchar)
        # terms_qbd_id (36 varchar)
        # vat
        # ref
        # category_name

        bad_chars = [';', ':', '!', "*", "$", "'"]
        name = vendor.name
        for i in bad_chars:
            name = name.replace(i,"")

        if len(name) > 40:
            name = name[:40]

        full_name = name.split(' ',1)
        print ("Full Nameeeeeeeeeeeeeeeeeeeeeeeeeee",full_name[0][:24])
        first_name = full_name[0][:24]
        if len(full_name) > 1:
            last_name = full_name[1][:24]
        else:
            last_name = ''

        if vendor.comment:
            bad_chars = [';', ':', '!', "*", "$", "'"]
            comment = vendor.comment
            for i in bad_chars:
                comment = comment.replace(i,"")
        else:
            comment = ''

        vendor_dict.update({
            'odoo_id': vendor.id,
            'name': name,
            'title': vendor.title.name if vendor.title.name else '',
            'first_name': first_name,
            'last_name': last_name,
            'phone': vendor.phone if vendor.phone else '',
            'mobile': vendor.mobile if vendor.mobile else '',
            'email': vendor.email if vendor.email else '',
            'comment': comment,
            'city': vendor.city if vendor.city else '',
            'zip': vendor.zip if vendor.zip else '',
            'state_id': vendor.state_id.code if vendor.state_id else '',
            'country_id': vendor.country_id.code if vendor.country_id else '',
            'terms_qbd_id': vendor.property_supplier_payment_term_id.quickbooks_id if vendor.property_supplier_payment_term_id.quickbooks_id else '',
            'vat': vendor.vat if vendor.vat else '',
            'ref': vendor.ref if vendor.ref else '',
            'category_name': vendor.category_id.name if vendor.category_id.name else '',
        })

        if vendor.street:
            bad_chars = [';', ':', '!', "*", "$", "'"]
            street = vendor.street
            for i in bad_chars:
                street = street.replace(i, "")
            data = street # street (41 varchar)
            vendor_dict.update({'street': (data[:40]) if len(data) > 40 else data}) # street (41 varchar)


        if vendor.street2:
            bad_chars = [';', ':', '!', "*", "$", "'"]
            street2 = vendor.street2
            for i in bad_chars:
                street2 = street2.replace(i, "")
            data = street2
            vendor_dict.update({'street2': (data[:40]) if len(data) > 40 else data})

        if vendor_dict:
            return vendor_dict


