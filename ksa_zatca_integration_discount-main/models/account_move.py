from cryptography.hazmat.backends import default_backend
from odoo import api, fields, models, exceptions, tools, _
from cryptography import x509
from odoo.tools.float_utils import float_round
from odoo.tools import mute_logger
import lxml.etree as ET
import binascii
import requests
import logging
import hashlib
import base64
import uuid
import json
import math
import re
import os
from collections import defaultdict


phase_1_ending_date = fields.datetime.strptime("1/jan/2000", "%d/%b/%Y").date() # last day for phase 1 invoices.

_logger = logging.getLogger(__name__)
_zatca = logging.getLogger('Zatca Debugger for account.move :')
message = "Based on the VAT regulation, after issuing an invoice, it is prohibited to " \
          "modify or cancel the invoice. and according the regulation, a debit/credit " \
          "notes must be generated to modify or cancel the generated invoice. Therefore" \
          " the supplier should issue an electronic credit/debit note linked to the original." \
          " modified invoice"

class AccountMove(models.Model):
    _inherit = "account.move"

    discount_jasara = fields.Float()
    amount_total = fields.Monetary(string='Total', store=True, readonly=True,
                                   compute='_compute_amount',
                                   inverse='_inverse_amount_total')

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id', 'discount_jasara')
    def _compute_amount(self):
        in_invoices = self.filtered(lambda m: m.move_type == 'in_invoice')
        out_invoices = self.filtered(lambda m: m.move_type == 'out_invoice')
        others = self.filtered(lambda m: m.move_type not in ('in_invoice', 'out_invoice'))
        reversed_mapping = defaultdict(lambda: self.env['account.move'])
        for reverse_move in self.env['account.move'].search([
            ('state', '=', 'posted'),
            '|', '|',
            '&', ('reversed_entry_id', 'in', in_invoices.ids), ('move_type', '=', 'in_refund'),
            '&', ('reversed_entry_id', 'in', out_invoices.ids), ('move_type', '=', 'out_refund'),
            '&', ('reversed_entry_id', 'in', others.ids), ('move_type', '=', 'entry'),
        ]):
            reversed_mapping[reverse_move.reversed_entry_id] += reverse_move

        caba_mapping = defaultdict(lambda: self.env['account.move'])
        caba_company_ids = self.company_id.filtered(lambda c: c.tax_exigibility)
        reverse_moves_ids = [move.id for moves in reversed_mapping.values() for move in moves]
        for caba_move in self.env['account.move'].search([
            ('tax_cash_basis_move_id', 'in', self.ids + reverse_moves_ids),
            ('state', '=', 'posted'),
            ('move_type', '=', 'entry'),
            ('company_id', 'in', caba_company_ids.ids)
        ]):
            caba_mapping[caba_move.tax_cash_basis_move_id] += caba_move

        for move in self:

            if move.payment_state == 'invoicing_legacy':
                # invoicing_legacy state is set via SQL when setting setting field
                # invoicing_switch_threshold (defined in account_accountant).
                # The only way of going out of this state is through this setting,
                # so we don't recompute it here.
                move.payment_state = move.payment_state
                continue

            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_to_pay = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = move._get_lines_onchange_currency().currency_id

            for line in move.line_ids:
                if move.is_invoice(include_receipts=True):
                    # === Invoices ===

                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        total_to_pay += line.balance
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.move_type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1
            move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
            move.amount_total = sign * (
                total_currency - move.discount_jasara if len(currencies) == 1 else total - move.discount_jasara)
            move.amount_residual = -sign * (total_residual_currency + move.discount_jasara if len(
                currencies) == 1 else total_residual + move.discount_jasara)
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(total) if move.move_type == 'entry' else - (
                    total - move.discount_jasara)
            print(move.amount_total_signed)
            move.amount_residual_signed = total_residual + move.discount_jasara
            print(move.amount_residual_signed)
            # print("1",total)
            # move.amount_total = sign * (total_currency + move.discount_jasara if len(currencies) == 1 else total + move.discount_jasara)
            # print('1',move.amount_total)
            # move.amount_residual = -sign * (total_residual_currency - move.discount_jasara if len(currencies) == 1 else total_residual - move.discount_jasara)
            # move.amount_untaxed_signed = -total_untaxed
            # move.amount_tax_signed = -total_tax
            # print("2",total)
            # move.amount_total_signed = abs(total + move.discount_jasara) if move.move_type == 'entry' else - (total + move.discount_jasara)
            # print('2',move.amount_total_signed)
            # move.amount_residual_signed = total_residual - move.discount_jasara

            currency = len(currencies) == 1 and currencies or move.company_id.currency_id

            # Compute 'payment_state'.
            new_pmt_state = 'not_paid' if move.move_type != 'entry' else False

            if move.is_invoice(include_receipts=True) and move.state == 'posted':

                if currency.is_zero(move.amount_residual):
                    reconciled_payments = move._get_reconciled_payments()
                    if not reconciled_payments or all(payment.is_matched for payment in reconciled_payments):
                        new_pmt_state = 'paid'
                    else:
                        new_pmt_state = move._get_invoice_in_payment_state()
                elif currency.compare_amounts(total_to_pay, total_residual) != 0:
                    new_pmt_state = 'partial'

            if new_pmt_state == 'paid' and move.move_type in ('in_invoice', 'out_invoice', 'entry'):
                reverse_moves = reversed_mapping[move]
                caba_moves = caba_mapping[move]
                for reverse_move in reverse_moves:
                    caba_moves |= caba_mapping[reverse_move]

                # We only set 'reversed' state in cas of 1 to 1 full reconciliation with a reverse entry; otherwise, we use the regular 'paid' state
                # We ignore potentials cash basis moves reconciled because the transition account of the tax is reconcilable
                reverse_moves_full_recs = reverse_moves.mapped('line_ids.full_reconcile_id')
                if reverse_moves_full_recs.mapped('reconciled_line_ids.move_id').filtered(lambda x: x not in (
                        caba_moves + reverse_moves + reverse_moves_full_recs.mapped('exchange_move_id'))) == move:
                    new_pmt_state = 'reversed'

            move.payment_state = new_pmt_state

    @mute_logger('Zatca Debugger for account.move :')
    def create_xml_file(self, previous_hash=0, pos_refunded_order_id=0):
        amount_verification = 0  # for debug mode
        conf = self.company_id.sudo()
        conf_company = self._get_zatca_company_data() if self.l10n_is_self_billed_invoice else self._get_zatca_partner_data()
        conf_partner = self._get_zatca_partner_data() if self.l10n_is_self_billed_invoice else self._get_zatca_company_data()
        if not conf.is_zatca:
            raise exceptions.AccessDenied(_("Zatca is not activated."))
        # No longer needed
        # if not previous_hash:
        #     self.create_xml_file(previous_hash=1)

        partner_id, company_id, buyer_identification, buyer_identification_no, license, license_no = self._get_partner_comapny()
        signature, signature_certificate, base_64_5 = self.get_signature()

        # UBL 2.1 sequence
        self.invoice_ksa_validations()
        l10n_sa_delivery_date = self.l10n_sa_delivery_date

        bt_3 = '383' if self.debit_origin_id.id else ('381' if self.move_type in ['out_refund', 'in_refund'] else '388')
        bt_25 = self.env['account.move']
        if bt_3 != '388':
            # if 'Shop' in self.ref:
            #     bt_25 = self.env['pos.order'].search([('account_move', '=', self.id)])
            #     bt_25_name = str(self.ref.replace(' REFUND', '')[0: len(self.ref.replace(' REFUND', ''))])
            #     bt_25 = self.env['pos.order'].search(
            #         [('name', '=', bt_25_name), ('session_id', '=', bt_25.session_id.id)]).account_move
            if pos_refunded_order_id:
                bt_25 = self.env['account.move'].browse(int(pos_refunded_order_id))
            else:
                bt_25 = self.reversed_entry_id or self.debit_origin_id
                if not self.ref or not bt_25.id:
                    raise exceptions.MissingError(_('Original Invoice Ref not found.'))
            if bt_25.l10n_sa_invoice_type != self.l10n_sa_invoice_type:
                self.l10n_sa_invoice_type = bt_25.l10n_sa_invoice_type
                raise exceptions.ValidationError(_("Mismatched Invoice Type for original and associated invoice."))

        # is_tax_invoice = 0 if 'O' in classified_tax_category_list or not len(classified_tax_category_list) else 1
        is_tax_invoice = 1 if self.l10n_sa_invoice_type == 'Standard' else 0
        if is_tax_invoice:
            self.tax_invoice_validations()

            if self.l10n_is_exports_invoice:
                partner_data = self._get_zatca_partner_data()
                partner_fields_ids = ['state_id']
                missing_partner_fields_ids = [partner_id._fields[partner_fields_id].string for partner_fields_id in
                                              partner_fields_ids if not partner_id[partner_fields_id]['id']]
                if len(missing_partner_fields_ids) > 0:
                    message = ' , '.join(missing_partner_fields_ids) + ' ' + _("are missing in Customer Address") + ', ' \
                              + _("which are required for tax invoices, in case of non-ksa resident.")
                    raise exceptions.ValidationError(message)

        if not is_tax_invoice and conf.csr_invoice_type[1:2] != '1':
            raise exceptions.AccessDenied(_("Certificate not allowed for Simplified Invoices."))

        self.invoice_uuid = self.invoice_uuid if self.invoice_uuid and self.invoice_uuid != '' else str(
            str(uuid.uuid4()))

        ksa_16 = int(conf.zatca_icv_counter)
        ksa_16 += 1
        conf.zatca_icv_counter = str(ksa_16)

        company_vat = 0

        # BR-KSA-26
        # ksa_13 = 0
        # ksa_13 = base64.b64encode(bytes(hashlib.sha256(str(ksa_13).encode('utf-8')).hexdigest(), encoding='utf-8')).decode('UTF-8')

        def get_pih(self, icv):
            try:
                pih = self.search([('zatca_icv_counter', '=', str(int(icv) - 1))])
                if icv < 0:
                    raise
                if not pih.id:
                    icv = icv - 1
                    pih = get_pih(self, icv)
            except:
                return False
            return pih

        pih = get_pih(self, ksa_16)
        self.zatca_icv_counter = str(ksa_16)
        ksa_13 = pih.zatca_invoice_hash if pih else 'NWZlY2ViNjZmZmM4NmYzOGQ5NTI3ODZjNmQ2OTZjNzljMmRiYzIzOWRkNGU5MWI0NjcyOWQ3M2EyN2ZiNTdlOQ=='
        # signature = 0 if is_tax_invoice else 1
        # BR-KSA-31 (KSA-2)
        ksa_2 = '01' if is_tax_invoice else '02'  # Simplified in case of tax category O
        ksa_2 += str(int(self.l10n_is_third_party_invoice))
        ksa_2 += str(int(self.l10n_is_nominal_invoice))
        # ksa_2 += str(int(self.l10n_is_exports_invoice))
        ksa_2 += "0" if not is_tax_invoice else str(int(self.l10n_is_exports_invoice))
        ksa_2 += str(int(self.l10n_is_summary_invoice))
        ksa_2 += "0" if self.l10n_is_exports_invoice or not is_tax_invoice else str(
            int(self.l10n_is_self_billed_invoice))

        document_currency = self.currency_id.name
        document_level_allowance_charge = 0
        vat_tax = 0
        bt_31 = company_id.vat
        bg_23_list = {}
        bt_92 = 0  # No document level allowance, in default odoo
        bt_106 = float(
            '{:0.2f}'.format(float_round(0, precision_rounding=0.01)))  # Sum of bt-131 Calculated in invoice line loop.
        bt_107 = float('{:0.2f}'.format(float_round(bt_92, precision_rounding=0.01)))
        delivery = 1
        not_know = 0
        ksa_note = 0
        # bt_81 = 10 if 'cash' else (30 if 'credit' else (42 if 'bank account' else (48 if 'bank card' else 1)))
        bt_81 = self.l10n_payment_means_code
        accounting_seller_party = 0
        self.zatca_unique_seq = self.name
        bt_1 = self.zatca_unique_seq
        ubl_2_1 = '''
            <Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
                     xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                     xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
                     xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2">'''
        # if not ksa_13 and signature:  # need to check this
        if signature and not previous_hash and not is_tax_invoice:
            ubl_2_1 += '''
                <ext:UBLExtensions>'''
            if signature:
                ubl_2_1 += '''
                    <ext:UBLExtension>
                        <ext:ExtensionURI>urn:oasis:names:specification:ubl:dsig:enveloped:xades</ext:ExtensionURI>
                        <ext:ExtensionContent>
                            <sig:UBLDocumentSignatures xmlns:sac="urn:oasis:names:specification:ubl:schema:xsd:SignatureAggregateComponents-2" 
                                                       xmlns:sbc="urn:oasis:names:specification:ubl:schema:xsd:SignatureBasicComponents-2"
                                                       xmlns:sig="urn:oasis:names:specification:ubl:schema:xsd:CommonSignatureComponents-2">
                                <sac:SignatureInformation>
                                    <cbc:ID>urn:oasis:names:specification:ubl:signature:1</cbc:ID>
                                    <sbc:ReferencedSignatureID>urn:oasis:names:specification:ubl:signature:Invoice</sbc:ReferencedSignatureID>
                                    <ds:Signature Id="signature" xmlns:ds="http://www.w3.org/2000/09/xmldsig#">'''
                ubl_2_1 += signature
                ubl_2_1 += signature_certificate
                ubl_2_1 += '''  </ds:Signature>
                                </sac:SignatureInformation>
                            </sig:UBLDocumentSignatures>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>      '''
            ubl_2_1 += '''
                </ext:UBLExtensions>'''
        if not previous_hash:
            ubl_2_1 += '''
                    <cbc:UBLVersionID>2.1</cbc:UBLVersionID>'''
        ubl_2_1 += '''
                <cbc:ProfileID>reporting:1.0</cbc:ProfileID>
                <cbc:ID>''' + str(self.check_allowed_size(1, 127, bt_1, 'bt_1')) + '''</cbc:ID>
                <cbc:UUID>''' + self.invoice_uuid + '''</cbc:UUID>
                <cbc:IssueDate>''' + self.l10n_sa_confirmation_datetime.strftime('%Y-%m-%d') + '''</cbc:IssueDate>
                <cbc:IssueTime>''' + self.l10n_sa_confirmation_datetime.strftime('%H:%M:%SZ') + '''</cbc:IssueTime>
                <cbc:InvoiceTypeCode name="''' + ksa_2 + '''">''' + bt_3 + '''</cbc:InvoiceTypeCode>'''
        if self.ksa_note:
            ubl_2_1 += '''
                <cbc:Note>''' + self.check_allowed_size(0, 1000, self.ksa_note,
                                                        self._fields['ksa_note'].string) + '''</cbc:Note>'''
        ubl_2_1 += '''
                <cbc:DocumentCurrencyCode>''' + document_currency + '''</cbc:DocumentCurrencyCode>
                <cbc:TaxCurrencyCode>SAR</cbc:TaxCurrencyCode>'''
        if self.purchase_id.id:
            ubl_2_1 += '''
                <cac:OrderReference>
                    <cbc:ID>''' + str(
                self.check_allowed_size(0, 127, self.purchase_id.id, self._fields['purchase_id'].string)) + '''</cbc:ID>
                </cac:OrderReference>'''
        if bt_3 != '388':  # BR-KSA-56
            ubl_2_1 += '''
                <cac:BillingReference>
                    <cac:InvoiceDocumentReference>
                        <cbc:ID>''' + str(self.check_allowed_size(1, 5000, bt_25.id, 'bt_25')) + '''</cbc:ID>
                        <cbc:IssueDate>''' + str(bt_25.l10n_sa_confirmation_datetime.strftime('%Y-%m-%d')) + '''</cbc:IssueDate>
                    </cac:InvoiceDocumentReference>
                </cac:BillingReference>'''
        ubl_2_1 += '''
                <cac:AdditionalDocumentReference>
                    <cbc:ID>ICV</cbc:ID>
                    <cbc:UUID>''' + str(ksa_16) + '''</cbc:UUID>
                </cac:AdditionalDocumentReference>
                <cac:AdditionalDocumentReference>
                    <cbc:ID>PIH</cbc:ID>
                    <cac:Attachment>
                        <cbc:EmbeddedDocumentBinaryObject mimeCode="text/plain">''' + str(ksa_13) + '''</cbc:EmbeddedDocumentBinaryObject>
                    </cac:Attachment>
                </cac:AdditionalDocumentReference>'''
        if not is_tax_invoice:
            # if is_tax_invoice:
            ubl_2_1 += '''<cac:AdditionalDocumentReference>
                    <cbc:ID>QR</cbc:ID>
                    <cac:Attachment>
                        <cbc:EmbeddedDocumentBinaryObject mimeCode="text/plain">zatca_l10n_sa_qr_code_str</cbc:EmbeddedDocumentBinaryObject>
                    </cac:Attachment>
                </cac:AdditionalDocumentReference>'''
        if not previous_hash and not is_tax_invoice:
            if signature:  # BR-KSA-60
                ubl_2_1 += '''
                <cac:Signature>
                    <cbc:ID>urn:oasis:names:specification:ubl:signature:Invoice</cbc:ID>
                    <cbc:SignatureMethod>urn:oasis:names:specification:ubl:dsig:enveloped:xades</cbc:SignatureMethod>
                </cac:Signature>'''
        ubl_2_1 += '''
                <cac:AccountingSupplierParty>
                    <cac:Party>'''
        ubl_2_1 += '''
                        <cac:PartyIdentification>
                            <cbc:ID schemeID="''' + license + '''">''' + license_no + '''</cbc:ID>
                        </cac:PartyIdentification>
                        <cac:PostalAddress>
                            <cbc:StreetName>''' + self.check_allowed_size(1, 1000, conf_company['street']['value'],
                                                                          "Company " + company_id._fields[conf_company[
                                                                              'street'][
                                                                              'field']].string) + '''</cbc:StreetName>'''
        if conf_company["street2"]['value']:
            ubl_2_1 += '''
                            <cbc:AdditionalStreetName>''' + self.check_allowed_size(0, 127,
                                                                                    conf_company['street2']['value'],
                                                                                    "Company " + company_id._fields[
                                                                                                               conf_company[
                                                                                                                   'street2'][
                                                                                                                   'field']].string) + '''</cbc:AdditionalStreetName>'''
        if len(str(company_id.zip)) != 5:
            raise exceptions.ValidationError(_('Company/Seller PostalZone/Zip must be exactly 5 digits'))
        ubl_2_1 += '''  <cbc:BuildingNumber>''' + str(company_id.building_no) + '''</cbc:BuildingNumber>'''
        if company_id.additional_no:
            ubl_2_1 += '''  
                            <cbc:PlotIdentification>''' + str(
                company_id.additional_no) + '''</cbc:PlotIdentification>'''
        ubl_2_1 += '''  <cbc:CitySubdivisionName>''' + self.check_allowed_size(1, 127,
                                                                               conf_company["district"]['value'],
                                                                               "Company " + company_id._fields[
                                                                                   conf_company["district"][
                                                                                       'field']].string) + '''</cbc:CitySubdivisionName>
                            <cbc:CityName>''' + self.check_allowed_size(1, 127, conf_company["city"]['value'],
                                                                        "Company " + company_id._fields[conf_company[
                                                                            "city"]['field']].string) + '''</cbc:CityName>
                            <cbc:PostalZone>''' + str(company_id.zip) + '''</cbc:PostalZone>
                            <cbc:CountrySubentity>''' + self.check_allowed_size(1, 127,
                                                                                conf_company["state_id_name"]['value'],
                                                                                "Company %s %s" % (company_id._fields[
                                                                                                       'state_id'].string,
                                                                                                   company_id.state_id._fields[
                                                                                                       conf_company[
                                                                                                           "state_id_name"][
                                                                                                           'field']].string)) + '''</cbc:CountrySubentity>
                            <cac:Country>
                                <cbc:IdentificationCode>''' + company_id.country_id.code + '''</cbc:IdentificationCode>
                            </cac:Country>
                        </cac:PostalAddress>
                        <cac:PartyTaxScheme>
                            <cbc:CompanyID>''' + bt_31 + '''</cbc:CompanyID>
                            <cac:TaxScheme>
                                <cbc:ID>VAT</cbc:ID>
                            </cac:TaxScheme>
                        </cac:PartyTaxScheme>
                        <cac:PartyLegalEntity>
                            <cbc:RegistrationName>''' + self.check_allowed_size(1, 1000, conf_company["name"]['value'],
                                                                                "Company " + company_id._fields[
                                                                                                                                                                                                                                                                                                                                                                        conf_company[
                                                                                                                                                                                                                                                                                                                                                                            "name"][
                                                                                                                                                                                                                                                                                                                                                                            'field']].string) + '''</cbc:RegistrationName>
                        </cac:PartyLegalEntity>
                    </cac:Party>
                </cac:AccountingSupplierParty>'''
        ubl_2_1 += '''
                <cac:AccountingCustomerParty>
                    <cac:Party>'''
        if buyer_identification and buyer_identification_no:
            ubl_2_1 += '''<cac:PartyIdentification>
                            <cbc:ID schemeID="''' + buyer_identification + '''">''' + buyer_identification_no + '''</cbc:ID>
                        </cac:PartyIdentification>'''
        if is_tax_invoice:
            ubl_2_1 += '''
                        <cac:PostalAddress>
                            <cbc:StreetName>''' + self.check_allowed_size(1, 1000, conf_partner["street"]["value"],
                                                                          "Customer " + partner_id._fields[conf_partner[
                                                                              "street"][
                                                                              "field"]].string) + '''</cbc:StreetName>'''
            if partner_id.street2:
                ubl_2_1 += '''
                            <cbc:AdditionalStreetName>''' + self.check_allowed_size(0, 127,
                                                                                    conf_partner["street2"]["value"],
                                                                                    "Customer %s" % partner_id._fields[
                                                                                                                   conf_partner[
                                                                                                                       "street2"][
                                                                                                                       "field"]].string) + '''</cbc:AdditionalStreetName>'''
            if partner_id.country_id.code == 'SA' or partner_id.building_no:
                ubl_2_1 += '''
                            <cbc:BuildingNumber>''' + str(partner_id.building_no) + '''</cbc:BuildingNumber>'''
            if partner_id.additional_no:
                ubl_2_1 += '''
                            <cbc:PlotIdentification>''' + str(
                    partner_id.additional_no) + '''</cbc:PlotIdentification>'''
            if partner_id.country_id.code == 'SA' or conf_partner["district"]["value"]:
                ubl_2_1 += '''
                            <cbc:CitySubdivisionName>''' + self.check_allowed_size(1, 127,
                                                                                   conf_partner["district"]["value"],
                                                                                   "Customer %s" % partner_id._fields[
                                                                                                                  conf_partner[
                                                                                                                      "district"][
                                                                                                                      "field"]].string) + '''</cbc:CitySubdivisionName>'''
            ubl_2_1 += '''
                            <cbc:CityName>''' + self.check_allowed_size(1, 127, conf_partner["city"]["value"],
                                                                        "Customer %s" % partner_id._fields[
                                                                                                   conf_partner["city"][
                                                                                                       "field"]].string) + '''</cbc:CityName>'''
            if partner_id.country_id.code == 'SA' or partner_id.zip:
                ubl_2_1 += '''
                            <cbc:PostalZone>''' + str(partner_id.zip) + '''</cbc:PostalZone>'''
            if partner_id.state_id.id:
                ubl_2_1 += '''
                            <cbc:CountrySubentity>''' + self.check_allowed_size(1, 127,
                                                                                conf_partner["state_id_name"]["value"],
                                                                                "Customer %s %s" % (partner_id._fields[
                                                                                                        'state_id'].string,
                                                                                                    partner_id.state_id._fields[
                                                                                                        conf_partner[
                                                                                                            "state_id_name"][
                                                                                                            "field"]].string)) + '''</cbc:CountrySubentity>'''
            ubl_2_1 += '''
                            <cac:Country>
                                <cbc:IdentificationCode>''' + partner_id.country_id.code + '''</cbc:IdentificationCode>
                            </cac:Country>
                        </cac:PostalAddress>
                        <cac:PartyTaxScheme>'''
            if partner_id.vat and not self.l10n_is_exports_invoice:
                ubl_2_1 += '''
                            <cbc:CompanyID>''' + partner_id.vat + '''</cbc:CompanyID>'''
            ubl_2_1 += '''
                            <cac:TaxScheme>
                                <cbc:ID>VAT</cbc:ID>
                            </cac:TaxScheme>
                        </cac:PartyTaxScheme>'''
        bt_121 = 0  # in ['VATEX-SA-EDU', 'VATEX-SA-HEA']
        bt_121 = list(set(self.invoice_line_ids.tax_ids.mapped('tax_exemption_selection')))
        # BR-KSA-25 and BR-KSA-42
        if is_tax_invoice or \
                (not is_tax_invoice and ('VATEX-SA-EDU' in bt_121 or 'VATEX-SA-HEA' in bt_121)) or \
                (not is_tax_invoice and self.l10n_is_summary_invoice):
            ubl_2_1 += '''
                        <cac:PartyLegalEntity>
                            <cbc:RegistrationName>''' + self.check_allowed_size(1, 1000, conf_partner["name"]["value"],
                                                                                "Customer %s" % partner_id._fields[
                                                                                                           conf_partner[
                                                                                                               "name"][
                                                                                                               "field"]].string) + '''</cbc:RegistrationName>
                        </cac:PartyLegalEntity>'''
        if ('VATEX-SA-EDU' in bt_121 or 'VATEX-SA-HEA' in bt_121) and buyer_identification != 'NAT':  # BR-KSA-49
            message = _("As tax exemption reason code is in") + " 'VATEX-SA-EDU', 'VATEX-SA-HEA'"
            message += " " + _("then Buyer Identification must be") + " 'NAT'"
            raise exceptions.ValidationError(message)
        ubl_2_1 += '''
                    </cac:Party>
                </cac:AccountingCustomerParty>'''
        latest_delivery_date = 1 if not is_tax_invoice and self.l10n_is_summary_invoice else 0
        if delivery and (
                (bt_3 == '388' and ksa_2[:2] == '01' or not is_tax_invoice and self.l10n_is_summary_invoice) or (
                latest_delivery_date and not_know)):
            ubl_2_1 += '''
                <cac:Delivery>'''
            ksa_5 = l10n_sa_delivery_date
            if bt_3 == '388' and ksa_2[:2] == '01' or not is_tax_invoice and self.l10n_is_summary_invoice:
                ubl_2_1 += '''
                    <cbc:ActualDeliveryDate>''' + str(ksa_5.strftime('%Y-%m-%d')) + '''</cbc:ActualDeliveryDate>'''
            if latest_delivery_date and not_know:
                ksa_24 = l10n_sa_delivery_date
                if ksa_24 < ksa_5:
                    raise exceptions.ValidationError(
                        _('LatestDeliveryDate must be less then or equal to ActualDeliveryDate'))
                ubl_2_1 += '''
                    <cbc:LatestDeliveryDate> ''' + str(ksa_24.strftime('%Y-%m-%d')) + ''' </cbc:LatestDeliveryDate> '''
            if not_know:
                ubl_2_1 += '''
                    <cac:DeliveryLocation>
                        <cac:Address>
                            <cac:Country>
                                <cbc:IdentificationCode>''' + "" + '''</cbc:IdentificationCode>
                            </cac:Country>
                        </cac:Address>
                    </cac:DeliveryLocation'''
            ubl_2_1 += '''
                </cac:Delivery>'''
        ubl_2_1 += '''<cac:PaymentMeans>
                <cbc:PaymentMeansCode>''' + str(bt_81) + '''</cbc:PaymentMeansCode>'''
        if bt_3 != '388':
            ubl_2_1 += '''
                <cbc:InstructionNote>''' + self.check_allowed_size(1, 1000, self.credit_debit_reason, self._fields[
                'credit_debit_reason'].string) + '''</cbc:InstructionNote>'''
        ubl_2_1 += '''
            </cac:PaymentMeans>'''
        if document_level_allowance_charge:
            bt_96 = float('{:0.2f}'.format(float_round(0, precision_rounding=0.01)))
            bt_96 = 100 if bt_96 > 100 else (0 if bt_96 < 0 else bt_96)
            ubl_2_1 += '''
                <cac:AllowanceCharge>
                    <cbc:ChargeIndicator>false</cbc:ChargeIndicator>
                    <cbc:AllowanceChargeReason>Discount</cbc:AllowanceChargeReason>
                    <cbc:Amount currencyID="''' + document_currency + '''">''' + str(bt_92) + '''</cbc:Amount>
                    <cbc:BaseAmount currencyID="''' + document_currency + '''">''' + str(bt_92) + '''</cbc:BaseAmount>
                    <cac:TaxCategory>
                        <cbc:ID>''' + "0" + '''</cbc:ID>
                        <cbc:Percent>''' + str(bt_96) + '''</cbc:Percent>
                        <cac:TaxScheme>
                            <cbc:ID>''' + "0" + '''</cbc:ID>
                        </cac:TaxScheme>
                    </cac:TaxCategory>
                </cac:AllowanceCharge>'''
        invoice_line_xml = ''
        for invoice_line_id in self.invoice_line_ids:
            if invoice_line_id.discount:
                bt_137 = float('{:0.2f}'.format(
                    float_round(invoice_line_id.price_unit * invoice_line_id.quantity, precision_rounding=0.01)))
                bt_138 = invoice_line_id.discount  # BR-KSA-DEC-01 for BT-138 only done
                bt_136 = float('{:0.2f}'.format(float_round(bt_137 * bt_138 / 100, precision_rounding=0.01)))
            else:
                bt_136 = float('{:0.2f}'.format(float_round(0, precision_rounding=0.01)))
                bt_137 = float('{:0.2f}'.format(float_round(0, precision_rounding=0.01)))
                bt_138 = invoice_line_id.discount  # BR-KSA-DEC-01 for BT-138 only done
            bt_129 = invoice_line_id.quantity
            bt_147 = 0  # NO ITEM PRICE DISCOUNT bt_148 * invoice_line_id.discount/100 if invoice_line_id.discount else 0
            bt_148 = invoice_line_id.price_unit
            bt_146 = bt_148 - bt_147
            bt_149 = 1  # ??
            bt_131 = float('{:0.2f}'.format(float_round(((bt_146 / bt_149) * bt_129), precision_rounding=0.01)))
            bt_131 -= float('{:0.2f}'.format(float_round(bt_136, precision_rounding=0.01)))
            bt_131 = float('{:0.2f}'.format(float_round(bt_131, precision_rounding=0.01)))
            bt_106 += float('{:0.2f}'.format(float_round(bt_131, precision_rounding=0.01)))
            bt_106 = float('{:0.2f}'.format(float_round(bt_106, precision_rounding=0.01)))
            bt_151 = invoice_line_id.tax_ids.classified_tax_category if invoice_line_id.tax_ids else "O"
            bt_152 = float('{:0.2f}'.format(
                float_round(invoice_line_id.tax_ids.amount, precision_rounding=0.01))) if invoice_line_id.tax_ids else 0
            bt_152 = 100 if bt_152 > 100 else (0 if bt_152 < 0 else bt_152)

            if bt_151 == "Z":
                bt_152 = 0
                if not bg_23_list.get("Z", False):
                    bg_23_list["Z"] = {'bt_116': 0, 'bt_121': invoice_line_id.tax_ids.tax_exemption_code,
                                       'bt_120': invoice_line_id.tax_ids.tax_exemption_text,
                                       'bt_119': bt_152, 'bt_117': 0}
                bg_23_list["Z"]['bt_116'] += bt_131
                # bg_23_list = ["Z"]  # BR-Z-01
            elif bt_151 == "E":
                bt_152 = 0
                if not bg_23_list.get("E", False):
                    bg_23_list["E"] = {'bt_116': 0, 'bt_121': invoice_line_id.tax_ids.tax_exemption_code,
                                       'bt_120': invoice_line_id.tax_ids.tax_exemption_text,
                                       'bt_119': bt_152, 'bt_117': 0}
                bg_23_list["E"]['bt_116'] += bt_131
                # bg_23_list = ["E"]  # BR-E-01
            elif bt_151 == "S":
                if not bg_23_list.get("S", False):
                    bg_23_list["S"] = {'bt_116': 0, 'bt_119': bt_152, 'bt_117': 0}
                bg_23_list["S"]['bt_116'] += bt_131
                # bg_23_list = ["E"]  # BR-S-09
            # elif bt_151 == "O":
            else:
                bt_152 = 0
                if not bg_23_list.get("O", False):
                    if invoice_line_id.tax_ids and (not invoice_line_id.tax_ids.tax_exemption_text or
                                                    not invoice_line_id.tax_ids.tax_exemption_code):
                        raise exceptions.MissingError(
                            _("Tax exemption Reason Text  is missing in Tax Category") + " 'O' ")
                    bg_23_list["O"] = {'bt_116': 0,
                                       'bt_121': invoice_line_id.tax_ids.tax_exemption_code if
                                       len(invoice_line_id.tax_ids) > 0 else 'VATEX-SA-OOS',
                                       'bt_120': invoice_line_id.tax_ids.tax_exemption_text if
                                       len(invoice_line_id.tax_ids) > 0 else 'Not subject to VAT',
                                       'bt_119': 0, 'bt_117': 0}
                bg_23_list["O"]['bt_116'] += bt_131
                # bg_23_list = ["O"]  # BR-O-01

            def next_invoice_line_id(invoice_line_id):
                id = self.env['ir.sequence'].with_company(self.company_id).next_by_code('zatca.move.line.seq')
                if invoice_line_id.sudo().search([('zatca_id', '=', id)]).id:
                    id = next_invoice_line_id(invoice_line_id)
                return id

            # seq check
            sequence = self.env['ir.sequence'].search([('code', '=', 'zatca.move.line.seq'),
                                                       ('company_id', 'in', [self.company_id.id, False])],
                                                      order='company_id', limit=1)
            if not sequence:
                raise exceptions.MissingError(
                    _("Sequence") + " 'zatca.move.line.seq' " + _("not found for this company"))
            invoice_line_id.zatca_id = next_invoice_line_id(invoice_line_id)

            invoice_line_xml += '''
                <cac:InvoiceLine>
                    <cbc:ID>''' + str(invoice_line_id.zatca_id) + '''</cbc:ID>
                    <cbc:InvoicedQuantity unitCode="PCE">''' + str(bt_129) + '''</cbc:InvoicedQuantity>
                    <cbc:LineExtensionAmount currencyID="''' + document_currency + '''">''' + str(
                bt_131) + '''</cbc:LineExtensionAmount>'''
            if invoice_line_id.discount:  # line_allowance_charge:
                invoice_line_xml += '''
                    <cac:AllowanceCharge>
                        <cbc:ChargeIndicator>false</cbc:ChargeIndicator>
                        <cbc:AllowanceChargeReasonCode>95</cbc:AllowanceChargeReasonCode>
                        <cbc:AllowanceChargeReason>Discount</cbc:AllowanceChargeReason>'''
                # invoice_line_xml += '''
                #     <cbc:MultiplierFactorNumeric>''' + str(bt_138) + '''</cbc:MultiplierFactorNumeric>'''
                invoice_line_xml += '''
                        <cbc:Amount currencyID="''' + document_currency + '''">''' + str(bt_136) + '''</cbc:Amount>'''
                # invoice_line_xml += '''
                #     <cbc:BaseAmount currencyID="''' + document_currency + '''">''' + str(bt_137) + '''</cbc:BaseAmount>'''
                if bt_151 != 'O':
                    invoice_line_xml += '''
                            <cac:TaxCategory>
                                <cbc:ID>S</cbc:ID>
                                <cbc:Percent>15</cbc:Percent>
                                <cac:TaxScheme>
                                    <cbc:ID>VAT</cbc:ID>
                                </cac:TaxScheme>
                            </cac:TaxCategory>'''
                invoice_line_xml += '''
                        </cac:AllowanceCharge>'''
            ksa_11 = float('{:0.2f}'.format(float_round(bt_131 * bt_152 / 100, precision_rounding=0.01)))  # BR-KSA-50
            ksa_12 = float('{:0.2f}'.format(float_round(bt_131 + ksa_11, precision_rounding=0.01)))  # BR-KSA-51
            # BR-KSA-52 and BR-KSA-53
            invoice_line_xml += '''
                    <cac:TaxTotal>
                        <cbc:TaxAmount currencyID="''' + document_currency + '''">''' + str(ksa_11) + '''</cbc:TaxAmount>
                        <cbc:RoundingAmount currencyID="''' + document_currency + '''">''' + str(ksa_12) + '''</cbc:RoundingAmount>
                    </cac:TaxTotal>
                    <cac:Item>
                        <cbc:Name>''' + str(
                self._get_zatca_product_name(invoice_line_id)["name"]["value"]) + '''</cbc:Name>'''
            if invoice_line_id.product_id.barcode and invoice_line_id.product_id.code_type:
                invoice_line_xml += '''
                        <cac:StandardItemIdentification>
                            <cbc:ID schemeID="''' + str(invoice_line_id.product_id.code_type) + '''">''' + str(
                    invoice_line_id.product_id.barcode) + '''</cbc:ID>
                        </cac:StandardItemIdentification>'''
            invoice_line_xml += '''
                        <cac:ClassifiedTaxCategory>
                            <cbc:ID>''' + str(bt_151) + '''</cbc:ID>'''
            if bt_151 != 'O':
                invoice_line_xml += '''
                            <cbc:Percent>''' + str(bt_152) + '''</cbc:Percent>'''
            invoice_line_xml += '''
                            <cac:TaxScheme>
                                <cbc:ID>VAT</cbc:ID>
                            </cac:TaxScheme>
                        </cac:ClassifiedTaxCategory>
                    </cac:Item>
                    <cac:Price>
                        <cbc:PriceAmount currencyID="''' + document_currency + '''">''' + str(bt_146) + '''</cbc:PriceAmount>
                        <cbc:BaseQuantity unitCode="PCE">''' + str(bt_149) + '''</cbc:BaseQuantity>
                    </cac:Price>
                </cac:InvoiceLine>'''
        bt_110 = float(
            '{:0.2f}'.format(float_round(0, precision_rounding=0.01)))  # Sum of bt-117 Calculated in bg_23 loop
        tax_subtotal_xml = ''
        for bg_23 in bg_23_list.keys():
            bt_116 = float('{:0.2f}'.format(float_round(bg_23_list[bg_23]['bt_116'], precision_rounding=0.01)))
            bt_119 = bg_23_list[bg_23]['bt_119']
            bt_118 = bg_23
            if bt_118 == "S":
                bt_117 = float('{:0.2f}'.format(float_round(bt_116 * (bt_119 / 100), precision_rounding=0.01)))
                bt_110 += bt_117
            else:
                bt_117 = float('{:0.2f}'.format(float_round(0, precision_rounding=0.01)))
            tax_subtotal_xml += '''
                <cac:TaxSubtotal>
                    <cbc:TaxableAmount currencyID="''' + document_currency + '''">''' + str(bt_116) + '''</cbc:TaxableAmount>
                    <cbc:TaxAmount currencyID="''' + document_currency + '''">''' + str(bt_117) + '''</cbc:TaxAmount>
                    <cac:TaxCategory>
                        <cbc:ID>''' + str(bt_118) + '''</cbc:ID>
                        <cbc:Percent>''' + str(bt_119) + '''</cbc:Percent>'''
            if bt_118 != "S" and bt_118 in ['E', 'O', 'Z']:
                bt_120 = bg_23_list[bg_23]['bt_120']
                bt_121 = bg_23_list[bg_23]['bt_121']
                tax_subtotal_xml += '''
                        <cbc:TaxExemptionReasonCode>''' + str(bt_121) + '''</cbc:TaxExemptionReasonCode>
                        <cbc:TaxExemptionReason>''' + str(bt_120) + '''</cbc:TaxExemptionReason>'''
            tax_subtotal_xml += '''
                        <cac:TaxScheme>
                            <cbc:ID>VAT</cbc:ID>
                        </cac:TaxScheme>
                    </cac:TaxCategory>
                </cac:TaxSubtotal>'''
        bt_109 = float('{:0.2f}'.format(float_round(bt_106 - bt_107, precision_rounding=0.01)))
        bt_111 = float('{:0.2f}'.format(
            float_round(bt_110 if document_currency == "SAR" else abs(self.amount_tax_signed),
                        precision_rounding=0.01)))  # Same as bt-110
        bt_112 = float('{:0.2f}'.format(float_round(bt_109 + bt_110, precision_rounding=0.01)))
        # bt_113 = float('{:0.2f}'.format(float_round(self.amount_total - self.amount_residual, precision_rounding=0.01)))
        bt_108 = 0
        bt_113 = 0
        bt_114 = self.discount_jasara
        bt_115 = float('{:0.2f}'.format(float_round(bt_112 - bt_113 + bt_114, precision_rounding=0.01)))
        # if bt_110 != float('{:0.2f}'.format(float_round(self.amount_tax, precision_rounding=0.01))):
        #     raise exceptions.ValidationError('Error in Tax Total Calculation')
        ubl_2_1 += '''
                <cac:TaxTotal>
                    <cbc:TaxAmount currencyID="''' + document_currency + '''">''' + str(bt_110) + '''</cbc:TaxAmount>'''
        ubl_2_1 += tax_subtotal_xml
        ubl_2_1 += '''
                </cac:TaxTotal>
                <cac:TaxTotal>
                    <cbc:TaxAmount currencyID="SAR">''' + str(bt_111) + '''</cbc:TaxAmount>
                </cac:TaxTotal>'''
        ubl_2_1 += '''
                <cac:LegalMonetaryTotal>
                    <cbc:LineExtensionAmount currencyID="''' + document_currency + '''">''' + str(bt_106) + '''</cbc:LineExtensionAmount>
                    <cbc:TaxExclusiveAmount currencyID="''' + document_currency + '''">''' + str(bt_109) + (
            " | " + str(self.amount_untaxed) if amount_verification else '') + '''</cbc:TaxExclusiveAmount>
                    <cbc:TaxInclusiveAmount currencyID="''' + document_currency + '''">''' + str(bt_112) + (
                       " | " + str(self.amount_total) if amount_verification else '') + '''</cbc:TaxInclusiveAmount>'''
        if bt_108:
            ubl_2_1 += '''
                    <cbc:ChargeTotalAmount currencyID="''' + document_currency + '''">''' + str(
                bt_108) + '''</cbc:ChargeTotalAmount>'''
        if bt_113:
            ubl_2_1 += '''
                    <cbc:PrepaidAmount currencyID="''' + document_currency + '''">''' + str(
                bt_113) + '''</cbc:PrepaidAmount>'''
        if bt_114:
            ubl_2_1 += '''
                    <cbc:PayableRoundingAmount currencyID="''' + document_currency + '''">''' + str(
                bt_114) + '''</cbc:PayableRoundingAmount>'''
        ubl_2_1 += '''
                    <cbc:PayableAmount currencyID="''' + document_currency + '''">''' + str(
            bt_115 if bt_115 > 0 else 0) + (" | " + str(self.amount_residual) if amount_verification else '') + '''</cbc:PayableAmount>
                </cac:LegalMonetaryTotal>'''
        ubl_2_1 += invoice_line_xml
        ubl_2_1 += '''
            </Invoice>'''

        file_name_specification = (str(bt_31) + "_" + self.l10n_sa_confirmation_datetime.strftime('%Y%m%dT%H%M%SZ')
                                   + "_" + str(re.sub(r"[^a-zA-Z0-9]", "-", self.zatca_unique_seq)))
        self.zatca_invoice_name = file_name_specification + ".xml"
        self.hash_with_c14n_canonicalization(xml=ubl_2_1)
        # conf.zatca_pih = self.zatca_invoice_hash
        if signature:
            hash_filename = ''
            private_key_filename = ''
            try:
                hash_filename = hashlib.sha256(
                    ('account_move_' + str(self.id) + '_signature_value').encode("UTF-8")).hexdigest()
                f = open('/tmp/' + str(hash_filename), 'wb+')
                f.write(base64.b64decode(self.zatca_invoice_hash))
                f.close()

                private_key = conf.zatca_prod_private_key
                _zatca.info("private_key:: %s", private_key)
                for x in range(1, math.ceil(len(private_key) / 64)):
                    private_key = private_key[:64 * x + x - 1] + '\n' + private_key[64 * x + x - 1:]
                private_key = "-----BEGIN EC PRIVATE KEY-----\n" + private_key + "\n-----END EC PRIVATE KEY-----"
                _zatca.info("private_key:: %s", private_key)

                private_key_filename = hashlib.sha256(
                    ('account_move_' + str(self.id) + '_private_key').encode("UTF-8")).hexdigest()
                f = open('/tmp/' + str(private_key_filename), 'wb+')
                f.write(private_key.encode())
                f.close()

                signature = '''openssl dgst -sha256 -sign /tmp/''' + private_key_filename + ''' /tmp/''' + hash_filename + ''' | base64 /dev/stdin'''
                signature_value = os.popen(signature).read()
                _zatca.info("signature_value:: %s", signature_value)
                signature_value = signature_value.replace('\n', '').replace(' ', '')
                _zatca.info("signature_value:: %s", signature_value)
                if not signature_value or signature_value in [None, '']:
                    raise exceptions.ValidationError(_("Error in private key, kindly regenerate credentials."))

                # signature_filename = hashlib.sha256(('account_move_' + str(self.id) + '_signature_value').encode("UTF-8")).hexdigest()
                # os.system('''echo ''' + str(signature_value) + ''' | base64 -d /dev/stdin > /tmp/''' + str(signature_filename))
                # Signature validation
                # signature_verify = '''echo ''' + str(self.zatca_invoice_hash_hex) + ''' | openssl dgst -verify /tmp/zatcapublickey.pem -signature /tmp/''' + str(signature_filename) + ''' /dev/stdin'''
                # if "Verified OK" not in os.popen(signature_verify).read():
                #     raise exceptions.ValidationError("Signature can't be verified, try again.")
                # os.system('''rm  /tmp/''' + str(signature_filename))

                ubl_2_1 = ubl_2_1.replace('zatca_signature_hash', str(base_64_5))
                ubl_2_1 = ubl_2_1.replace('zatca_signature_value', str(signature_value))
                _zatca.info("compute_qr_code_str")
                self.compute_qr_code_str(signature_value, is_tax_invoice, bt_112, bt_110)
                _zatca.info("l10n_sa_qr_code_str:: %s", self.l10n_sa_qr_code_str)
                if not is_tax_invoice:
                    # if is_tax_invoice:
                    ubl_2_1 = ubl_2_1.replace('zatca_l10n_sa_qr_code_str', str(self.l10n_sa_qr_code_str))
            except Exception as e:
                _logger.info("ZATCA: Private Key Issue: " + str(e))
                if str(e) == _('Error in private key, kindly regenerate credentials.'):
                    raise e
                raise exceptions.AccessError(_("Error in signing invoice, kindly try again."))
            finally:
                # For security purpose, files should not exist out of odoo
                os.system('''rm  /tmp/''' + str(hash_filename))
                os.system('''rm  /tmp/''' + str(private_key_filename))

        ubl_2_1 = ubl_2_1.replace('zatca_invoice_hash', str(self.zatca_invoice_hash))

        try:
            atts = self.env['ir.attachment'].sudo().search(
                [('res_model', '=', 'account.move'), ('res_field', '=', 'zatca_invoice'),
                 ('res_id', 'in', self.ids), ('company_id', 'in', [self.env.company.id, False])])
            if atts:
                atts.sudo().write({'datas': base64.b64encode(bytes(ubl_2_1, 'utf-8'))})
            else:
                atts.sudo().create([{
                    'name': file_name_specification + ".xml",
                    'res_model': 'account.move',
                    'res_field': 'zatca_invoice',
                    'res_id': self.id,
                    'type': 'binary',
                    'datas': base64.b64encode(bytes(ubl_2_1, 'utf-8')),
                    'mimetype': 'text/xml',
                    # 'datas_fname': file_name_specification + ".xml"
                }])
            self._cr.commit()
        except Exception as e:
            _logger.info("ZATCA: Attachment in Odoo Issue: " + str(e))
            exceptions.AccessError(_("Error in creating invoice attachment."))
        _logger.info("ZATCA: Invoice & its hash generated for invoice " + str(self.name))