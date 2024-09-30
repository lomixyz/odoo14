# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrEmployeePrivate(models.Model):
    _inherit = 'hr.employee'

    plan_to_change_car = fields.Boolean('Plan To Change Car', default=False)

class FleetVehicleInh(models.Model):
    _inherit = 'fleet.vehicle'

    driver_id = fields.Many2one('hr.employee', 'Driver', tracking=True, help='Driver of the vehicle', copy=False)
    # future_driver_id = fields.Many2one('hr.employee', 'Future Driver', tracking=True, help='Next Driver of the vehicle', copy=False, )
    

    # @api.model
    # def create(self, vals):
    #     # Fleet administrator may not have rights to create the plan_to_change_car value when the driver_id is a res.user
    #     # This trick is used to prevent access right error.
    #     ptc_value = 'plan_to_change_car' in vals.keys() and {'plan_to_change_car': vals.pop('plan_to_change_car')}
    #     res = super(FleetVehicleInh, self).create(vals)
    #     if ptc_value:
    #         res.sudo().write(ptc_value)
    #     if 'driver_id' in vals and vals['driver_id']:
    #         res.create_driver_history(vals['driver_id'])
    #     if 'future_driver_id' in vals and vals['future_driver_id']:
    #         state_waiting_list = self.env.ref('fleet.fleet_vehicle_state_waiting_list', raise_if_not_found=False)
    #         states = res.mapped('state_id').ids
    #         if not state_waiting_list or state_waiting_list.id not in states:
    #             future_driver = self.env['hr.employee'].browse(vals['future_driver_id'])
    #             future_driver.sudo().write({'plan_to_change_car': True})
    #     return res

    # def write(self, vals):
    #     if 'driver_id' in vals and vals['driver_id']:
    #         driver_id = vals['driver_id']
    #         self.filtered(lambda v: v.driver_id.id != driver_id).create_driver_history(driver_id)

    #     if 'future_driver_id' in vals and vals['future_driver_id']:
    #         state_waiting_list = self.env.ref('fleet.fleet_vehicle_state_waiting_list', raise_if_not_found=False)
    #         states = self.mapped('state_id').ids if 'state_id' not in vals else [vals['state_id']]
    #         if not state_waiting_list or state_waiting_list.id not in states:
    #             future_driver = self.env['hr.employee'].browse(vals['future_driver_id'])
    #             future_driver.sudo().write({'plan_to_change_car': True})

    #     res = super(FleetVehicleInh, self).write(vals)
    #     if 'active' in vals and not vals['active']:
    #         self.mapped('log_contracts').write({'active': False})
    #     return res



# class FleetVehicleAssignationLog(models.Model):
#     _inherit = "fleet.vehicle.assignation.log"

#     driver_id = fields.Many2one('hr.employee', string="Driver", required=True)
