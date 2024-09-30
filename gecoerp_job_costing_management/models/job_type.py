# -*- coding: utf-8 -*-

from odoo import models, fields


class JobType(models.Model):
    _name = 'job.type'
    _description = 'Tipo de Trabajo'

    name = fields.Char(
        string='Nombre',
        required=True,
    )
    code = fields.Char(
        string='Codigo',
        required=True,
    )
    job_type = fields.Selection(
        selection=[
            ('material','Material'),
            ('labour','Labor'),
            ('overhead','Gasto en General')],
        string='Type',
        required=True,
    )
