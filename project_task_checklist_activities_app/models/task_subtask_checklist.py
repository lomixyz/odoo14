# -*- coding: utf-8 -*-

from odoo import _,api, fields, models
from odoo.exceptions import UserError, ValidationError

class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    checklist_task_progress_restriction = fields.Boolean(string ='Restriction To Checklist Task Progress')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.ref('base.main_company').id, required=True)
    task_progress_restriction = fields.Selection([
        ('no_restriction', 'No Task Progress Restriction'),
        ('restriction', 'Restriction To Task Progress Before All Checklist Completion')
        ],related='company_id.task_progress_restriction'
        )


class ChecklistActivityStage(models.Model):
    _name = "checklist.activity.stage"
    _description = "Checklist Activity Stage"

    name = fields.Char(string='Name',required=True)
    sequence = fields.Integer(string='Sequence')
    default_stage = fields.Char(string='Default Stage')
    is_dft_stage = fields.Boolean("Is Default Stage")

    _sql_constraints = [
            ('unique_sequence', 'unique (sequence)', 'You can not create record for same sequence.!!!')
        ]


class TaskChecklist(models.Model):
    _name = "task.checklist"
    _description = "Task Checklist"

    name = fields.Char(string='Name', required=True)
    description = fields.Char(string='Description')
    project_id = fields.Many2one('project.project', string ='Project', required=True)
    activities_ids = fields.One2many('checklist.activity','task_checklist_id',string="Checklist Activity")

class ProjectActivities(models.Model):
    _name = "checklist.activity"
    _description = "Project Activities"

    task_checklist_id = fields.Many2one('task.checklist', string ='Task Checklist')
    name = fields.Char(string='Name')
    description = fields.Char(string='Description')
    stage_id = fields.Many2one('checklist.activity.stage', string ='Stage')
    user_id = fields.Many2one('res.users',
        string='Assigned to',
        default=lambda self: self.env.user.id,
        index=True, track_visibility='always')

class ProjectTask(models.Model):
    _inherit = "project.task"

    checklist_id = fields.Many2one('task.checklist', string ='Checklist', domain="[('project_id','=',project_id)]")
    checklist_master_ids = fields.One2many('checklist.master','project_task_id',string="Checklist Activity")
    task_activity = fields.Float(compute='_compute_activity',string="Checklist Progress" , store=True)
    
    @api.depends('checklist_master_ids.stage_id')
    def _compute_activity(self):
        for record in self:
            completed_task = []
            total_task = []
            for task in record.checklist_master_ids:
                total_task.append(task)
                if task.stage_sequence == 10:
                    completed_task.append(task.stage)
            if len(total_task) != 0:
                progress = (len(completed_task)/len(total_task))*100
                record.task_activity = progress

    def write(self, values):
        currenet_stage = []
        currenet_stage.append(self.stage_id.id)
        result = super(ProjectTask, self).write(values)
            
        res_config_settings = self.env['res.config.settings'].sudo().search([('task_progress_restriction', '=', 'restriction')])   
        if res_config_settings:
            project_task_type = self.env['project.task.type'].search([('checklist_task_progress_restriction', '=', True)])
            x = [a.name for a in self.checklist_master_ids if a.stage_sequence != 10 and a.stage_sequence != 11]
            x = ','.join(map(str, x))

            if values.get('stage_id'):
                if currenet_stage[0] > values.get('stage_id'):
                    raise ValidationError(_("You Can Not Go Back!"))    

            for task_type in project_task_type:
                for act in self.checklist_master_ids:
                    if act.stage_sequence != 10 and act.stage_sequence != 11:
                        if values.get('stage_id'):
                            if self.stage_id.name == task_type.name:
                                raise ValidationError(_("You Can Not Change State for the task '%s' Because %s Activities are not Completed or not Cancelled!")% (self.name,x))     
        return result

    @api.onchange('checklist_id')
    def task_compute(self):
        for i in self:
            i.checklist_master_ids = [(5,0,0)]
        task_checklist = self.env['task.checklist'].search([('id', '=', self.checklist_id.id)])
        
        lines = []
        for activity in task_checklist.activities_ids:
            vals = {'name':activity.name,
                    'description':activity.description,
                    'stage' : activity.stage_id.name,
                    'stage_id' : activity.stage_id.id,
                    'user_id' : activity.user_id.id,
                    }
            lines.append((0,0,vals))
        self.checklist_master_ids = lines   
  

class ChecklistMaster(models.Model):
    _name = "checklist.master"
    _description = "Checklist Master"

    project_task_id = fields.Many2one('project.task', string ='Task')
    project_id = fields.Many2one('project.project',related='project_task_id.project_id', string ='Project',store=True)
    name = fields.Char(string='Name',required=True)
    description = fields.Char(string='Description')
    stage_sequence = fields.Integer(string='Stage Sequence')
    user_id = fields.Many2one('res.users',
        string='Assigned to',
        default=lambda self: self.env.user.id,
        index=True, track_visibility='always')
    stage_id = fields.Many2one('checklist.activity.stage', string ='Stage')
    stage = fields.Char(string='stage')
    related_stage = fields.Char(string='Stage Operation')

    @api.model
    def create(self, vals):
        stage = vals.get('stage_id')
        activity_stage = self.env['checklist.activity.stage'].search([('id', '=', stage)])
        vals.update({'stage':activity_stage.name})
        for i in self:
            i.stage = activity_stage.name
        return super(ChecklistMaster, self).create(vals)


    def is_check(self):
        activity_stage = self.env['checklist.activity.stage'].search([('sequence', '=', 9)],limit=1)
        self.stage = activity_stage.name
        self.related_stage = activity_stage.name
        self.stage_id = activity_stage.id
        self.stage_sequence = activity_stage.sequence

    def is_right(self):
        activity_stage = self.env['checklist.activity.stage'].search([('sequence', '=', 10)],limit=1)
        self.related_stage = activity_stage.name
        self.stage = activity_stage.name
        self.stage_id = activity_stage.id
        self.stage_sequence = activity_stage.sequence
    
    def is_close(self):
        activity_stage = self.env['checklist.activity.stage'].search([('sequence', '=', 11)],limit=1)
        self.stage = activity_stage.name
        self.related_stage = activity_stage.name
        self.stage_id = activity_stage.id
        self.stage_sequence = activity_stage.sequence

    def is_refresh(self):
        activity_stage = self.env['checklist.activity.stage'].search([('sequence', '=', 1)],limit=1)
        self.stage = activity_stage.name
        self.related_stage = activity_stage.name
        self.stage_id = activity_stage.id
        self.stage_sequence = activity_stage.sequence

class ActivityCount(models.Model):
    _inherit = "project.project"

    activities_count = fields.Integer(string="Activity Count", compute='_compute_activity_count', store = True)
    label_act = fields.Char(string='Use Activity as', default=lambda s: _('Activity'), translate=True,
        help="Gives label to tasks on project's kanban view.")

    @api.depends('task_ids.checklist_master_ids.stage_id')
    def _compute_activity_count(self):
        for project in self:
            project_task = self.env['project.task'].search([('project_id','=',project.id)])
            task_act = []
            project_task_act = []
            for task in project_task:
                if task.project_id.name == project.name:
                    for activity in task.checklist_master_ids:
                        task_act.append(activity.name)
                        task_activities = len(task_act)
                        project.activities_count = task_activities  

    def open_activites(self):
        return {
                'name': _('Activities'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'checklist.master',
                'type': 'ir.actions.act_window',
                'domain' :[('project_id', '=', self.id)],
             
            }
