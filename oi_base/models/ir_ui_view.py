'''
Created on Jan 8, 2020

@author: Zuhair Hammadi
'''
from odoo import models, api
from .arabic_number import amount_to_text_ar, en_to_ar

class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    @api.model
    def _prepare_qcontext(self):
        qcontext = super(IrUiView, self)._prepare_qcontext()
        qcontext.update({
            'en_to_ar' : en_to_ar,
            'amount_to_text_ar' : amount_to_text_ar
            })
        return qcontext
