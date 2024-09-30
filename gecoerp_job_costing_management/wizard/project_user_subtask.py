# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectUserSubtask(models.TransientModel):
    _name = 'project.user.subtask'
    _description = 'Subtarea de Usuario del Proyecto'

    subtask_user_ids = fields.One2many(
        'user.subtask', 
        'subtask_id',
        string="Usuario de la Subtarea del Proyecto",
        required=True,
    )
    
    def create_subtask(self):
        task_id = self._context.get('active_id', False)
        task = self.env['project.task'].browse(task_id)
        subtask_ids = []
        for subtask in self.subtask_user_ids:
            vals = {
                'planned_hours' : subtask.planned_hours,
                'description'   : subtask.description,
                'user_id'       : subtask.user_id.id,
                'name'          : subtask.name,
                'parent_task_id' : task.id,
                'parent_id'      : task.id,
                'project_id'     : task.project_id.id,
                'company_id'     : task.company_id.id,
            }
            copy_task_vals = self.env['project.task'].create(vals)
            subtask_ids.append(copy_task_vals.id)
        if subtask_ids:
            result = self.env.ref('project.project_task_action_sub_task')
            result = result.read()[0]
            result['domain'] = "[('id','in',[" + ','.join(map(str, subtask_ids)) + "])]"
            return result
        return True
    
class UserSubtask(models.TransientModel):
    _name = 'user.subtask'
    _description = 'Subtarea de Usuario'
    
    user_id = fields.Many2one(
        'res.users',
        string="Usuarios",
        required=True,
    )
    name = fields.Char(
        string='Nombre de la Tarea',
        required=True,
    )
    description = fields.Text(
        string='Descripción de la Tarea',
        required=True,
    )
    planned_hours = fields.Float(
        'Planned Hours',
        required=True,
    )
    subtask_id = fields.Many2one(
        'project.user.subtask',
        string='Project User Subtask'
    )
