from odoo import fields, models, api


class ModelName(models.TransientModel):
    _name = 'wiz.update.reason'
    _description = 'Description'

    reject_reason = fields.Text(required=True)

    def update_reject_reason(self):
        man_act = self.env.context.get('active_id', False)
        man = self.env['maintenance.request'].search([('id', '=', man_act)])
        return man.write({'reject_reason': self.reject_reason,
                          'reject_reason_fl': True})
