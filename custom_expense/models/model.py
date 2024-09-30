from odoo import fields, models, api


class HrExpense(models.Model):
    _inherit = ['hr.expense']

    @api.model
    def get_empty_list_help(self, help):
        if self.env.user.has_group('hr_expense.group_hr_expense_manager') and (
                not isinstance(help, str) or "o_view_nocontent_empty_folder" not in help):
            action_id = self.env.ref('hr_expense_extract.action_expense_sample_receipt').id
            return """
    <p class="o_view_nocontent_expense_receipt">
        WAY IST
    </p>
    """ % {'action_id': action_id, 'mail_alias': self._get_empty_list_mail_alias()}
        return super().get_empty_list_help(help)