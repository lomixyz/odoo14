# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api


class Timesheet(models.Model):
    _inherit = 'account.analytic.line'

    ticket_id = fields.Many2one('helpdesk.ticket', string='Helpdesk Ticket')
    start_date = fields.Datetime("Start Date")
    end_date = fields.Datetime("End Date")

    def _get_duration(self, start_date, end_date):
        """ Get the duration value between the 2 given dates. """
        if end_date and start_date:
            diff = fields.Datetime.from_string(
                end_date) - fields.Datetime.from_string(start_date)
            if diff:
                unit_amount = float(diff.days) * 24 + \
                    (float(diff.seconds) / 3600)

                return round(unit_amount, 2)
            return 0.0

    @api.onchange('start_date', 'end_date')
    def onchange_duration_custom(self):
        if self and self.start_date and self.end_date:
            start_date = self.start_date
            date = start_date.date()
            self.date = date
            self.unit_amount = self._get_duration(
                self.start_date, self.end_date)
