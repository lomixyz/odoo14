'''
Created on Jan 14, 2021

@author: Zuhair Hammadi
'''
from odoo import models

class IrTranslation(models.Model):
    _inherit = "ir.translation"
    
    def _modified(self):
        super(IrTranslation, self)._modified()        
        self.flush()
        
        for trans in self:
            if trans.type in ['model','model_terms'] and trans.res_id and trans.name and ',' in trans.name:
                model, field = trans.name.split(',')
                if model in self.env:
                    model = self.env[model].with_context(lang = trans.lang)
                    if field in model._fields:
                        field = model._fields[field]
                        record = model.browse(trans.res_id)
                        record.modified([field.name])                        
                        record.flush()
