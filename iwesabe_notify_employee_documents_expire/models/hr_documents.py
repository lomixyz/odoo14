# -*- coding: utf-8 -*-
from datetime import timedelta,date,datetime
from odoo import models, fields, api, _

class HrDocuments(models.Model):
	_name = 'hr.documents'
	_description = 'Hr Documents'

	name = fields.Char('Document Name')
	employee_id = fields.Many2one('hr.employee','Employee',)
	attachment_ids = fields.Many2many('ir.attachment','hr_documents_rel','doc_id','info_id',string='Attachment Document(s)')
	submit_date = fields.Date('Document Submit Date')
	expiry_date = fields.Date('Expiry Date')
	notify_before = fields.Integer('Notify Before (Days)', default=10)
	tech_notify_before = fields.Integer('Notify Before (Days-For Cron)', default=10)
	company_id = fields.Many2one('res.company', default = lambda self:self.env.company.id)
	state = fields.Selection([('new','New'),('running','Running'),('expired','Expired')], default='new')
	email_sent = fields.Boolean('Email Sent', copy=False)
	
	def action_submit(self):
		for record in self:
			record.tech_notify_before = record.notify_before
			record.state = 'running'

	@api.model
	def create(self, vals):
		result = super().create(vals)
		result._make_public_attachments()
		return result
	
	def write(self, vals):
		result = super().write(vals)
		self._make_public_attachments()
		return result

	def _make_public_attachments(self):
		self = self.sudo()
		for record in self:
			not_public = record.attachment_ids.sudo().filtered(lambda x: not x.public)
			if not_public:
				not_public.sudo().update({
					'public':True
				})
	
	@api.model
	def _send_doc_expiry_notification(self):
		self = self.sudo()
		for document in self.search([('state','=','running')]):
			notification_date = document.expiry_date - timedelta(days=document.tech_notify_before)
			if not document.employee_id.work_email:
				continue
			today = date.today() + timedelta(days=document.notify_before - document.tech_notify_before)
			if notification_date == today:
				if not document.tech_notify_before:
					document._document_expired()
				else:
					document._document_will_be_expired(document.tech_notify_before)
					document.tech_notify_before -= 1
				
	def _document_expired(self):
		subject = "Expired Document - Request for New Document"
		mail_body = """
			<div class="page">
				<div class="container">
					<div style="font-family: Arial, sans-serif; font-size: 14px; color: #333; line-height: 1.5;">
						<p>
							Dear {employee},
						</p>
						<p>
							I hope this email finds you well. I am writing to inform you that we have noticed that your document(s) has expired on {exp_date}.
							This document is a critical requirement for our records, and we request that you submit a new one as soon as possible.
						</p>
						<p>
							To avoid any disruptions to your work, we kindly request you to submit the updated document at your earliest convenience. If you have already renewed your document, please send us a scanned copy of the updated one.
						</p>
						<p>
							In case you have any questions or concerns, please do not hesitate to reach out to me or our HR department.
						</p>
						<p>
							Best regards,
						</p>
						<p>
							{company_name}
						</p>
						<p>
							[Attachment: Expired Document]
						</p>
					</div>
				</div>
			</div>
		""".format(employee = self.employee_id.name,exp_date=str(self.expiry_date),company_name=self.company_id.name)
		mail_id = self.env['mail.mail'].create({
			'subject':subject,
			'email_from':self.company_id.email,
			'email_to':self.employee_id.work_email,
			'body_html':mail_body,
			'attachment_ids':[(6,0,self.attachment_ids.ids)]
		})
		mail_id.sudo().send()
		self.state = 'expired'
		self.email_sent = False

	def _document_will_be_expired(self, days):
		subject = "Document Expiry - Request for New Document"
		mail_body = """
			<div class="page">
				<div class="container">
					<div style="font-family: Arial, sans-serif; font-size: 14px; color: #333; line-height: 1.5;">
						<p>
							Dear {employee},
						</p>
						<p>
							I hope this email finds you well. I am writing to inform you that we have noticed that your document(s) is about to expire on {exp_date}. This document is a critical requirement for our records, and we request that you submit a new one as soon as possible.
						</p>
						<p>
							To avoid any disruptions to your work, we kindly request you to submit the updated document at your earliest convenience. Please find attached a copy of the document that is about to expire for your reference.
						</p>
						<p>
							If you have already renewed your document, please send us a scanned copy of the updated one.
						</p>
						<p>
							In case you have any questions or concerns, please do not hesitate to reach out to me or our HR department.
						</p>
						<p>
							Best regards,
						</p>
						<p>
							{company_name}
						</p>
						<p>
							[Attachment: Document About to Expire]
						</p>
					</div>
				</div>
			</div>
		""".format(employee = self.employee_id.name,exp_date=str(self.expiry_date),company_name=self.company_id.name)
		mail_id = self.env['mail.mail'].create({
			'subject':subject,
			'email_from':self.company_id.email,
			'email_to':self.employee_id.work_email,
			'body_html':mail_body,
			'attachment_ids':[(6,0,self.attachment_ids.ids)]
		})
		mail_id.sudo().send()
		self.email_sent = True