'''
Created on Oct 4, 2021

@author: Zuhair Hammadi
'''
from odoo import models, fields

class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'
    
    default_ids = fields.One2many('ir.default', 'field_id', string = 'User-defined Defaults')