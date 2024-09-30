# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrEmployee(models.Model):
	_inherit = 'hr.employee'

	def action_add_emp_doc(self):
		action = self.env["ir.actions.actions"]._for_xml_id("iwesabe_notify_employee_documents_expire.action_hr_documents")
		form_view = [(self.env.ref('iwesabe_notify_employee_documents_expire.form_hr_documents').id, 'form')]
		action['views'] = form_view
		action['context'] = {'default_employee_id':self.id}
		return action

