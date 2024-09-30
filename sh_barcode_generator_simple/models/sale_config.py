# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    generate_barcode_on_product = fields.Boolean(
        string="Generate Product Barcode On Product Create?")

    sh_barcode_type = fields.Selection([
        ('code128', 'Code 128'),
        ('code39', 'Code 39'),
        ('ean', 'EAN'),
        ('ean13', 'EAN-13'),
        ('ean14', 'EAN-14'),
        ('ean8', 'EAN-8'),
        ('isbn10', 'ISBN10'),
        ('isbn13', 'ISBN13'),
        ('issn', 'ISSN'),
        ('jan', 'JAN'),
        ('pzn', 'PZN'),
        ('upca', 'UPCA')
    ], string='Barcode-Type (Product)', translate=True, default='ean13')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    generate_barcode_on_product = fields.Boolean(
        string="Generate Product Barcode On Product Create?", related='company_id.generate_barcode_on_product', translate=True, readonly=False)

    sh_barcode_type = fields.Selection(
        related='company_id.sh_barcode_type', string='Barcode-Type (Product)', translate=True, readonly=False)
