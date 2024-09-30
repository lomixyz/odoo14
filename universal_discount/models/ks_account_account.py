from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class Company(models.Model):
    _inherit = "res.company"

    ks_enable_discount = fields.Boolean(string="Activate Universal Discount")
    ks_product_discount = fields.Many2one('product.product', string="Discount Product")


class KSResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ks_enable_discount = fields.Boolean(string="Activate Universal Discount", related='company_id.ks_enable_discount', readonly=False)
    ks_product_discount = fields.Many2one('product.product', string="Discount Product", related='company_id.ks_product_discount', readonly=False)
