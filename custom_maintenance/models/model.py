from odoo import fields, models, api, _


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    cost = fields.Float()
    date_preview = fields.Date()
    date_in_progress = fields.Date()
    preview_note = fields.Html(string='Note')
    location_id = fields.Many2one('location.location', string='Location', required=True)
    type_of_maintenance = fields.Text()
    damage_type = fields.Selection(
        string='Damage Type',
        selection=[('manufacture_defect', 'Manufacture Defect'),
                   ('consumption_defect', 'Consumption Defect'),
                   ('misuse', 'Misuse')])

    state = fields.Selection(selection=[
        ('draft', 'New Request'),
        ('status', 'Order Status'),
        ('preview', 'Preview'),
        ('in_progress', 'In Progress'),
        ('evaluation', 'Evaluation'),
        ('close', 'Close'),
    ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')
    new_note = fields.Html(string='Note', required=True)
    status_note = fields.Html(string='Note')
    evaluation = fields.Html(string='Note')
    reject_reason = fields.Text(string='Reject Reason')
    reject_reason_fl = fields.Boolean(string='Reject Reason', default=False)
    new_attachment_ids = fields.Many2many('ir.attachment', string='Attachment', ondelete='cascade', required=True)
    partner_id = fields.Many2one('res.partner', string='Vendor')
    product_id = fields.Many2one('product.product', string='Product')
    warranty = fields.Float('Warranty')

    def action_confirm(self):
        return self.write({'state': 'status'})

    def action_approve(self):
        return self.write({'state': 'preview'})

    def action_preview(self):
        return self.write({'state': 'in_progress'})

    def action_evaluation(self):
        return self.write({'state': 'evaluation'})

    def action_close(self):
        return self.write({'state': 'close'})

    def action_reject(self):
        return {
            'view_mode': 'form',
            'view_id': self.env.ref('custom_maintenance.wiz_update_reason').id,
            'res_model': 'wiz.update.reason',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': False,
        }


class Location(models.Model):
    _name = 'location.location'
    _description = 'vehicles location'

    name = fields.Char()
