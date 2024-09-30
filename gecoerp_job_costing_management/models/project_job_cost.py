# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    type_of_construction = fields.Selection(
        [('agricultural','Agricultura'),
        ('residential','Residencial'),
        ('commercial','Comercial'),
        ('institutional','Institucional'),
        ('industrial','Industrial'),
        ('heavy_civil','Obra Civil'),
        ('environmental','Ambiental'),
        ('other','Otro')],
        string='Tipo de Obra'
    )
    location_id = fields.Many2one(
        'res.partner',
        string='Locación'
    )
    notes_ids = fields.One2many(
        'note.note', 
        'project_id', 
        string='Identificador de Notas',
    )
    notes_count = fields.Integer(
        compute='_compute_notes_count', 
        string="Notas",
    )

    @api.depends()
    def _compute_notes_count(self):
        for project in self:
            project.notes_count = len(project.notes_ids)

    def view_notes(self):
        for rec in self:
            res = self.env.ref('gecoerp_job_costing_management.action_project_note_note')
            res = res.read()[0]
            res['domain'] = str([('project_id','in',rec.ids)])
        return res
