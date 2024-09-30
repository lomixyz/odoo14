# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    sh_sec_uom = fields.Many2one(
        comodel_name="uom.uom", string="Secondary UOM")
    sh_sec_qty = fields.Float('Secondary Qty', readonly=True)

    def _select(self):
        select_str = super()._select()
        select_str += """
            ,sh_sec_uom as sh_sec_uom, sh_sec_qty as sh_sec_qty
            """
        return select_str

    def _sub_select(self):
        select_str = super()._sub_select()
        select_str += """
            ,sh_sec_uom, sh_sec_qty
            """
        return select_str

    def _group_by(self):
        group_by_str = super()._group_by()
        group_by_str += ",sh_sec_uom, sh_sec_qty"
        return group_by_str
