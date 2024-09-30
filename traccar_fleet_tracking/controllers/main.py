# -*- coding: utf-8 -*-
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2017 BulkTP
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from odoo import http, SUPERUSER_ID, _
from odoo.http import request

from datetime import datetime
import pytz
from pytz import timezone
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
import logging

_logger = logging.getLogger(__name__)


class WebsiteForm(http.Controller):

    @http.route(['/traccar_positions/<int:device_id>/<float:latitude>/<float:longitude>/<string:fixTime>'], type='http',
                auth='none')
    def register_positions(self, device_id, latitude, longitude, fixTime):
        if request.env['ir.config_parameter'].sudo().get_param('real_time_tracking', default=False):
            fixTime = datetime.fromtimestamp(int(fixTime) / 1000).strptime(DATETIME_FORMAT)

            # get user's timezone
            user_db = request.env['res.users'].sudo()
            user = user_db.browse(SUPERUSER_ID)
            if user.partner_id.tz:
                tz = timezone(user.partner_id.tz) or timezone('UTC')
            else:
                tz = timezone('UTC')

            fixTime = tz.localize(fixTime)
            fixTime = fixTime.astimezone(pytz.utc)

            vehicle = request.env['fleet.vehicle'].sudo().search([('traccar_device_id', '=', int(device_id))], limit=1)
            if vehicle and vehicle.vehicle_latitude != round(float(latitude), 5) and vehicle.vehicle_longitude != round(
                    float(longitude), 5):
                location_history_ids = [(0, 0, {
                    'vehicle_latitude': float(latitude),
                    'vehicle_longitude': float(longitude),
                    'date_localization': fixTime,
                    'name': vehicle.name,
                    'driver_name': vehicle.driver_id and vehicle.driver_id.name or '-'
                })]
                vehicle.sudo().write({
                    'vehicle_latitude': latitude,
                    'vehicle_longitude': longitude,
                    'date_localization': fixTime,
                    'location_history_ids': location_history_ids
                })
        return request.not_found()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
