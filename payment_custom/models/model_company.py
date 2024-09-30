

from odoo import models , fields


class ResPartnerCustom(models.Model):
    _inherit = 'res.partner'

    company_id = fields.Many2one('res.company', string='Company', readonly=True,
            default=lambda self: self.env.company)


class ProductTemplateCustom(models.Model):
    _inherit = 'product.template'

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
            default=lambda self: self.env.company)


class ProductProductCustom(models.Model):
    _inherit = 'product.product'

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
            default=lambda self: self.env.company)


class ProductCategoryCustom(models.Model):
    _inherit = 'product.category'

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
            default=lambda self: self.env.company)
