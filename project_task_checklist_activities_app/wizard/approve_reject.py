# -*- coding: utf-8 -*-

from odoo import _,api, fields, models

class ApproveReject(models.TransientModel):
    _name = "approve.reject"

    skip_record = fields.Boolean(string ='Skip Records In Complete And Cancel State')
    
    def mark_complete(self):
        alltask_activity = self.env['checklist.master'].browse(self._context.get('active_ids'))
        completed_stage = self.env['checklist.activity.stage'].search([('sequence', '=', 10)],limit=1)
        cancelled_stage = self.env['checklist.activity.stage'].search([('sequence', '=', 11)],limit=1)
        for activity in alltask_activity:
            if self.skip_record == True:
                if activity.stage_sequence == 10:
                    activity.stage = completed_stage.name
                    activity.stage_id = completed_stage.id
                elif activity.stage_sequence == 11:
                    activity.stage = cancelled_stage.name
                    activity.stage_id = cancelled_stage.id
                elif activity.stage_sequence != 10 and activity.stage != 11:
                    activity.stage = completed_stage.name
                    activity.stage_id = completed_stage.id
                    activity.stage_sequence = 10
            else:
                activity.stage = completed_stage.name
                activity.stage_id = completed_stage.id
                activity.stage_sequence = 10
                
    def mark_cancel(self):
        alltask_activity = self.env['checklist.master'].browse(self._context.get('active_ids'))
        completed_stage = self.env['checklist.activity.stage'].search([('sequence', '=', 10)], limit=1)
        cancelled_stage = self.env['checklist.activity.stage'].search([('sequence', '=', 11)], limit=1)
        for activity in alltask_activity:
            if self.skip_record == True:
                if activity.stage_sequence == 10:
                    activity.stage = completed_stage.name
                    activity.stage_id = completed_stage.id
                elif activity.stage_sequence == 11:
                    activity.stage = cancelled_stage.name
                    activity.stage_id = cancelled_stage.id
                elif activity.stage_sequence != 10 and activity.stage_sequence != 11:
                    activity.stage = cancelled_stage.name
                    activity.stage_id = cancelled_stage.id
                    activity.stage_sequence = 11
                    
            else:
                activity.stage = cancelled_stage.name
                activity.stage_id = cancelled_stage.id
                activity.stage_sequence = 11
