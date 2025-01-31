# -*- coding: utf-8 -*-
import os

from unittest.mock import patch

from odoo.tools import misc
from .common import TestL10nClEdiCommon, _check_with_xsd_patch


@patch('odoo.tools.xml_utils._check_with_xsd', _check_with_xsd_patch)
class TestL10nClDte(TestL10nClEdiCommon):
    """
    Summary of the document types to test:
        - 33:
            - A invoice with tax in each line
            - A invoice with references_ids and tax in each line
            - A invoice with holding taxes
            - A invoice with discounts
        - 34:
            - A invoice with two lines
        - 39:
            - A invoice
        - 56:
            - A  invoice with line discounts
        - 110:
            - A invoice
    """

    @patch('odoo.addons.l10n_cl_edi.models.l10n_cl_edi_util.L10nClEdiUtilMixin._get_cl_current_strftime')
    def test_l10n_cl_dte_33(self, get_cl_current_strftime):
        get_cl_current_strftime.return_value = '2019-10-24T20:00:00'

        self.tax_19 = self.env['account.tax'].search([
            ('name', '=', 'IVA 19% Venta'),
            ('company_id', '=', self.company_data['company'].id)])
        invoice = self.env['account.move'].with_context(default_move_type='out_invoice').create({
            'partner_id': self.partner_sii.id,
            'move_type': 'out_invoice',
            'invoice_date': '2019-10-23',
            'currency_id': self.env.ref('base.CLP').id,
            'journal_id': self.sale_journal.id,
            'l10n_latam_document_type_id': self.env.ref('l10n_cl.dc_a_f_dte').id,
            'company_id': self.company_data['company'].id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Tapa Ranurada UL FM 300 6"',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 26,
                'price_unit': 2391.0,
                'tax_ids': [self.tax_19.id],
            }), (0, 0, {
                'name': 'Copla Flexible 1NS 6"',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 80,
                'price_unit': 2914.0,
                'tax_ids': [self.tax_19.id],
            })],
        })

        invoice.action_post()

        self.assertEqual(invoice.state, 'posted')
        self.assertEqual(invoice.l10n_cl_dte_status, 'not_sent')

        xml_expected_dte = misc.file_open(os.path.join(
            'l10n_cl_edi', 'tests', 'expected_dtes', 'dte_33.xml')).read()

        self.assertXmlTreeEqual(
            self.get_xml_tree_from_string(xml_expected_dte.encode()),
            self.get_xml_tree_from_attachment(invoice.l10n_cl_sii_send_file)
        )

    @patch('odoo.addons.l10n_cl_edi.models.l10n_cl_edi_util.L10nClEdiUtilMixin._get_cl_current_strftime')
    def test_l10n_cl_dte_33_with_reference_ids(self, get_cl_current_strftime):
        get_cl_current_strftime.return_value = '2019-10-24T20:00:00'

        self.tax_19 = self.env['account.tax'].search([
            ('name', '=', 'IVA 19% Venta'),
            ('company_id', '=', self.company_data['company'].id)])
        invoice = self.env['account.move'].with_context(default_move_type='out_invoice').create({
            'partner_id': self.partner_sii.id,
            'move_type': 'out_invoice',
            'invoice_date': '2019-10-23',
            'currency_id': self.env.ref('base.CLP').id,
            'journal_id': self.sale_journal.id,
            'l10n_latam_document_type_id': self.env.ref('l10n_cl.dc_a_f_dte').id,
            'company_id': self.company_data['company'].id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Tapa Ranurada UL FM 300 6"',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 26,
                'price_unit': 2391.0,
                'tax_ids': [self.tax_19.id],
            }), (0, 0, {
                'name': 'Copla Flexible 1NS 6"',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 80,
                'price_unit': 2914.0,
                'tax_ids': [self.tax_19.id],
            })],
        })
        invoice.write({
            'l10n_cl_reference_ids': [(0, 0, {
                'origin_doc_number': 'PO00273',
                'l10n_cl_reference_doc_type_selection': '801',
                'reason': 'Test',
                'move_id': invoice.id,
                'date': '2019-10-18'
            }), (0, 0, {
                'origin_doc_number': '996327',
                'l10n_cl_reference_doc_type_selection': '52',
                'reason': 'Test',
                'move_id': invoice.id,
                'date': '2019-10-18'
            })],
        })

        invoice._post()

        self.assertEqual(invoice.state, 'posted')
        self.assertEqual(invoice.l10n_cl_dte_status, 'not_sent')

        xml_expected_dte = misc.file_open(os.path.join(
            'l10n_cl_edi', 'tests', 'expected_dtes', 'dte_33_with_reference_ids.xml')).read()

        self.assertXmlTreeEqual(
            self.get_xml_tree_from_string(xml_expected_dte.encode()),
            self.get_xml_tree_from_attachment(invoice.l10n_cl_sii_send_file)
        )

    @patch('odoo.addons.l10n_cl_edi.models.l10n_cl_edi_util.L10nClEdiUtilMixin._get_cl_current_strftime')
    def test_l10n_cl_dte_33_withholding_taxes(self, get_cl_current_strftime):
        get_cl_current_strftime.return_value = '2019-10-24T20:00:00'

        self.tax_19 = self.env['account.tax'].search([
            ('name', '=', 'IVA 19% Venta'),
            ('company_id', '=', self.company_data['company'].id)])
        self.tax_205 = self.env['account.tax'].search([
            ('name', '=', 'Vinos (Ventas)'),
            ('company_id', '=', self.company_data['company'].id)])
        self.tax_100 = self.env['account.tax'].search([
            ('name', '=', 'Beb. Analc. 10% (Ventas)'),
            ('company_id', '=', self.company_data['company'].id)])

        invoice = self.env['account.move'].with_context(default_move_type='out_invoice').create({
            'partner_id': self.partner_sii.id,
            'move_type': 'out_invoice',
            'invoice_date': '2019-10-23',
            'currency_id': self.env.ref('base.CLP').id,
            'journal_id': self.sale_journal.id,
            'l10n_latam_document_type_id': self.env.ref('l10n_cl.dc_a_f_dte').id,
            'company_id': self.company_data['company'].id,
            'invoice_line_ids': [(0, 0, {
                'name': 'FALERNIA CABERNET SAUVIGNON RESERVA 2018 750ML 14',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 1,
                'price_unit': 31110.0,
                'tax_ids': [self.tax_19.id, self.tax_205.id],
            }), (0, 0, {
                'name': 'FALERNIA CARMENERE 2017 RESERVA 14 750ML',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 1,
                'price_unit': 31110.0,
                'tax_ids': [self.tax_19.id, self.tax_205.id],
            }), (0, 0, {
                'name': 'FAL CARMENERE 2017 375CC',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 1,
                'price_unit': 36210.0,
                'tax_ids': [self.tax_19.id, self.tax_205.id],
            }), (0, 0, {
                'name': 'FALERNIA CARMENERE GRAN RESERVA 2016 750ML 15',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 1,
                'price_unit': 26138.0,
                'tax_ids': [self.tax_19.id, self.tax_205.id],
            }), (0, 0, {
                'name': 'FALERNIA C. SAUVIGNON GR.RESERVA 2017 750ML 14,5',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 1,
                'price_unit': 26138.0,
                'tax_ids': [self.tax_19.id, self.tax_205.id],
            }), (0, 0, {
                'name': 'COCA COLA NO RETORNABLE 2L',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 12,
                'price_unit': 800.0,
                'tax_ids': [self.tax_19.id, self.tax_100.id],
            }), (0, 0, {
                'name': 'COSTO LOGISTICO',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 1,
                'price_unit': 7143.0,
                'tax_ids': [self.tax_19.id],
            }), ],
        })

        invoice.action_post()

        self.assertEqual(invoice.state, 'posted')
        self.assertEqual(invoice.l10n_cl_dte_status, 'not_sent')

        xml_expected_dte = misc.file_open(os.path.join(
            'l10n_cl_edi', 'tests', 'expected_dtes', 'dte_33_with_holding_taxes.xml')).read()

        self.assertXmlTreeEqual(
            self.get_xml_tree_from_string(xml_expected_dte.encode()),
            self.get_xml_tree_from_attachment(invoice.l10n_cl_sii_send_file)
        )

    @patch('odoo.addons.l10n_cl_edi.models.l10n_cl_edi_util.L10nClEdiUtilMixin._get_cl_current_strftime')
    def test_l10n_cl_dte_33_with_discounts(self, get_cl_current_strftime):
        get_cl_current_strftime.return_value = '2019-10-24T20:00:00'

        self.tax_19 = self.env['account.tax'].search([
            ('name', '=', 'IVA 19% Venta'),
            ('company_id', '=', self.company_data['company'].id)])
        invoice = self.env['account.move'].with_context(default_move_type='out_invoice').create({
            'partner_id': self.partner_sii.id,
            'move_type': 'out_invoice',
            'invoice_date': '2019-10-23',
            'currency_id': self.env.ref('base.CLP').id,
            'journal_id': self.sale_journal.id,
            'l10n_latam_document_type_id': self.env.ref('l10n_cl.dc_a_f_dte').id,
            'company_id': self.company_data['company'].id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Tapa Ranurada UL FM 300 6"',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 200,
                'price_unit': 5.0,
                'discount': 5.99,
                'tax_ids': [self.tax_19.id],
            }), (0, 0, {
                'name': 'Copla Flexible 1NS 6"',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 300,
                'price_unit': 800.0,
                'discount': 9.77,
                'tax_ids': [self.tax_19.id],
            }), (0, 0, {
                'name': 'Desk Combination',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 5,
                'price_unit': 40000.0,
                'discount': 10.00,
                'tax_ids': [self.tax_19.id],
            })],
        })

        invoice.action_post()

        self.assertEqual(invoice.state, 'posted')
        self.assertEqual(invoice.l10n_cl_dte_status, 'not_sent')

        xml_expected_dte = misc.file_open(os.path.join(
            'l10n_cl_edi', 'tests', 'expected_dtes', 'dte_33_with_discounts.xml')).read()
        self.assertXmlTreeEqual(
            self.get_xml_tree_from_string(xml_expected_dte.encode()),
            self.get_xml_tree_from_attachment(invoice.l10n_cl_sii_send_file)
        )

    @patch('odoo.addons.l10n_cl_edi.models.l10n_cl_edi_util.L10nClEdiUtilMixin._get_cl_current_strftime')
    def test_l10n_cl_dte_34(self, get_cl_current_strftime):
        get_cl_current_strftime.return_value = '2019-10-22T20:23:27'

        self.product_a.write({
            'name': 'Desk Combination',
            'default_code': 'FURN_7800'
        })

        invoice = self.env['account.move'].with_context(default_move_type='out_invoice').create({
            'partner_id': self.partner_sii.id,
            'move_type': 'out_invoice',
            'invoice_date': '2019-10-22',
            'currency_id': self.env.ref('base.CLP').id,
            'journal_id': self.sale_journal.id,
            'l10n_latam_document_type_id': self.env.ref('l10n_cl.dc_y_f_dte').id,
            'company_id': self.company_data['company'].id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Desk Combination',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 1,
                'price_unit': 1200000.0,
            }), (0, 0, {
                'name': 'Desk Combination',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 1,
                'price_unit': 2400000.0,
            })],
        })

        invoice.action_post()

        self.assertEqual(invoice.state, 'posted')
        self.assertEqual(invoice.l10n_cl_dte_status, 'not_sent')

        xml_expected_dte = misc.file_open(os.path.join(
            'l10n_cl_edi', 'tests', 'expected_dtes', 'dte_34.xml')).read()

        self.assertXmlTreeEqual(
            self.get_xml_tree_from_string(xml_expected_dte.encode()),
            self.get_xml_tree_from_attachment(invoice.l10n_cl_sii_send_file)
        )

    @patch('odoo.addons.l10n_cl_edi.models.l10n_cl_edi_util.L10nClEdiUtilMixin._get_cl_current_strftime')
    def test_l10n_cl_dte_39(self, get_cl_current_strftime):
        get_cl_current_strftime.return_value = '2019-10-24T20:00:00'

        self.tax_19 = self.env['account.tax'].search([
            ('name', '=', 'IVA 19% Venta'),
            ('company_id', '=', self.company_data['company'].id)])
        invoice = self.env['account.move'].with_context(default_move_type='out_invoice').create({
            'partner_id': self.partner_anonimo.id,
            'move_type': 'out_invoice',
            'invoice_date': '2019-10-23',
            'currency_id': self.env.ref('base.CLP').id,
            'journal_id': self.sale_journal.id,
            'l10n_latam_document_type_id': self.env.ref('l10n_cl.dc_b_f_dte').id,
            'company_id': self.company_data['company'].id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Regla De Anchura De Grietas',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 1,
                'price_unit': 10694.70,
                'tax_ids': [self.tax_19.id],
            }), (0, 0, {
                'name': 'Despacho Chilexpress',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 1,
                'price_unit': 6000.0,
                'tax_ids': [self.tax_19.id],
            }), ],
        })

        invoice.action_post()

        self.assertEqual(invoice.state, 'posted')
        self.assertEqual(invoice.l10n_cl_dte_status, 'not_sent')

        xml_expected_dte = misc.file_open(os.path.join(
            'l10n_cl_edi', 'tests', 'expected_dtes', 'dte_39.xml')).read()

        self.assertXmlTreeEqual(
            self.get_xml_tree_from_string(xml_expected_dte.encode()),
            self.get_xml_tree_from_attachment(invoice.l10n_cl_sii_send_file)
        )

    @patch('odoo.addons.l10n_cl_edi.models.l10n_cl_edi_util.L10nClEdiUtilMixin._get_cl_current_strftime')
    def test_l10n_cl_dte_56(self, get_cl_current_strftime):
        get_cl_current_strftime.return_value = '2019-10-24T20:00:00'

        self.tax_19 = self.env['account.tax'].search([
            ('name', '=', 'IVA 19% Venta'),
            ('company_id', '=', self.company_data['company'].id)])

        invoice = self.env['account.move'].with_context(default_move_type='out_invoice').create({
            'partner_id': self.partner_sii.id,
            'move_type': 'out_invoice',
            'invoice_date': '2019-10-23',
            'currency_id': self.env.ref('base.CLP').id,
            'journal_id': self.sale_journal.id,
            'l10n_latam_document_type_id': self.env.ref('l10n_cl.dc_nd_f_dte').id,
            'l10n_latam_document_number': '122',
            'company_id': self.company_data['company'].id,
            'invoice_line_ids': [(0, 0, {
                'name': '[WUS-0558538] Conjunto De Control Electrónico Ps3.39',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 1,
                'discount': 10.00,
                'price_unit': 497804.44,
                'tax_ids': [self.tax_19.id],
            }), (0, 0, {
                'name': '[WUS-0558424A] Vastago Ps 3.39',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 1,
                'price_unit': 171375.56,
                'discount': 10.00,
                'tax_ids': [self.tax_19.id],
            }), (0, 0, {
                'name': '[WUS-0555217] Filtro Malla Acero',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 1,
                'price_unit': 6801.11,
                'discount': 10.00,
                'tax_ids': [self.tax_19.id],
            }), (0, 0, {
                'name': '[WUS-0524421] Retenedor Wagner 339',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 1,
                'price_unit': 19722.22,
                'discount': 10.00,
                'tax_ids': [self.tax_19.id],
            }), (0, 0, {
                'name': '[INSUMO] Insumos Varios',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 2,
                'price_unit': 4760.00,
                'tax_ids': [self.tax_19.id],
            }), (0, 0, {
                'name': '[SERVICIO03] Servicio de Reparación Equipo Airless (Fieldlazer, 695-MarkV, PS3.29-3.39)',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 1,
                'price_unit': 114250.00,
                'tax_ids': [self.tax_19.id],
            }), (0, 0, {
                'name': '[WUS-0558587] Kit Reparación Ps3 .39',
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 1,
                'price_unit': 150973.33,
                'discount': 10.00,
                'tax_ids': [self.tax_19.id],
            }), ],
        })

        invoice.write({
            'l10n_cl_reference_ids': [[0, 0, {
                'move_id': invoice.id,
                'origin_doc_number': 1961,
                'l10n_cl_reference_doc_type_selection': '61',
                'reference_doc_code': '1',
                'reason': 'Anulación NC por aceptación con reparo (N/C 001961)',
                'date': invoice.invoice_date, }, ], ]
        })

        invoice.action_post()

        self.assertEqual(invoice.state, 'posted')
        self.assertEqual(invoice.l10n_cl_dte_status, 'not_sent')

        xml_expected_dte = misc.file_open(os.path.join(
            'l10n_cl_edi', 'tests', 'expected_dtes', 'dte_56.xml')).read()

        self.assertXmlTreeEqual(
            self.get_xml_tree_from_string(xml_expected_dte.encode()),
            self.get_xml_tree_from_attachment(invoice.l10n_cl_dte_file)
        )

    @patch('odoo.addons.l10n_cl_edi.models.l10n_cl_edi_util.L10nClEdiUtilMixin._get_cl_current_strftime')
    def test_l10n_cl_dte_110(self, get_cl_current_strftime):
        get_cl_current_strftime.return_value = '2019-10-22T20:23:27'

        foreign_partner = self.env['res.partner'].create({
            'name': 'Mitchell Admin',
            'country_id': self.env.ref('base.us').id,
            'city': 'Scranton',
            'state_id': self.env.ref('base.state_us_39').id,
            'street': '215 Vine St',
            'phone': '+1 555-555-5555',
            'company_id': self.company_data['company'].id,
            'email': 'admin@yourcompany.example.com',
            'l10n_latam_identification_type_id': self.env.ref('l10n_latam_base.it_pass').id,
            'l10n_cl_sii_taxpayer_type': '4',
            'vat': '123456789',
        })
        currency_usd = self.env.ref('base.USD')
        self.env['res.currency.rate'].create({
            'name': '2019-10-22',
            'company_id': self.company_data['company'].id,
            'currency_id': currency_usd.id,
            'rate': 0.0013})
        invoice = self.env['account.move'].with_context(default_move_type='out_invoice').create({
            'partner_id': foreign_partner,
            'move_type': 'out_invoice',
            'invoice_date': '2019-10-22',
            'currency_id': currency_usd.id,
            'journal_id': self.sale_journal.id,
            'l10n_latam_document_type_id': self.env.ref('l10n_cl.dc_fe_dte').id,
            'company_id': self.company_data['company'].id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product_a.id,
                'product_uom_id': self.product_a.uom_id.id,
                'quantity': 2,
                'price_unit': 5018.75,
            })],
        })

        invoice.action_post()

        self.assertEqual(invoice.state, 'posted')
        self.assertEqual(invoice.l10n_cl_dte_status, 'not_sent')

        xml_expected_dte = misc.file_open(os.path.join(
            'l10n_cl_edi', 'tests', 'expected_dtes', 'dte_110.xml')).read()
        self.assertXmlTreeEqual(
            self.get_xml_tree_from_string(xml_expected_dte.encode()),
            self.get_xml_tree_from_attachment(invoice.l10n_cl_sii_send_file)
        )
