# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import Warning, UserError


class PurchaseRequisition(models.Model):
    _inherit = 'material.purchase.requisition'

    @api.onchange('task_id')
    def onchange_project_task(self):
        for rec in self:
            rec.project_id = rec.task_id.project_id.id
            rec.analytic_account_id = rec.task_id.project_id.analytic_account_id.id

    @api.depends('requisition_line_ids',
                 'requisition_line_ids.product_id',
                 'requisition_line_ids.product_id.boq_type')
    def compute_equipment_machine(self):
        eqp_machine_total = 0.0
        work_resource_total = 0.0
        work_cost_package_total = 0.0
        subcontract_total = 0.0
        for rec in self:
            for line in rec.requisition_line_ids:
                if line.product_id.boq_type == 'eqp_machine':
                    eqp_machine_total += line.product_id.standard_price * line.qty
                if line.product_id.boq_type == 'worker_resource':
                    work_resource_total += line.product_id.standard_price * line.qty
                if line.product_id.boq_type == 'work_cost_package':
                    work_cost_package_total += line.product_id.standard_price * line.qty
                if line.product_id.boq_type == 'subcontract':
                    subcontract_total += line.product_id.standard_price * line.qty
            print ("::::::::::::::::::::::::eqp_machine_total",eqp_machine_total)
            rec.equipment_machine_total = eqp_machine_total
            rec.worker_resource_total = work_resource_total
            rec.work_cost_package_total = work_cost_package_total
            rec.subcontract_total = subcontract_total

    task_id = fields.Many2one(
        'project.task',
        string='Tarea / Orden de Trabajo',
    )
    task_user_id = fields.Many2one(
        'res.users',
        related='task_id.user_id',
        string='Tarea / Orden de Trabajo por Usuario'
    )
    project_id = fields.Many2one(
        'project.project',
        string='Proyecto',
    )
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Orden de Compra',
    )

    purchase_order_ids = fields.Many2many(
        'purchase.order', 
        string='Ordenes de Compra',
    )

    equipment_machine_total = fields.Float(
        compute='compute_equipment_machine',
        string='Maquinaria / Costo de Equipo',
        store=True,
    )
    worker_resource_total = fields.Float(
        compute='compute_equipment_machine',
        string='Recursos / Costo de Trabajo',
        store=True,
    )
    work_cost_package_total = fields.Float(
        compute='compute_equipment_machine',
        string='Costo de Trabajo',
        store=True,
    )
    subcontract_total = fields.Float(
        compute='compute_equipment_machine',
        string='Costo de Subcontrato',
        store=True,
    )
