# -*- coding: utf-8 -*-

from odoo import models, api ,_
from odoo.exceptions import ValidationError 

class ResPartner(models.Model):
    _inherit = 'res.partner'


    @api.constrains('phone')
    def _check_phone(self):
        for record in self:
            partner = self.env['res.partner'].search([
                ('phone', '=', record.phone)
            ])
            if len(partner)>1:
                raise ValidationError(_("The Phone Most Be Unique"))
