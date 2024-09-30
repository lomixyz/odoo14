# Copyright 2015 Oihane Crucelaegui
# Copyright 2015-2019 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html.html

from email.policy import default
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = ["product.template"]

    def get_company_domain(self):
        return [('id', 'in',  self._context.get('allowed_company_ids'))]
    
    company_id = fields.Many2one('res.company', 'Company', index=True ,default=lambda self: self.env.company ,domain = get_company_domain)
class ResPartner(models.Model):
    _inherit = ["product.product"]

    def get_company_domain(self):
        return [('id', 'in',  self._context.get('allowed_company_ids'))]
    
    company_id = fields.Many2one('res.company', 'Company', index=True ,default=lambda self: self.env.company ,domain = get_company_domain)
