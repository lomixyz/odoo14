from flask import Blueprint, request
from connection import connect_to_qbd,close_connection_to_qbd
import logging
logging.basicConfig(level=logging.DEBUG)

payments = Blueprint('payments', __name__, template_folder='templates')

'''
TPA - Third Party Application
'''
@payments.route('/QBD/import_payments')
def import_QBD_payments_to_TPA():
    try:
        data = connect_to_qbd()
        con = data[0]
        cursor = con.cursor()

        to_execute_account = int(request.args.get('to_execute_account'))
        limit = int(request.args.get('limit'))        

        if to_execute_account == 1:
            payments = "SELECT TOP {} CustomerRefListID, ARAccountRefListID, TxnDate, TotalAmount, PaymentMethodRefFullName, Memo, TxnId, RefNumber, TimeModified FROM ReceivePayment Order by timemodified asc".format(limit)
            cursor.execute(payments)

        elif to_execute_account == 2:
            time_modified = "{ts'"+str(request.args.get('last_qbd_id'))+"'}" 
            # print (time_modified)
            payments = "SELECT TOP {} CustomerRefListID, ARAccountRefListID, TxnDate, TotalAmount, PaymentMethodRefFullName, Memo, TxnId, RefNumber, TimeModified FROM ReceivePayment where timemodified >={}".format(limit, time_modified)
            cursor.execute(payments)

        # elif request.args['fetch_record'] == 'one':
        #     ListId = request.args['quickbooks_id']
        #     cursor.execute("SELECT ListId, ParentRefListId, FullName, Email, Phone, AltPhone, Fax, Notes, BillAddressAddr1, BillAddressAddr2, BillAddressCountry, BillAddressState, BillAddressCity, BillAddressPostalCode FROM Customer Where ListID='"+ListId+"' Order by ListId ASC")

        odoo_payment_list = []
        
        for row in cursor.fetchall():
            odoo_payment_dict = {}
            row_as_list = [x for x in row]

            odoo_payment_dict = {}
            odoo_payment_dict['partner_name'] = row_as_list[0]
            #Search partner_name in res.partner with field quickbooks_id to get odoo_id and store this in field partner_id 

            odoo_payment_dict['payment_method_name'] = row_as_list[4]
            odoo_payment_dict['date'] = str(row_as_list[2])
            odoo_payment_dict['partner_type'] = 'customer'
            odoo_payment_dict['state'] = 'posted'
            odoo_payment_dict['payment_type'] = 'inbound'
            odoo_payment_dict['journal_id'] = '9' #jounal id of bank is 7
            odoo_payment_dict['communication'] = str(row_as_list[5])
            odoo_payment_dict['quickbooks_id'] = str(row_as_list[6])
            odoo_payment_dict['amount'] = str(row_as_list[3])
            if row_as_list[7]:
                odoo_payment_dict['payment_ref_number'] = str(row_as_list[7])
            else:
                odoo_payment_dict['payment_ref_number'] = '' 
            odoo_payment_dict['last_time_modified'] = str(row_as_list[8])

            # Last_QBD_id = str(row_as_list[8])
            odoo_payment_list.append(odoo_payment_dict)
            
        # print (odoo_payment_list)

        cursor.close()
        return (str(odoo_payment_list))
        
    except Exception as e:
        # print (e)
        data = 0
        return ({"Status": 404, "Message":"Please wait for sometime and check whether Quickbooks Desktop and Command Prompt are running as adminstrator."})

    finally:
        if data != 0:
            close_connection_to_qbd(data[0])

