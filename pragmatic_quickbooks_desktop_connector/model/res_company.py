import logging
from odoo import api, fields, models, _
import requests
import json
import ast
from datetime import datetime

from odoo.exceptions import except_orm, Warning, RedirectWarning,ValidationError,UserError
from requests.exceptions import ConnectionError


_logger = logging.getLogger(__name__)


class Qb_Config_Settings(models.Model):
    _inherit = 'res.company'

    # last_imported_date_of_accounts = fields.Datetime("Last Imported On")
    # last_imported_date_of_payment_methods = fields.Datetime("Last Imported On")
    # last_imported_date_of_partners = fields.Datetime("Last Imported On")
    # last_imported_date_of_vendors = fields.Datetime("Last Imported On")
    # last_imported_date_of_products = fields.Datetime("Last Imported On")
    # last_imported_date_of_orders = fields.Datetime("Last Imported On")
    # last_imported_date_of_invoices = fields.Datetime("Last Imported On")
    # last_imported_date_of_payments = fields.Datetime("Last Imported On")
    # last_imported_date_of_purchase_orders = fields.Datetime("Last Imported On")
    # qbd_loger_id = fields.One2many('qbd.loger','res_company_id')
    # limit = fields.Char('Limit for export record',default=100)
    # import_limit = fields.Char('Limit for import record',default=100)

    url = fields.Char("Server Instance", help='Enter your php instance path for eg.http://192.0.0.0')
    last_imported_qbd_id_for_account = fields.Char("Account Last Imported Modified Date")
    last_imported_qbd_id_for_payment_methods = fields.Char("Payment Methods Last Imported Modified Date")
    last_imported_qbd_id_for_partners = fields.Char("Partners Last Imported Modified Date")
    last_imported_qbd_id_for_vendors = fields.Char("Vendors Last Imported Modified Date")
    last_imported_qbd_id_for_product = fields.Char("Product Last Imported Modified Date")
    last_imported_qbd_id_for_sale_orders = fields.Char("Sale Order Last Imported Modified Date")
    last_imported_qbd_id_for_invoice = fields.Char("Invoice Last Imported Modified Date")
    last_imported_qbd_id_for_payments = fields.Char("Payments Last Imported Modified Date")
    last_imported_qbd_id_for_purchase_orders = fields.Char("Purchase Order Last Imported Modified Date")

    qb_account_recievable = fields.Many2one('account.account', 'Account Recievable')
    qb_account_payable = fields.Many2one('account.account', 'Account Payable')
    qb_income_account = fields.Many2one('account.account', 'Income Account')
    qb_expense_account = fields.Many2one('account.account', 'Expense Account')
    qb_asset_account = fields.Many2one('account.account', 'AssetAccount')
    qb_cogs_account = fields.Many2one('account.account', 'COGSAccount')
    qb_default_tax = fields.Many2one('account.tax', 'Default Tax')

    import_acc_limit = fields.Char('Import Accounts', default=50)
    import_cus_limit = fields.Char('Import Customer', default=50)
    import_ven_limit = fields.Char('Import Vendors', default=50)
    import_pro_limit = fields.Char('Import Prdoucts', default=50)
    import_so_limit = fields.Char('Import Sales Orders', default=20)
    import_inv_limit = fields.Char('Import Invoice', default=20)
    import_pay_limit = fields.Char('Import Payments', default=50)
    import_po_limit = fields.Char('Import Purchase Order', default=20)

    export_updated_record = fields.Boolean('Export Updated Record')
    export_acc_limit = fields.Char('Export Accounts', default=50)
    export_cus_limit = fields.Char('Export Customer', default=50)
    export_ven_limit = fields.Char('Export Vendors', default=50)
    export_pro_limit = fields.Char('Export Prdoucts', default=50)
    export_so_limit = fields.Char('Export Sales Orders', default=20)
    export_inv_limit = fields.Char('Export Invoice', default=20)
    export_pay_limit = fields.Char('Export Payments', default=50)
    export_po_limit = fields.Char('Export Purchase Order', default=20)

    export_sales_order_date = fields.Char('Export Sales Order Date', default=False)
    export_invoice_date = fields.Char('Export Invoice Date', default=False)
    export_payment_date = fields.Char('Export Payment Date', default=False)
    export_purchase_order_date = fields.Char('Export Purchase Date', default=False)

    # setting up the Account Receivable for Partners
    @api.onchange('qb_account_recievable')
    def onchange_qb_account_recievable(self):
        if self.qb_account_recievable:
            acc_dict = {}
            acc_dict.update({'name': 'property_account_receivable_id'})
            
            field_id = self.env['ir.model.fields'].search([('name', '=', 'property_account_receivable_id'),
                                                           ('model_id.name', '=', 'Contact')])
            property_account_receivable_id = self.env['ir.property'].sudo().search([('name', '=', 'property_account_receivable_id'),
                                                                                    ('fields_id.model_id.name', '=', 'Contact')])
            if property_account_receivable_id:
                property_account_receivable_id.write({'value_reference': 'account.account,' + str(self.qb_account_recievable.id)})
            else:
                if field_id:
                    acc_dict.update({'value_reference': 'account.account,' + str(self.qb_account_recievable.id),
                                     'fields_id': field_id.id})
                    self.env['ir.property'].sudo().create(acc_dict)


    # Setting Up the Account Payable for Partners
    @api.onchange('qb_account_payable')
    def onchange_qb_account_payable(self):
        if self.qb_account_payable:
            acc_dict = {}
            acc_dict.update({'name': 'property_account_payable_id'})
            
            field_id = self.env['ir.model.fields'].search([('name', '=', 'property_account_payable_id'),
                                                           ('model_id.name', '=', 'Contact')])
            property_account_payable_id = self.env['ir.property'].sudo().search([('name', '=', 'property_account_payable_id'),
                                                                                    ('fields_id.model_id.name', '=', 'Contact')])
            if property_account_payable_id:
                property_account_payable_id.write({'value_reference': 'account.account,' + str(self.qb_account_payable.id)})
            else:
                if field_id:
                    acc_dict.update({'value_reference': 'account.account,' + str(self.qb_account_payable.id),
                                     'fields_id': field_id.id})
                    self.env['ir.property'].sudo().create(acc_dict)
    
    # Setting Up the Income Account for Product Category
    @api.onchange('qb_income_account')
    def onchange_qb_income_account(self):
        if self.qb_income_account:
            acc_dict = {}
            acc_dict.update({'name': 'property_account_income_categ_id'})
            
            field_id = self.env['ir.model.fields'].search([('name', '=', 'property_account_income_categ_id'),
                                                           ('model_id.name', '=', 'Product Category')])
            property_account_income_categ_id = self.env['ir.property'].sudo().search([('name', '=', 'property_account_income_categ_id'),
                                                                                    ('fields_id.model_id.name', '=', 'Product Category')])
            if property_account_income_categ_id:
                property_account_income_categ_id.write({'value_reference': 'account.account,' + str(self.qb_income_account.id)})
            else:
                if field_id:
                    acc_dict.update({'value_reference': 'account.account,' + str(self.qb_income_account.id),
                                     'fields_id': field_id.id})
                    self.env['ir.property'].sudo().create(acc_dict)
        
    # Setting Up the Expense Account for Product Category
    @api.onchange('qb_expense_account')
    def onchange_qb_expense_account(self):
        if self.qb_expense_account:
            acc_dict = {}
            acc_dict.update({'name': 'property_account_expense_categ_id'})
            
            field_id = self.env['ir.model.fields'].search([('name', '=', 'property_account_expense_categ_id'),
                                                           ('model_id.name', '=', 'Product Category')])
            property_account_expense_categ_id = self.env['ir.property'].sudo().search([('name', '=', 'property_account_expense_categ_id'),
                                                                                    ('fields_id.model_id.name', '=', 'Product Category')])
            if property_account_expense_categ_id:
                property_account_expense_categ_id.write({'value_reference': 'account.account,' + str(self.qb_expense_account.id)})
            else:
                if field_id:
                    acc_dict.update({'value_reference': 'account.account,' + str(self.qb_expense_account.id),
                                     'fields_id': field_id.id})
                    self.env['ir.property'].sudo().create(acc_dict)
        
    # @api.multi
    def sendMessage(self, response):
        message = ''
        # print('response TEXT : ',response.text)
        # if response.ok:
        #     response_text = json.loads(response.text)
        if 'Message' in response:
            message=response['Message']
        #            message = response.json()
        else:
            if 400 <= response.status_code < 500:
                message = u'%s Client Error for url: %s' % (response.status_code, self.url)

            elif 500 <= response.status_code < 600:
                message = u'%s Server Error for url: %s' % (response.status_code, self.url)

        data_obj = self.env['ir.model.data']
        view_id = self.env.ref('pragmatic_quickbooks_desktop_connector.response_message_wizard_form').id
        if view_id:
            value = {
                'name': _('Message'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'response.message.wizard',
                'view_id': False,
                'context': {'message': message},
                'views': [(view_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
            return value

    # @api.multi
    def test_qb_connection(self):

        headers = {'content-type': "application/json"}
        try:
            response = requests.get(self.url+'/test_connection', verify=False)

        # except ConnectionError as ce:
        #     raise Warning("We were not able to connect to your Quickbooks!!")
        except Exception as e:
            return self.sendMessage({'Message': "Connection Check to Quickbooks Unsuccessful !!"})

#         print("\n\n test connection response",response.text)
        r = json.loads(response.text)
        if r.get('Status') == 200:
            return self.sendMessage({'Message':"Connection Check to Quickbooks Successful !!"})
        else:
            return self.sendMessage({'Message': "Connection Check to Quickbooks Unsuccessful !!"})

    #@api.multi
    def check_tax_code_for_order_invoices(self):
        pass

        logger_obj = self.env['qbd.orderinvoice.logger']
        self.env['qbd.orderinvoice.logger'].search([]).unlink()

        # Find Sale Order - Tax Code
        self.env.cr.execute("SELECT order_id FROM sale_order_line WHERE qbd_tax_code is NULL and product_id is NOT NULL")
        result = self.env.cr.fetchall()

        if result:
            common_so = list(set(result))
            for rec in common_so:
                self.env.cr.execute("SELECT id,name,quickbooks_id FROM sale_order WHERE id={}".format(rec[0]))
                result = self.env.cr.fetchall()
                for row in result:
                    if row[2]:
                        logger_obj.create({'odoo_id': row[0], 'name': row[1], 'type': 'sale', 'qbd_id': row[2], 'message': 'Tax Code Missing'})
                    else:
                        logger_obj.create({'odoo_id': row[0], 'name': row[1], 'type': 'sale', 'qbd_id': None, 'message': 'Tax Code Missing'})


        # Find Invoices - Tax Code
        self.env.cr.execute("SELECT move_id FROM account_move_line WHERE qbd_tax_code is NULL and product_id is NOT NULL")
        result = self.env.cr.fetchall()

        if result:
            common_inv = list(set(result))
            for rec in common_inv:
                self.env.cr.execute("SELECT id,name,quickbooks_id FROM account_move WHERE id={}".format(rec[0]))
                result = self.env.cr.fetchall()
                for row in result:
                    if row[2]:
                        logger_obj.create({'odoo_id': row[0], 'name': row[1], 'type': 'invoice', 'qbd_id': row[2], 'message': 'Tax Code Missing'})
                    else:
                        logger_obj.create({'odoo_id': row[0], 'name': row[1], 'type': 'invoice', 'qbd_id': None, 'message': 'Tax Code Missing'})

    # @api.multi
    def check_duplicates(self):

        logger_obj = self.env['qbd.duplicates.logger']
        self.env['qbd.duplicates.logger'].search([]).unlink()

        # Find PRODUCTS Duplicate#
        # self.env.cr.execute("SELECT id,default_code,name,quickbooks_id FROM product_template WHERE default_code IN (SELECT default_code FROM product_template GROUP BY default_code HAVING (COUNT(default_code) > 1))")
        # internal_ref_result = self.env.cr.fetchall()
        # print("\n\n\nInternal Ref Result",internal_ref_result)

        # Find PRODUCTS Duplicate#
        self.env.cr.execute("SELECT id,default_code,name,quickbooks_id FROM product_template WHERE name IN (SELECT name FROM product_template GROUP BY name,default_code HAVING (COUNT(name) > 1))")
        same_name_result = self.env.cr.fetchall()
        # print("\n\n\nSame Name Result",same_name_result)

        # result = list(set(internal_ref_result + same_name_result))
        result = list(set(same_name_result))
        # print("\n\n\n\nResult",result)
        if result:
            for row in result:
                if row[3]:
                    logger_obj.create({'odoo_id':row[0], 'parent_dcode':row[1] , 'name':row[2], 'type':'product', 'qbd_id':row[3], 'message':'Name/Internal Reference matches with Record in Odoo so modify the other Name/Internal Reference before exporting it to Odoo'})
                else:
                    logger_obj.create({'odoo_id':row[0], 'parent_dcode':row[1], 'name': row[2], 'type': 'product', 'qbd_id':None , 'message':'Same Name/Internal Reference'})

        # Find Customer Duplicate#
        self.env.cr.execute("SELECT id,parent_id,name,display_name,quickbooks_id FROM res_partner WHERE supplier_rank= 0 and display_name IN (SELECT display_name FROM res_partner WHERE supplier_rank= 0 GROUP BY display_name HAVING (COUNT(display_name) > 1))")
        # self.env.cr.execute("SELECT id,name FROM res_partner WHERE supplier= 'false' and quickbooks_id IS NULL and name IN (SELECT name FROM res_partner GROUP BY name HAVING (COUNT(name) > 1))")
        result = self.env.cr.fetchall()
        # print("\n\n\nDuplicate",result)
        if result:
            for row in result:
#                 print ("ROW -- ",row[1],row[2],row[3])
                if row[1]:
                    parent = row[3].replace(row[2],'')
                    parent = parent[:-2]
                else:
                    parent = None

                if row[4]:
                    qbd_id = row[4]
                    message = 'Name matches with Record in Odoo so modify the other record before exporting it to Odoo'
                else:
                    qbd_id = None
                    message = 'Same Name'

                logger_obj.create({'odoo_id':row[0], 'parent_dcode':parent, 'name':row[2], 'type':'customer', 'qbd_id':qbd_id, 'message':message})

        # Find VENDOR Duplicate#
        self.env.cr.execute("SELECT id,name FROM res_partner WHERE supplier_rank = 1 and quickbooks_id IS NULL and name IN (SELECT name FROM res_partner GROUP BY name HAVING (COUNT(name) > 1))")
        result = self.env.cr.fetchall()
        # print (result)
        if result:
            for row in result:
                logger_obj.create({'odoo_id':row[0], 'name':row[1], 'type':'vendor', 'message':'Same Name'})

        return self.sendMessage({'Message': "Check Duplicate Loggers if duplicate found and remove duplicates before exporting records !!"})

    # @api.multi
    def empty_quickbooks_id(self):
        return self.sendMessage({'Message': "Quickbooks Id and import datetime removed from all master successfully !!"})

    # @api.multi
    def import_export_essential(self):
        logger_obj = self.env['qbd.connection.logger']
        self.import_partner_category(logger_obj)
        self.import_vendor_category(logger_obj)
        self.import_partner_title(logger_obj)
        self.import_payment_terms(logger_obj)
        self.import_sales_tax(logger_obj)
        self.import_tax_code(logger_obj)

        # self.export_payment_terms()

    # @api.multi
    def empty_quickbooks_id(self):
        partner_records = self.env['res.partner'].search([])
        for rec in partner_records:
            rec.write({'quickbooks_id': False})

        invoice_records = self.env['account.move'].search([])
        for rec in invoice_records:
            rec.write({'quickbooks_id': False})

        tax_code_records = self.env['qbd.tax.code'].search([])
        for rec in tax_code_records:
            rec.write({'quickbooks_id': False})

        account_records = self.env['account.account'].search([])
        for rec in account_records:
            rec.write({'quickbooks_id': False})

        payment_records = self.env['account.payment'].search([])
        for rec in payment_records:
            rec.write({'quickbooks_id': False})

        sale_order_records = self.env['sale.order'].search([])
        for rec in sale_order_records:
            rec.write({'quickbooks_id': False})

        product_records = self.env['product.template'].search([])
        for rec in product_records:
            rec.write({'quickbooks_id': False})

        partner_category_records = self.env['res.partner.category'].search([])
        for rec in partner_category_records:
            rec.write({'quickbooks_id': False})

        payment_term_records = self.env['account.payment.term'].search([])
        for rec in payment_term_records:
            rec.write({'quickbooks_id': False})

        tax_records = self.env['account.tax'].search([])
        for rec in tax_records:
            rec.write({'quickbooks_id': False})

        payment_method_records = self.env['qbd.payment.method'].search([])
        for rec in payment_method_records:
            rec.write({'quickbooks_id': False})

        purchase_order_records = self.env['purchase.order'].search([])
        for rec in purchase_order_records:
            rec.write({'quickbooks_id': False})

        self.search([]).write({
            'last_imported_qbd_id_for_account': False,
            'last_imported_qbd_id_for_payment_methods': False,
            'last_imported_qbd_id_for_partners': False,
            'last_imported_qbd_id_for_vendors': False,
            'last_imported_qbd_id_for_product': False,
            'last_imported_qbd_id_for_sale_orders': False,
            'last_imported_qbd_id_for_invoice': False,
            'last_imported_qbd_id_for_payments': False,
            'last_imported_qbd_id_for_purchase_orders': False,
        })

        return self.sendMessage({'Message': "Quickbooks Id and import datetime removed from all master successfully !!"})

###########  Import ###############

    # @api.multi
    def import_partner_title(self,logger_obj):
        try:
            headers = {'content-type': "application/json"}
            response = requests.request('GET', self.url + '/import_partner_title', headers=headers, verify=False)
            title_data = response.text

            if title_data:
                data = ast.literal_eval(title_data)
                if 'Status' in data:
                    if data.get('Status') == 404:
                        logger_obj.create({'message':'Connected to Script, but Connection to Quickbooks Unsuccessful !!', 'type':'Importing Customer Title', 'date':datetime.now()})
                    else:
                        is_imported = self.env['res.partner.title'].import_partner_title(data)
                else:
                    is_imported = self.env['res.partner.title'].import_partner_title(data)

            # return self.sendMessage({'Message':"Data imported Successful !!"})

        except ConnectionError as ce:
            logger_obj.create({'message': 'Connection Failed with the Host', 'type': 'Importing Customer Title', 'date': datetime.now()})
        except Exception as e:
            logger_obj.create({'message': e, 'type': 'Importing Customer Title', 'date': datetime.now()})

    # @api.multi
    def import_partner_category(self,logger_obj):
        try:
            headers = {'content-type': "application/json"}
            response = requests.request('GET', self.url + '/import_partner_category', headers=headers, verify=False)
            partner_category_data = response.text

            if partner_category_data:
                data = ast.literal_eval(partner_category_data)
                if 'Status' in data:
                    if data.get('Status') == 404:
                        logger_obj.create({'message':'Connected to Script, but Connection to Quickbooks Unsuccessful !!', 'type':'Importing Customer Category', 'date':datetime.now()})
                    else:
                        is_imported = self.env['res.partner.category'].import_vendor_customer_category(data,'customer')
                else:
                    is_imported = self.env['res.partner.category'].import_vendor_customer_category(data,'customer')
        # return self.sendMessage({'Message':"Data imported Successful !!"})

        except ConnectionError as ce:
            logger_obj.create({'message': 'Connection Failed with the Host', 'type': 'Importing Customer Category', 'date': datetime.now()})
        except Exception as e:
            logger_obj.create({'message': e, 'type': 'Importing Customer Category', 'date': datetime.now()})

    # @api.multi
    def import_vendor_category(self,logger_obj):
        try:
            headers = {'content-type': "application/json"}
            response = requests.request('GET', self.url + '/import_vendor_category', headers=headers, verify=False)
            vendor_category_data = response.text

            if vendor_category_data:
                data = ast.literal_eval(vendor_category_data)
                if 'Status' in data:
                    if data.get('Status') == 404:
                        logger_obj.create({'message': 'Connected to Script, but Connection to Quickbooks Unsuccessful !!', 'type': 'Importing Vendor Category', 'date':datetime.now()})
                    else:
                        is_imported = self.env['res.partner.category'].import_vendor_customer_category(data,'vendor')
                else:
                    is_imported = self.env['res.partner.category'].import_vendor_customer_category(data,'vendor')

            # return self.sendMessage({'Message': "Data imported Successful !!"})

        except ConnectionError as ce:
            logger_obj.create({'message': 'Connection Failed with the Host', 'type': 'Importing Vendor Category', 'date': datetime.now()})
        except Exception as e:
            logger_obj.create({'message': e, 'type': 'Importing Vendor Category', 'date': datetime.now()})

    # @api.multi
    def import_payment_terms(self,logger_obj):
        try:
            headers = {'content-type': "application/json"}
            response = requests.request('GET', self.url + '/import_payment_terms', headers=headers, verify=False)
            terms_data = response.text

            if terms_data:
                data = ast.literal_eval(terms_data)
                if 'Status' in data:
                    if data.get('Status') == 404:
                        logger_obj.create({'message': 'Connected to Script, but Connection to Quickbooks Unsuccessful !!', 'type': 'Importing Payment Terms', 'date':datetime.now()})
                    else:
                        is_imported = self.env['account.payment.term'].import_payment_terms(data)
                else:
                    is_imported = self.env['account.payment.term'].import_payment_terms(data)

            # return self.sendMessage({'Message':"Data imported Successful !!"})
        except ConnectionError as ce:
            logger_obj.create({'message': 'Connection Failed with the Host', 'type': 'Importing Payment Terms', 'date': datetime.now()})
        except Exception as e:
            logger_obj.create({'message': e, 'type': 'Importing Payment Terms', 'date': datetime.now()})



    # @api.multi
    def import_sales_tax(self,logger_obj):
        try:
            headers = {'content-type': "application/json"}
            response = requests.request('GET', self.url + '/import_sales_tax', headers=headers, verify=False)
            sales_tax_data = response.text

            if sales_tax_data:
                data = ast.literal_eval(sales_tax_data)
                if 'Status' in data:
                    if data.get('Status') == 404:
                        logger_obj.create({'message': 'Connected to Script, but Connection to Quickbooks Unsuccessful !!', 'type': 'Importing Sales Tax', 'date':datetime.now()})
                    else:
                        is_imported = self.env['account.tax'].import_sales_tax(data)
                else:
                    is_imported = self.env['account.tax'].import_sales_tax(data)

            # return self.sendMessage({'Message':"Data imported Successful !!"})

        except ConnectionError as ce:
            logger_obj.create({'message': 'Connection Failed with the Host', 'type': 'Importing Sales Tax', 'date': datetime.now()})
        except Exception as e:
            logger_obj.create({'message': e, 'type': 'Importing Sales Tax', 'date': datetime.now()})

    # @api.multi
    def import_tax_code(self,logger_obj):
        try:
            headers = {'content-type': "application/json"}
            response = requests.request('GET', self.url + '/import_tax_code', headers=headers, verify=False)
            tax_code_data = response.text

            if tax_code_data:
                data = ast.literal_eval(tax_code_data)
                if 'Status' in data:
                    if data.get('Status') == 404:
                        logger_obj.create(
                            {'message': 'Connected to Script, but Connection to Quickbooks Unsuccessful !!', 'type': 'Importing Tax Code', 'date':datetime.now()})
                    else:
                        is_imported = self.env['qbd.tax.code'].import_tax_code(data)
                else:
                    is_imported = self.env['qbd.tax.code'].import_tax_code(data)

            # return self.sendMessage({'Message':"Data imported Successful !!"})

        except ConnectionError as ce:
            logger_obj.create({'message': 'Connection Failed with the Host', 'type': 'Importing Tax Code', 'date': datetime.now()})
        except Exception as e:
            logger_obj.create({'message': e, 'type': 'Importing Tax Code', 'date': datetime.now()})

    def import_accounts(self):
        logger_obj = self.env['qbd.connection.logger'].sudo()
        try:
            headers = {'content-type': "application/json"}
            is_imported = False
            to_execute_account = 1
            accounts_data = []
            company = self.env['res.users'].search([('id', '=', 2)]).company_id
            if company.import_acc_limit:
                limit = company.import_acc_limit
            else:
                limit = 0
            if not self.last_imported_qbd_id_for_account:
                params = {'to_execute_account': 1, 'function_name': 'import_accounts', 'limit': limit}
                try:
                    response = requests.request('GET', self.url + '/import_account', params=params, headers=headers,
                                            verify=False)
                except Exception as e:
                    raise Warning(e)
                formatted_data = ast.literal_eval(response.text)
            else:
                last_qbd_id = self.last_imported_qbd_id_for_account
                params = {'to_execute_account': 2, 'last_qbd_id': last_qbd_id, 'function_name': 'import_accounts', 'limit': limit}
                try:
                    response = requests.request('GET', self.url + '/import_account', params=params, headers=headers,
                                            verify=False)
                except ConnectionError as e:
                    logger_obj.create({'message': 'Connection Failed with the Host', 'type': 'Importing Accounts', 'date': datetime.now()})
                    return self.sendMessage({'Message': "Connection Failed with the Host !!"})
                except Exception as e:
#                     logger_obj.create({'message': e, 'type': 'Importing Accounts', 'date': datetime.now()})
                    _logger.error('Exception : {}'.format(str(e)))
                formatted_data = ast.literal_eval(response.text)
            if formatted_data:
                is_imported = self.env['account.account'].create_accounts(formatted_data)
                if is_imported:
                    pass
            return self.sendMessage({'Message': "Data imported Successful !!"})
        except ConnectionError as ce:
            logger_obj.create({'message': 'Connection Failed with the Host', 'type': 'Importing Accounts', 'date': datetime.now()})
            return self.sendMessage({'Message': "Connection Failed with the Host !!"})
        except Exception as e:
#             logger_obj.create({'message': str(e), 'type': 'Importing Accounts', 'date': datetime.now()})
            _logger.error('Exception : {}'.format(str(e)))

    # @api.multi
    def import_product(self):
        headers = {'content-type': "application/json"}
        is_imported = False
        to_execute_account = 1
        products_data = []
        formatted_data = []

        company = self.env['res.users'].search([('id', '=', 2)]).company_id
        if company.import_pro_limit:
            limit = company.import_pro_limit
        else:
            limit = 0

        if not self.last_imported_qbd_id_for_product:
            params = {'to_execute_account': 1, 'function_name': 'import_products', 'limit': limit}
#             print("\n\n im port product before response")
            try:
                response = requests.request('GET', self.url + '/import_products', params=params, headers=headers,
                                        verify=False)
            except Exception as e:
                raise Warning(e)

#             print("\n\n im port account after response",response.text)

            formatted_data = ast.literal_eval(response.text)

        else:
            last_qbd_id = self.last_imported_qbd_id_for_product
            params = {'to_execute_account': 2, 'last_qbd_id': last_qbd_id, 'function_name': 'import_products', 'limit': limit}
            try:
                response = requests.request('GET', self.url + '/import_products', params=params, headers=headers,
                                        verify=False)
            except Exception as e:
                raise Warning(e)

            formatted_data = ast.literal_eval(response.text)

        if formatted_data:
            is_imported = self.env['product.product'].create_products(formatted_data)

        return self.sendMessage({'Message': "Data imported Successful !!"})


    # @api.multi
    def import_payment_methods(self):
        is_imported = False

        headers = {'content-type': "application/json"}
        params = {'fetch_record': 'all',}
#         print('\n\nRequest !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1 \n\n')
        response = requests.request('GET', self.url + '/import_payments_method',
                                    params=params,
                                    headers=headers, verify=False)

        payment_method_data = ast.literal_eval(response.text)
#         print("\n\nPayment Method data : ",payment_method_data[1])
        if payment_method_data[1]:
           is_imported = self.env['qbd.payment.method'].create_qbd_payment_methods(ast.literal_eval(payment_method_data[1]))

        # if is_imported:
        #     self.write({'last_imported_date_of_payment_methods': datetime.now()})

        return self.sendMessage({'Message':"Data imported Successful !!"})

    # @api.multi
    def import_partner(self):
        is_imported = False
        headers = {'content-type': "application/json"}
        to_execute_account = 1
        formatted_data = []
        partner_data = []
        company = self.env['res.users'].search([('id', '=', 2)]).company_id
        if company.import_cus_limit:
            limit = company.import_cus_limit
        else:
            limit = 0

        if not self.last_imported_qbd_id_for_partners:
            params = {'to_execute_account': 1,'fetch_record': 'all', 'limit': limit}

            try:
                response = requests.request('GET', self.url + '/import_customer', params=params, headers=headers,
                                        verify=False)
            except Exception as e:
                raise Warning(e)

            formatted_data = ast.literal_eval(response.text)

        else:
            last_qbd_id = self.last_imported_qbd_id_for_partners
            params = {'to_execute_account': 2,'fetch_record': 'all', 'last_qbd_id': last_qbd_id, 'limit': limit}

            try:
                response = requests.request('GET', self.url + '/import_customer', params=params, headers=headers,
                                        verify=False)
            except Exception as e:
                raise Warning(e)

            formatted_data = ast.literal_eval(response.text)

        if formatted_data:
            is_imported = self.env['res.partner'].create_customers(formatted_data)

        if is_imported:
            return self.sendMessage({'Message': "Data imported Successful !!"})

        return self.sendMessage(response)

    # import Vendors
    # @api.multi
    def import_vendor(self):
#         print('\n\nImport Vendor method calleeddddd\n\n')
        is_imported = False
        headers = {'content-type': "application/json"}
        to_execute_account = 1
        vendor_data = []
        formatted_data = []

        company = self.env['res.users'].search([('id', '=', 2)]).company_id
        if company.import_ven_limit:
            limit = company.import_ven_limit
        else:
            limit = 0

        if not self.last_imported_qbd_id_for_vendors:
            params = {'to_execute_account': 1, 'function_name': 'import_vendors', 'limit':limit}

            try:
                response = requests.request('GET', self.url + '/import_vendor', params=params, headers=headers,
                                        verify=False)
            except Exception as e:
                raise Warning(e)

            formatted_data = ast.literal_eval(response.text)

        else:
            last_qbd_id = self.last_imported_qbd_id_for_vendors
            params = {'to_execute_account': 2, 'last_qbd_id': last_qbd_id, 'function_name': 'import_vendors', 'limit':limit}

            try:
                response = requests.request('GET', self.url + '/import_vendor', params=params, headers=headers,
                                        verify=False)
            except Exception as e:
                raise Warning(e)

            formatted_data = ast.literal_eval(response.text)

#             print ('formated data:  ::',formatted_data)

        if formatted_data:
            is_imported = self.env['res.partner'].create_vendors(formatted_data)

        if is_imported:
            return self.sendMessage({'Message': "Data imported Successful !!"})

        return self.sendMessage(response)

    # @api.multi
    def import_order(self):
        is_imported = False
        to_execute_account = 1
        headers = {'content-type': "application/json"}
        sale_order_data = []
        formatted_data = []

        company = self.env['res.users'].search([('id', '=', 2)]).company_id
        if company.import_so_limit:
            limit = company.import_so_limit
        else:
            limit = 0

        if not self.last_imported_qbd_id_for_sale_orders:
            params = {'to_execute_account': 1, 'fetch_record': 'all', 'limit': limit}
            try:
                response = requests.request('GET', self.url + '/import_sales_order', params=params, headers=headers,
                                        verify=False)
            except Exception as e:
                raise Warning(e)
#             print('\n\nResponse ::', response.text)
            formatted_data = ast.literal_eval(response.text)

        else:
            last_qbd_id = self.last_imported_qbd_id_for_sale_orders
            params = {'to_execute_account': 2,'last_qbd_id': last_qbd_id, 'fetch_record': 'all', 'limit':limit}
            try:
                response = requests.request('GET', self.url + '/import_sales_order', params=params, headers=headers,
                                        verify=False)
            except Exception as e:
                raise Warning(e)
#             print('\n\nResponse ::', response.text)
            formatted_data = ast.literal_eval(response.text)

        if formatted_data:
            is_imported = self.env['sale.order'].create_sale_orders(formatted_data)

        if is_imported:
            pass

        return self.sendMessage({'Message': "Data imported Successful !!"})

    # @api.multi
    def import_invoice(self):
        is_imported = False
#         print("\n\n in invoice method")
        headers = {'content-type': "application/json"}
        invoice_data = []
        to_execute_account = 1
        formatted_data = []

        company = self.env['res.users'].search([('id', '=', 2)]).company_id
        if company.import_inv_limit:
            limit = company.import_inv_limit
        else:
            limit = 0

        if not self.last_imported_qbd_id_for_invoice:
            params = {'to_execute_account':1,'fetch_record': 'all', 'limit': limit}
            try:
                response = requests.request('GET', self.url + '/import_invoice', params=params, headers=headers,
                                        verify=False)
            except Exception as e:
                raise Warning(e)
            formatted_data = ast.literal_eval(response.text)

        else:
            last_qbd_id = self.last_imported_qbd_id_for_invoice
            params = {'to_execute_account':2,'last_qbd_id':last_qbd_id,'fetch_record': 'all', 'limit': limit}
            try:
                response = requests.request('GET', self.url + '/import_invoice', params=params, headers=headers,
                                        verify=False)
            except Exception as e:
                raise Warning(e)

            formatted_data = ast.literal_eval(response.text)

        if formatted_data:
            is_imported = self.env['account.move'].create_invoice(formatted_data)

        if is_imported:
            pass

        return self.sendMessage({'Message': "Data imported Successful !!"})


    # @api.multi
    def import_payments(self):
        is_imported = False
        headers = {'content-type': "application/json"}
        to_execute_account = 1
        payment_data = []

        company = self.env['res.users'].search([('id', '=', 2)]).company_id
        if company.import_pay_limit:
            limit = company.import_pay_limit
        else:
            limit = 0

        if not self.last_imported_qbd_id_for_payments:
            params = {'to_execute_account':1,'fetch_record': 'all', 'limit': limit}
#             print('\n\nRequest in Payment !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1 \n\n')
            try:
                response = requests.request('GET', self.url + '/import_payments', params=params, headers=headers,
                                        verify=False)
            except Exception as e:
                raise Warning(e)

            payment_data = ast.literal_eval(response.text)
            # last_qbd_id = payment_data[0]

        else:
            last_qbd_id = self.last_imported_qbd_id_for_payments
            params = {'to_execute_account': 2,'last_qbd_id':last_qbd_id, 'fetch_record': 'all', 'limit': limit}
#             print('\n\nRequest in Payment !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1 \n\n')
            try:
                response = requests.request('GET', self.url + '/import_payments', params=params, headers=headers,
                                        verify=False)
            except Exception as e:
                raise Warning(e)

            payment_data = ast.literal_eval(response.text)

        if payment_data:
            is_imported = self.env['account.payment'].create_payments(payment_data)

        if is_imported:
            pass

        return self.sendMessage({'Message': "Data imported Successful !!"})

    # @api.multi
    def import_purchase_orders(self):
        is_imported = False
        to_execute_account = 1
        headers = {'content-type': "application/json"}
        purchase_order_data = []
        formatted_data = []

        company = self.env['res.users'].search([('id', '=', 2)]).company_id
        if company.import_po_limit:
            limit = company.import_po_limit
        else:
            limit = 0

        if not self.last_imported_qbd_id_for_purchase_orders:
            params = {'to_execute_account':1,'fetch_record': 'all', 'limit': limit}
            try:
                response = requests.request('GET', self.url + '/import_purchase_order', params=params, headers=headers,
                                        verify=False)
            except Exception as e:
                raise Warning(e)
#             print('\n\nResponse ::', response.text)
            formatted_data = ast.literal_eval(response.text)

        else:
            last_qbd_id = self.last_imported_qbd_id_for_purchase_orders
            params = {'to_execute_account':2,'last_qbd_id': last_qbd_id,'fetch_record': 'all', 'limit':limit}
            try:
                response = requests.request('GET', self.url + '/import_purchase_order', params=params, headers=headers,
                                        verify=False)
            except Exception as e:
                raise Warning(e)
#             print('\n\nResponse ::', response.text)

            formatted_data = ast.literal_eval(response.text)

        if formatted_data:
            is_imported = self.env['purchase.order'].create_purchase_orders(formatted_data)

        if is_imported:
            pass

        return self.sendMessage({'Message': "Data imported Successful !!"})


###########  Export ###############
    # @api.multi
    def export_masters(self):
        self.export_accounts()
        self.export_partners()
        self.export_vendors()
        self.export_products()
        return self.sendMessage({'Message': "Check Connection, Duplicate and Export Loggers to verify whether data was exported to quickbooks !!"})

    # @api.multi
    def export_accounts(self):
        logger_obj = self.env['qbd.connection.logger']

        try:
#             print('\n\n!!!!!Export Accounts !!!!\n\n')
            is_exported = False

            is_exported = self.env['account.account'].export_accounts()

            return self.sendMessage({'Message': "Data Exported Successful !!"})

        except ConnectionError as ce:
            logger_obj.create({'message': 'Connection Failed with the Host', 'type': 'Exporting Accounts', 'date': datetime.now()})
            return self.sendMessage({'Message': "Connection Failed with the Host !!"})
        except Exception as e:
            logger_obj.create({'message': e, 'type': 'Exporting Accounts', 'date': datetime.now()})
            return self.sendMessage({'Message': e})

    # @api.multi
    def export_partners(self):
#         print('\n\n!!!!!Export Partners !!!!\n\n')
        self.check_duplicates()
        records = self.env['qbd.duplicates.logger'].search([('type', '=', 'customer')])
#         print ("Records -----------",records)
        if not records:
            is_exported = False
            is_exported = self.env['res.partner'].export_partners()
            return self.sendMessage({'Message': "Data Exported Successful !!"})

        else:
            return self.sendMessage({'Message': "Please Check Loggers !!"})

    # @api.multi
    def export_vendors(self):
#         print('\n\n!!!!!Export Vendors !!!!\n\n')
        self.check_duplicates()
        records = self.env['qbd.duplicates.logger'].search([('type', '=', 'vendor')])

        if not records:
            is_exported = False
            is_exported = self.env['res.partner'].export_vendors()
            return self.sendMessage({'Message': "Data Exported Successful !!"})

        else:
            return self.sendMessage({'Message': "Please Check Loggers !!"})

    # @api.multi
    def export_products(self):
#         print('\n\n!!!!!Export Products !!!!\n\n')
        self.check_duplicates()
        records = self.env['qbd.duplicates.logger'].search([('type', '=', 'product')])
        print("\n\n\n\nrecords",records)
        if not records:
            is_exported = False
            is_exported = self.env['product.product'].export_products()
            return self.sendMessage({'Message': "Data Exported Successful !!"})

        else:
            return self.sendMessage({'Message': "Please Check Loggers !!"})

    # @api.multi
    def export_sale_orders(self):
#         print('\n\n!!!!!Export Sale Orders !!!!\n\n')
        is_exported = False

        is_exported = self.env['sale.order'].export_sale_orders()

        return self.sendMessage({'Message': "Data Exported Successful !!"})

    # @api.multi
    def export_invoices(self):
#         print('\n\n!!!!!Export Invoices !!!!\n\n')
        is_exported = False

        is_exported = self.env['account.move'].export_invoices()

        return self.sendMessage({'Message': "Data Exported Successful !!"})

    # @api.multi
    def export_purchase_order(self):
#         print('\n\n!!!!!Export Purchase Order !!!!\n\n')
        is_exported = False

        is_exported = self.env['purchase.order'].export_purchase_order()

        return self.sendMessage({'Message': "Data Exported Successful !!"})

    # @api.multi
    def export_payments(self):
#         print('Export Payments !!!!!! 11111111111111')
        is_exported = False

        is_exported = self.env['account.payment'].export_payments()

        return self.sendMessage({'Message': "Data Exported Successful !!"})


    ##### cron job #####

    # import crons

    @api.model
    def import_accounts_cron(self):
#         print('\n\n---Import Accounts Schedular Calleeeeed---\n\n',self)
        company = self.env.user.company_id
#         print('Comapny : ',company)
        company.import_accounts()


    @api.model
    def import_partners_cron(self):
#         print('\n\n---Import Partners Schedular Calleeeeed---\n\n', self)
        company = self.env.user.company_id
#         print('Comapny : ', company)
        company.import_partner()

    @api.model
    def import_vendors_cron(self):
#         print('\n\n---Import Vendors Schedular Calleeeeed---\n\n', self)
        company = self.env.user.company_id
#         print('Comapny : ', company)
        company.import_vendor()


    @api.model
    def import_products_cron(self):
#         print('\n\n---Import Products Schedular Calleeeeed---\n\n', self)
        company = self.env.user.company_id
#         print('Comapny : ', company)
        company.import_product()

    @api.model
    def import_sale_order_cron(self):
#         print('\n\n---Import Sale Orders Schedular Calleeeeed---\n\n', self)
        company = self.env.user.company_id
#         print('Comapny : ', company)
        company.import_order()

    @api.model
    def import_purchase_order_cron(self):
#         print('\n\n---Import Purchase Orders Schedular Calleeeeed---\n\n', self)
        company = self.env.user.company_id
#         print('Comapny : ', company)
        company.import_purchase_orders()

    @api.model
    def import_invoices_cron(self):
#         print('\n\n---Import Invoices Schedular Calleeeeed---\n\n')
        company = self.env.user.company_id
#         print('Comapny : ', company)
        company.import_invoice()

    @api.model
    def import_payments_cron(self):
#         print('\n\n---Import Payments Schedular Calleeeeed---\n\n')
        company = self.env.user.company_id
#         print('Comapny : ', company)
        company.import_payments()

    ## Export crons

    @api.model
    def export_accounts_cron(self):
#         print('\n\n--- Export Accounts Schedular ---\n\n')
        company = self.env.user.company_id
#         print('Comapny : ', company)
        company.export_accounts()

    @api.model
    def export_partners_cron(self):
#         print('\n\n--- Export Partners Schedular ---\n\n')
        company = self.env.user.company_id
#         print('Comapny : ', company)
        company.export_partners()

    @api.model
    def export_vendors_cron(self):
#         print('\n\n--- Export Vendors Schedular ---\n\n')
        company = self.env.user.company_id
#         print('Comapny : ', company)
        company.export_vendors()

    @api.model
    def export_products_cron(self):
#         print('\n\n--- Export Products Schedular ---\n\n')
        company = self.env.user.company_id
#         print('Comapny : ', company)
        company.export_products()

    @api.model
    def export_sale_orders_cron(self):
#         print('\n\n--- Export Sale Orders Schedular ---\n\n')
        company = self.env.user.company_id
#         print('Comapny : ', company)
        company.export_sale_orders()

    @api.model
    def export_purchase_orders_cron(self):
#         print('\n\n--- Export Purchase Orders Schedular ---\n\n')
        company = self.env.user.company_id
#         print('Comapny : ', company)
        company.export_purchase_order()

    @api.model
    def export_invoices_cron(self):
#         print('\n\n--- Export Invoices Schedular ---\n\n')
        company = self.env.user.company_id
#         print('Comapny : ', company)
        company.export_invoices()

    @api.model
    def export_payments_cron(self):
#         print('\n\n--- Export Payments Schedular ---\n\n')
        company = self.env.user.company_id
#         print('Comapny : ', company)
        company.export_payments()







