# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models, api, _
from odoo.exceptions import UserError
try:
    import barcode
    _lib_imported = True
except ImportError:
    _lib_imported = False
import random

import werkzeug.exceptions
import base64


def get_random_number():
    random_num = str(random.randint(10000000000, 99999999999))
    random_first_digit = random.randint(1, 9)
    random_str = str(random_first_digit) + ''.join(map(str, random_num[:11]))
    return random_str


def generate_ean(barcode_type):
    if not _lib_imported:
        raise UserError(_('python-barcode is not installed. Please install it.'))
    EAN = barcode.get_barcode_class(barcode_type)
    ean = EAN(get_random_number())
    return ean.get_fullcode()


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sh_product_barcode_img = fields.Binary(
        string="Barcode Image", readonly=True)

    def action_generate_barcode_image(self):
        self.ensure_one()
        if self.barcode:
            img_barcode = self.env['ir.actions.report'].barcode('Code128', self.barcode, width=500, height=90, humanreadable=0)
            self.sh_product_barcode_img = base64.b64encode(img_barcode)

    def generate_barcode_image(self, ean):
        # generate Barcode image
        try:
            ean_barcode = self.env['ir.actions.report'].barcode(
                'EAN13', ean, width=500, height=90, humanreadable=0)
            if ean_barcode:
                self.sh_product_barcode_img = base64.b64encode(ean_barcode)

        except (ValueError, AttributeError):
            raise werkzeug.exceptions.HTTPException(
                description='Cannot convert into barcode.')

    def action_generate_barcode(self):
        if self:
            for rec in self:
                ean = generate_ean(self.env.company.sh_barcode_type)
                rec.barcode = ean
                rec.generate_barcode_image(ean)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def action_generate_barcode_image(self):
        self.ensure_one()
        if self.barcode:
            img_barcode = self.env['ir.actions.report'].barcode('Code128', self.barcode, width=500, height=90, humanreadable=0)
            self.sh_product_barcode_img = base64.b64encode(img_barcode)

    def action_generate_barcode(self):
        if self:
            for rec in self:
                ean = generate_ean(self.env.company.sh_barcode_type)
                rec.barcode = ean
                rec.generate_barcode_image(ean)

    def generate_barcode_image(self, ean):
        # generate Barcode image
        try:
            ean_barcode = self.env['ir.actions.report'].barcode(
                'EAN13', ean, width=500, height=90, humanreadable=0)
            if ean_barcode:
                self.sh_product_barcode_img = base64.b64encode(ean_barcode)

        except (ValueError, AttributeError):
            raise werkzeug.exceptions.HTTPException(
                description='Cannot convert into barcode.')

    @api.model
    def create(self, vals):
        if not vals.get('barcode', False) and self.user_has_groups('sh_barcode_generator_simple.group_barcode_generator') and self.env.company.generate_barcode_on_product:
            res = super(ProductProduct, self).create(vals)
            ean = generate_ean(self.env.company.sh_barcode_type)
            res.barcode = ean
            res.generate_barcode_image(ean)
            return res
        else:
            res = super(ProductProduct, self).create(vals)
            return res


class GenerateProductBarcode(models.Model):
    _name = 'generate.product.barcode'
    _description = 'Generate Product Barcode'

    # Generate Barcode for Existing Product
    overwrite_existing = fields.Boolean("Overwrite Barcode If Exists")

    def generate_barcode(self):
        if self.user_has_groups('sh_barcode_generator_simple.group_barcode_generator'):

            context = dict(self._context or {})
            active_ids = context.get('active_ids', []) or []
            active_model = context.get('active_model', []) or []

            if active_model == 'product.product':
                for record in self.env['product.product'].browse(active_ids):

                    new_barcode = ''
                    if record.id:
                        new_barcode = generate_ean(
                            self.env.company.sh_barcode_type)
                        if self.overwrite_existing:  # Overwrite existing
                            record.barcode = new_barcode
                            record.generate_barcode_image(new_barcode)
                        else:
                            if not record.barcode:  # If barcode exists,then don't overwrite, Else generate New
                                record.barcode = new_barcode
                                record.generate_barcode_image(new_barcode)

            elif active_model == 'product.template':
                for record in self.env['product.template'].browse(active_ids):
                    new_barcode = ''
                    if record.id:
                        new_barcode = generate_ean(
                            self.env.company.sh_barcode_type)
                        if self.overwrite_existing:  # Overwrite existing
                            record.barcode = new_barcode
                            record.generate_barcode_image(new_barcode)
                        else:
                            if not record.barcode:  # If barcode exists,then don't overwrite, Else generate New
                                record.barcode = new_barcode
                                record.generate_barcode_image(new_barcode)

            return {'type': 'ir.actions.act_window_close'}

        else:
            raise UserError(
                _("You don't have rights to generate product barcode"))
