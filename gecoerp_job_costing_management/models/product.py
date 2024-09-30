# -*- coding: utf-8 -*-

from odoo import models, fields


class Product(models.Model):
    _inherit = 'product.product'

    boq_type = fields.Selection([
        ('eqp_machine', 'Maquinaria / Equipo'),
        ('worker_resource', 'Obrero / Recurso'),
        ('work_cost_package', 'Costo de Trabajo'),
        ('subcontract', 'Subcontratado')],
        string='Tipo de BOQ',
    )
