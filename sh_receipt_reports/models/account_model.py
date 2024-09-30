# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models,fields,api,_


class account_invoice(models.Model):
    _inherit = "account.move"
    
    
    # @api.multi
    def sh_rr_get_printed_report_name(self):
        self.ensure_one()
        return  self.type == 'out_invoice' and self.state == 'draft' and _('Draft Invoice Receipt') or \
                self.type == 'out_invoice' and self.state in ('open','paid') and _('Invoice Receipt - %s') % (self.number) or \
                self.type == 'out_refund' and self.state == 'draft' and _('Credit Note Receipt') or \
                self.type == 'out_refund' and _('Credit Note Receipt - %s') % (self.number) or \
                self.type == 'in_invoice' and self.state == 'draft' and _('Vendor Bill Receipt') or \
                self.type == 'in_invoice' and self.state in ('open','paid') and _('Vendor Bill Receipt - %s') % (self.number) or \
                self.type == 'in_refund' and self.state == 'draft' and _('Vendor Credit Note Receipt') or \
                self.type == 'in_refund' and _('Vendor Credit Note Receipt - %s') % (self.number)
    