@payments.route('/QBD/export_payments', methods=['POST'])
def export_TPA_payments_to_QBD():
    try:
        data = connect_to_qbd()
        con = data[0]
        cursor = con.cursor()

        req = request.get_json(force=True)
        # print (req)
        if 'payments_list' in req:

            tpa_payments_list = []
            for rec in req.get('payments_list'):
                # print (rec)

                tpa_payments_dict={}
                
                customer_quickbooks_id = rec.get('partner_name')
                # ara_account_quickbooks_id = '40000-933270541'
                payment_quickbooks_id = rec.get('payment_method_name')
                payment_date = "{d'"+rec.get('date')+"'}" 
                if rec.get('amount'):
                    paid_amount = float(rec.get('amount'))
                else:
                    paid_amount = float(0.0)
                is_auto_apply = str(True)
                if rec.get('communication'):
                    memo = rec.get('communication')
                else:
                    memo = ''

                ref_number = rec.get('ref_number')

                if rec.get('invoice_quickbooks_number'):
                    inv_qb_id = rec.get('invoice_quickbooks_number')
                else:
                    inv_qb_id = False

                if ref_number:
                    check_record ="Select Top 1 TxnId,RefNumber,TimeModified from ReceivePayment where RefNumber='{}'".format(ref_number)

                cursor.execute(check_record)
                is_present = cursor.fetchone()

                # insertQuery = "INSERT INTO ReceivePaymentLine (CustomerRefListID, ARAccountRefListID, PaymentMethodRefListID, TotalAmount, IsAutoApply) VALUES ('{}' ,'{}' ,'{}' ,{} ,{})".format(customer_quickbooks_id, ara_account_quickbooks_id, payment_quickbooks_id, paid_amount, is_auto_apply)
                if is_present: 
                    logging.info("Record Already Present in Quickbboks so updating id in Odoo ----------------------------- ")
                    logging.info(check_record)
                    logging.info(is_present[0])

                    tpa_payments_dict['odoo_id'] = rec.get('odoo_id')
                    tuple_data = cursor.fetchone()
                    tpa_payments_dict['quickbooks_id'] = is_present[0] 
                    tpa_payments_dict['message'] = 'Quickbooks Id Successfully Added'
                    tpa_payments_dict['last_modified_date'] = str(is_present[2])

                    tpa_payments_list.append(tpa_payments_dict)
                    cursor.commit()


                elif not is_present:
                    if inv_qb_id:
                        insertQuery = "INSERT INTO ReceivePaymentLine (CustomerRefListID, PaymentMethodRefListID, TotalAmount, Memo, TxnDate, RefNumber, AppliedToTxnTxnId, AppliedToTxnPaymentAmount) VALUES ('{}', '{}' , {}, '{}', {}, '{}', '{}', {})".format(customer_quickbooks_id, payment_quickbooks_id, paid_amount, memo, payment_date, ref_number, inv_qb_id, paid_amount)
                    else:
                        insertQuery = "INSERT INTO ReceivePaymentLine (CustomerRefListID, PaymentMethodRefListID, TotalAmount, IsAutoApply, Memo, TxnDate, RefNumber) VALUES ('{}', '{}' ,{} , {}, '{}', {}, '{}')".format(customer_quickbooks_id, payment_quickbooks_id, paid_amount, is_auto_apply, memo, payment_date, ref_number)

                    # print ("--------------")
                    # print (insertQuery)
                    try:
                        logging.info("Insert Query ----------------------------- ")
                        logging.info(insertQuery)
                        cursor.execute(insertQuery)
                        logging.info("Insert Query ----------------------------- ")

                    except Exception as e:
                        logging.info("1")
                        logging.warning(e)
                        # print(e)
                        tpa_payments_dict['odoo_id'] = rec.get('odoo_id')
                        tpa_payments_dict['quickbooks_id'] = ''
                        tpa_payments_dict['message'] = 'Error While Creating'
                        pass

                if not is_present:
                    if ref_number:
                        lastInserted ="Select Top 1 TxnId,RefNumber from ReceivePayment where RefNumber='{}'".format(ref_number)
                        cursor.execute(lastInserted)
                        
                        tpa_payments_dict['odoo_id'] = rec.get('odoo_id')
                        tuple_data = cursor.fetchone()
                        tpa_payments_dict['quickbooks_id'] = tuple_data[0] 
                        tpa_payments_dict['message'] = 'Successfully Created'
                            
                        tpa_payments_list.append(tpa_payments_dict)
                        cursor.commit()
                
                    else:
                        tpa_payments_dict['odoo_id'] = rec.get('odoo_id')
                        tpa_payments_dict['quickbooks_id'] = 'Payment Reference not found'
                        tpa_payments_dict['message'] = 'Successfully Created'
                            
                        tpa_payments_list.append(tpa_payments_dict)
                        cursor.commit()

            # print(tpa_payments_list)
            cursor.close()

            return (str([{"Data":tpa_payments_list}]))
        
        return (str([{"Data":[]}]))

    except Exception as e:
        logging.info("2")
        logging.warning(e)        
        # print (e)
        data = 0
        return ({"Status": 404, "Message":"Please wait for sometime and check whether Quickbooks Desktop and Command Prompt are running as adminstrator."})

    finally:
        if data != 0:
            close_connection_to_qbd(data[0])
