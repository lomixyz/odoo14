# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import requests
import logging

import datetime
import pytz
from pytz import timezone
from bokeh.plotting import gmap
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import (GMapPlot, GMapOptions, ColumnDataSource, Line, Circle,
                          Range1d, PanTool, WheelZoomTool, HoverTool, SaveTool)

from odoo import api, fields, models, tools, osv, exceptions, SUPERUSER_ID, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


def get_last_position(cookie, device_id):
    params = {
        'uniqueID': device_id,
        'from': '2000-01-01T00:00:00.000Z',
        'to': '2050-01-01T00:00:00.000Z',
    }
    headers = {
        'Cookie': cookie[0],
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    response = requests.get(cookie[1] + '/api/positions', headers=headers, params=params)
    result = 0, 0, None, None

    for position in response.json():
        if position['deviceId'] == device_id:
            totalDistance = 0
            if 'attributes' in position and position['attributes'].get('totalDistance', False): totalDistance = \
                position['attributes'].get('totalDistance', 0)
            time_test = datetime.datetime.strptime(position['fixTime'], '%Y-%m-%dT%H:%M:%S.000+00:00')
            result = float(position['latitude']), float(position['longitude']), time_test, totalDistance
    return result


class FleetVehicleLastLocation(models.TransientModel):
    _name = "fleet.vehicle.last.location"
    _description = 'Vehicle Last Location on the Map'

    @api.depends('vehicle_id')
    def _compute_bokeh_chart(self):
        for rec in self:
            map_options = GMapOptions(lat=rec.vehicle_id.vehicle_latitude or 0,
                                      lng=rec.vehicle_id.vehicle_longitude or 0, map_type="roadmap",
                                      zoom=11)

            # For GMaps to function, Google requires you obtain and enable an API key:
            #     https://developers.google.com/maps/documentation/javascript/get-api-key
            gmaps_api_key = self.env['ir.config_parameter'].sudo().get_param('base_geolocalize.google_map_api_key')
            print('//////////////////////////', gmaps_api_key)
            if not gmaps_api_key:
                raise UserError(
                    _("You have not entered a Google Maps API key (under Fleet - Traccar Settings), please do so to view map views."))
            p = gmap(gmaps_api_key, map_options, title="Last Map Location")

            source = ColumnDataSource(
                data=dict(lat=[rec.vehicle_id.vehicle_latitude or 0],
                          lon=[rec.vehicle_id.vehicle_longitude or 0])
            )

            p.circle(x="lon", y="lat", size=15, fill_color="blue", fill_alpha=0.8, source=source)
            p.add_tools(SaveTool())
            # p.sizing_mode = 'scale_width'

            # Get the html components and convert them to string into the field.
            script, div = components(p)
            rec.bokeh_last_location = '%s%s' % (div, script)

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True)
    bokeh_last_location = fields.Text(
        string='Trip',
        compute=_compute_bokeh_chart, track_visibility='always')


class FleetVehicleLocationHistory(models.Model):
    _name = "fleet.vehicle.location.history"
    _order = 'date_localization desc'
    _description = 'Vehicle Location History'

    def _compute_inactive(self):
        for rec in self:
            rec.inactive_period = False
            if not rec.vehicle_id or (
                    rec.vehicle_latitude == 0 and rec.vehicle_longitude == 0) or not rec.date_localization:
                continue

            ir_config_param = self.env['ir.config_parameter'].sudo()
            inactivity_period_duration = ir_config_param.get_param('inactivity_period_duration', default='30')
            on_date = rec.date_localization
            date_localization_from = on_date - datetime.timedelta(minutes=int(inactivity_period_duration))

            all_history_records = self.search(
                [('vehicle_id', '=', rec.vehicle_id.id), ('date_localization', '>=', date_localization_from),
                 ('date_localization', '<=', rec.date_localization)])
            if all_history_records:
                inactive = False
                for h in all_history_records:
                    if round(h.vehicle_latitude, 4) != round(rec.vehicle_latitude, 4) or round(h.vehicle_longitude,
                                                                                               4) != round(
                        rec.vehicle_longitude, 4):  # if locations are close enough
                        inactive = False
                        break
                    else:
                        inactive = True
                if inactive: rec.inactive_period = True

    @api.depends('date_localization')
    def _compute_bokeh_chart(self):
        for rec in self:
            on_date = self.date_localization
            day_after = on_date + datetime.timedelta(days=1)

            day_points = self.env['fleet.vehicle.location.history'].search([('vehicle_id', '=', self.vehicle_id.id),
                                                                            ('date_localization', '<', day_after),
                                                                            ('date_localization', '>=', on_date)])
            if not day_points:
                # no data
                return

            data = {
                'lat': [],
                'lon': [],
                'info': []
            }
            for point in day_points:
                data['lat'].append(point.vehicle_latitude)
                data['lon'].append(point.vehicle_longitude)
                data['info'].append(point.driver_name + ' - ' + point.date_localization.strftime("%Y-%m-%d %H:%M:%S"))

            map_options = GMapOptions(lat=rec.vehicle_latitude,
                                      lng=rec.vehicle_longitude, map_type="roadmap", zoom=11)

            gmaps_api_key = self.env['ir.config_parameter'].sudo().get_param('base_geolocalize.google_map_api_key')
            if not gmaps_api_key:
                raise UserError(_(
                    "You have not entered a Google Maps API key (under Fleet - Traccar Settings), please do so to view map views."))
            p = GMapPlot(api_key=gmaps_api_key, x_range=Range1d(),
                         y_range=Range1d(), map_options=map_options)  # , title="My Drive")

            source = ColumnDataSource(data=dict(lat=data['lat'], lon=data['lon'],
                                                info=data['info'], ))

            path = Line(x="lon", y="lat", line_width=3, line_color='blue', line_alpha=0.8)
            car = Circle(x="lon", y="lat", size=10, fill_color='red', fill_alpha=0.9)

            # p = figure(title="PNG Highlands Earthquake 7.5 Affected Villages", y_range=(-4.31509, -7.0341),
            #           x_range=(141.26667, 145.56598))
            # p.xaxis.axis_label = 'longitude'
            # p.yaxis.axis_label = 'latitude'

            p.add_glyph(source, path)
            source = ColumnDataSource(data=dict(lat=[rec.vehicle_latitude], lon=[rec.vehicle_longitude],
                                                info=[rec.driver_name + ' - ' + rec.date_localization.strftime(
                                                    "%Y-%m-%d %H:%M:%S")]))
            p.add_glyph(source, car)
            p.add_tools(PanTool(), WheelZoomTool(), SaveTool(),
                        HoverTool(tooltips=[("Info", "@info"), ]))
            p.sizing_mode = 'scale_width'
            p.toolbar.active_scroll = "auto"

            script, div = components(p)
            rec.trip = '%s%s' % (div, script)
            rec.on_date = on_date.date()

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True)
    name = fields.Char(string='Name', required=True)
    driver_name = fields.Char(string='Driver Name')
    image_128 = fields.Image(related='vehicle_id.image_128', string="Logo (small)")
    vehicle_latitude = fields.Float(string='Geo Latitude', digits=(16, 5))
    vehicle_longitude = fields.Float(string='Geo Longitude', digits=(16, 5))
    date_localization = fields.Datetime(string='Located on')
    inactive_period = fields.Boolean(string='Inactive Period', compute='_compute_inactive', store=False)

    on_date = fields.Date(string='On Date', compute=_compute_bokeh_chart)
    all_day = fields.Boolean(string='All Day', default=True)
    trip = fields.Text(
        string='Trip',
        compute=_compute_bokeh_chart)


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    def _compute_bokeh_chart(self):
        for rec in self:
            map_options = GMapOptions(lat=rec.vehicle_latitude or 0, lng=rec.vehicle_longitude or 0, map_type="roadmap",
                                      zoom=11)

            # For GMaps to function, Google requires you obtain and enable an API key:
            #     https://developers.google.com/maps/documentation/javascript/get-api-key
            gmaps_api_key = self.env['ir.config_parameter'].sudo().get_param('base_geolocalize.google_map_api_key')
            if not gmaps_api_key:
                raise UserError(
                    _("You have not entered a Google Maps API key (under Fleet - Traccar Settings), please do so to view map views."))
            p = gmap(gmaps_api_key, map_options, title="Last Map Location")

            source = ColumnDataSource(
                data=dict(lat=[rec.vehicle_latitude or 0],
                          lon=[rec.vehicle_longitude or 0])
            )

            p.circle(x="lon", y="lat", size=15, fill_color="blue", fill_alpha=0.8, source=source)
            p.add_tools(PanTool(), WheelZoomTool(), SaveTool())
            p.sizing_mode = 'scale_width'

            # Get the html components and convert them to string into the field.
            script, div = components(p)
            rec.bokeh_last_location = '%s%s' % (div, script)

    def _reverse_geocode(self):
        ir_config_param = self.env['ir.config_parameter'].sudo()
        do_reverse_geocoding = ir_config_param.get_param('do_reverse_geocoding') or False
        if do_reverse_geocoding:
            for record in self:
                result = ''
                base = "https://maps.googleapis.com/maps/api/geocode/json?"
                gmaps_api_key = ir_config_param.get_param('base_geolocalize.google_map_api_key') or ''
                params = "latlng={lat},{lon}&sensor={sen}&key={key}".format(
                    lat=record.vehicle_latitude,
                    lon=record.vehicle_longitude,
                    sen='false',
                    key=gmaps_api_key
                )
                url = "{base}{params}".format(base=base, params=params)
                try:
                    response = requests.get(url)
                    res_json = response.json() if response else False
                    if res_json.get('status') != 'OK':
                        continue
                    result = res_json and res_json.get('results', False) and res_json.get('results')[0][
                        'formatted_address'] or ''
                except Exception as e:
                    _logger.exception(_(
                        'Cannot contact geolocation servers. Please make sure that your Internet connection is up and running (%s).') % e)

                if result: record.current_address = result

    def change_color_on_kanban(self):
        """    this method is used to change color index :return: index of color for kanban view    """
        for record in self:
            active_time = None
            if record.date_localization:
                inactivity_period_duration = self.env['ir.config_parameter'].sudo().get_param(
                    'inactivity_period_duration', default='30')
                active_time = fields.Datetime.datetime.datetime.now() - datetime.timedelta(
                    minutes=int(inactivity_period_duration))
            if record.gps_tracking and record.vehicle_latitude and record.vehicle_longitude and record.date_localization >= active_time:
                color = 5
                state = 'Tracking'
            elif record.gps_tracking:
                color = 7
                state = 'Tracking, not active'
            elif not record.gps_tracking:
                color = 2
                state = 'Not tracking'
            else:
                color = 0
                state = 'Unknown'
            record.kanban_color = color
            record.kanban_state = state

    vehicle_latitude = fields.Float(string='Geo Latitude', digits=(16, 5))
    vehicle_longitude = fields.Float(string='Geo Longitude', digits=(16, 5))
    current_address = fields.Char(string='Current Address', compute='_reverse_geocode', store=False)
    date_localization = fields.Datetime(string='Last Time Geolocated')
    traccar_uniqueID = fields.Char(string='Traccar unique ID')
    traccar_device_id = fields.Integer(string='Traccar device ID')
    gps_tracking = fields.Boolean(string='Tracking')
    location_history_ids = fields.One2many('fleet.vehicle.location.history', 'vehicle_id', string='Location History',
                                           copy=False, readonly=True)

    working_hours_from = fields.Float(string='Shift Starting Hour')
    working_hours_to = fields.Float(string='Shift Ending Hour')
    date_inactive_filter = fields.Date(string='On Date', store=False)

    pre_tracking_odometer = fields.Float(string='Odometer Before Tracking Started',
                                         help='Odometer status when the vehicle was started to be tracked on (each location update then updates the odometer).')

    bokeh_last_location = fields.Text(
        string='Last Location',
        compute=_compute_bokeh_chart)
    kanban_color = fields.Integer('Color Index', compute="change_color_on_kanban")
    kanban_state = fields.Char('Tracking State', compute="change_color_on_kanban")

    def action_show_daytrip(self):
        self.ensure_one()
        context = self.env.context.copy()
        context['default_vehicle_id'] = self.id
        new_ids = []
        all_dates = []
        all_location_records = self.env['fleet.vehicle.location.history'].search(
            [('vehicle_id', '=', self.id), ('date_localization', '!=', False), ('vehicle_latitude', '!=', 0),
             ('vehicle_longitude', '!=', 0)], order='date_localization desc')
        if all_location_records:
            for day in all_location_records:
                last_date = day.date_localization.date()
                if last_date not in all_dates:
                    all_dates.append(last_date)
                    new_id = self.env['fleet.vehicle.day.trip'].create({'vehicle_id': self.id, 'on_date': last_date})
                    if new_id:
                        new_ids.append(new_id.id)
        view_id = self.env.ref('traccar_fleet_tracking.view_vehicle_day_trip_calendar')
        return {
            'name': _('Daily Trip Data'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.vehicle.day.trip',
            'view_mode': 'calendar',
            'view_type': 'calendar',
            'target': 'current',
            'views': [(view_id.id, 'calendar')],
            'context': context,
            'domain': [('id', 'in', new_ids)]
        }

    def action_show_last_map_location(self):
        self.ensure_one()
        context = self.env.context.copy()
        context['default_vehicle_id'] = self.id
        new_id = self.env['fleet.vehicle.last.location'].create({'vehicle_id': self.id})
        view_id = self.env.ref('traccar_fleet_tracking.view_vehicle_last_location')
        return {
            'name': _('Last Location on the Map'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.vehicle.last.location',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'view_id': view_id and view_id.id or False,
            'context': context,
            'domain': [('id', 'in', [new_id and new_id.id or False])]
        }

    def action_show_map(self):
        self.ensure_one()
        context = self.env.context.copy()
        vehicles = [self.id]
        view_map_id = self.env.ref('traccar_fleet_tracking.view_fleet_vehicle_map')
        return {
            'name': _('Map'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.vehicle',
            'view_mode': 'google_map',
            'view_type': 'google_map',
            'views': [(view_map_id.id, 'google_map')],
            'context': context,
            'domain': [('id', 'in', vehicles)]
        }

    def toggle_gps_tracking(self):
        """ Inverse the value of the field ``gps_tracking`` on the records in ``self``. """
        for record in self:
            if not record.traccar_uniqueID:
                raise exceptions.Warning(
                    _('You have not provided a Traccar device unique ID, please click Edit and enter it before adding/removing a device!'))
            record.gps_tracking = not record.gps_tracking

            try:
                cookie = record.login()
                uniqueID = record.traccar_uniqueID
                if record.gps_tracking:
                    record.add_device(cookie, uniqueID)
                else:
                    record.remove_device(cookie, uniqueID)
            except:
                raise exceptions.Warning(_("Could not connect to Traccar, please check your Traccar Settings!"))

    def login(self):
        ir_config_obj = self.env['ir.config_parameter'].sudo()
        url = ir_config_obj.get_param('traccar_server_url', default='http://127.0.0.1:8082')
        traccar_username = ir_config_obj.get_param('traccar_username', default='admin')
        traccar_password = ir_config_obj.get_param('traccar_password', default='admin')

        response = requests.post(url + '/api/session', data={'email': traccar_username, 'password': traccar_password})
        res = response.headers.get('Set-Cookie'), url

        # check if there's an Odoo group in Traccar, which we link all the devices from Odoo and all geofences to
        self.check_odoo_traccar_group(res)

        return res

    def check_odoo_traccar_group(self, cookie):
        ir_config_obj = self.env['ir.config_parameter'].sudo()
        headers = {'Cookie': cookie[0], 'Content-Type': 'application/json', 'Accept': 'application/json'}
        group_id = False
        OdooTraccarGroupId = ir_config_obj.get_param('odoo_traccar_groupId')
        try:
            if OdooTraccarGroupId:
                response = requests.get(cookie[1] + '/api/groups', headers=headers)
                data = response.json()
                group_id = False
                for group in data:
                    if str(OdooTraccarGroupId) == str(group['id']):
                        group_id = True
            if not group_id:
                group = {'name': 'Odoo Group'}
                response = requests.post(cookie[1] + '/api/groups', headers=headers, data=json.dumps(group))
                data = response.json()
                group_id = data and data['id'] or False
                if group_id:
                    ir_config_obj.set_param('odoo_traccar_groupId', (group_id))
        except:
            _logger.exception("Traccar - Odoo group retrieval failed.")

    def remove_device(self, cookie, uniqueID):
        headers = {'Cookie': cookie[0], 'Content-Type': 'application/json', 'Accept': 'application/json'}
        response = requests.get(cookie[1] + '/api/devices', headers=headers)
        data = response.json()
        for device in data:
            if uniqueID == device['uniqueId']:
                response = requests.delete(cookie[1] + '/api/devices/' + str(device['id']), headers=headers)

    def add_device(self, cookie, uniqueID):
        headers = {'Cookie': cookie[0], 'Content-Type': 'application/json', 'Accept': 'application/json'}
        response = requests.get(cookie[1] + '/api/devices', headers=headers)
        data = response.json()
        device_id = False
        for device in data:
            if uniqueID == device['uniqueId']:
                device_id = device['id']

        if not device_id:
            OdooTraccarGroupId = self.env['ir.config_parameter'].sudo().get_param('odoo_traccar_groupId')
            device = {'name': self.name, 'uniqueId': uniqueID}
            if OdooTraccarGroupId: device.update(groupId=OdooTraccarGroupId)
            response = requests.post(cookie[1] + '/api/devices', headers=headers, data=json.dumps(device))
            data = response.json()
            device_id = data and data['id'] or False
        self.write({'traccar_device_id': device_id})

    def geo_localize(self):
        add_to_odometer = True if self.env['ir.config_parameter'].sudo().get_param('add_to_odometer',
                                                                                   'False').lower() != 'false' else False
        # get superuser's timezone
        user = self.env['res.users'].sudo().browse(SUPERUSER_ID)
        if user.partner_id.tz:
            tz = timezone(user.partner_id.tz) or timezone('UTC')
        else:
            tz = timezone('UTC')

        cookie = self.login()
        for vehicle in self:
            traccar_device_id = vehicle.traccar_device_id
            if cookie and traccar_device_id:
                result = get_last_position(cookie, traccar_device_id)
                if result and result[0] != 0 and result[1] != 0 and result[2]:
                    res = {
                        'vehicle_latitude': result[0],
                        'vehicle_longitude': result[1],
                        'date_localization': result[2],
                    }

                    if not self.env['fleet.vehicle.location.history'].search(
                            [('vehicle_id', '=', vehicle.id), ('date_localization', '=', result[2])]):
                        res.update({
                            'location_history_ids': [(0, 0, {
                                'vehicle_latitude': result[0],
                                'vehicle_longitude': result[1],
                                'date_localization': result[2],
                                'name': vehicle.name,
                                'driver_name': vehicle.driver_id and vehicle.driver_id.name or '-'
                            })]
                        })
                        if result[3] and add_to_odometer: res.update(
                            odometer=vehicle.pre_tracking_odometer + (
                                (result[3] / 1000.00) if vehicle.odometer_unit == 'kilometers' else (result[
                                                                                                         3] / 1000.00) * 0.62137))
                    vehicle.write(res)
        return True

    @api.model
    def schedule_traccar(self):
        """Schedules fleet tracking using Traccar platform."""

        records_to_schedule = self.env['fleet.vehicle'].search(
            [('gps_tracking', '=', True), ('traccar_device_id', '!=', False)])
        if not records_to_schedule:
            return

        try:
            records_to_schedule.geo_localize()
            res = True
        except Exception:
            _logger.exception("Fleet Tracking Failed.")
            res = None
        return res

    def action_show_inactives(self):
        self.ensure_one()
        context = self.env.context.copy()
        context['default_vehicle_id'] = self.id
        new_ids = []
        condition = [('vehicle_id', '=', self.id),
                     ('vehicle_latitude', '!=', 0), ('vehicle_longitude', '!=', 0)]  # ('inactive_period','=', True)
        if self.date_inactive_filter:
            condition.extend([('date_localization', '>=', self.date_inactive_filter), (
                'date_localization', '<=',
                datetime.datetime.combine(self.date_inactive_filter.date(), datetime.time.max))])

        all_location_records = self.env['fleet.vehicle.location.history'].search(condition,
                                                                                 order='date_localization desc')
        if all_location_records:
            for day in all_location_records:
                if day.inactive_period: new_ids.append(day.id)
        view_id = self.env.ref('traccar_fleet_tracking.view_vehicle_location_history_tree')
        return {
            'name': _('Inactive Periods'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.vehicle.location.history',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'target': 'current',
            # 'views': [(view_id.id, 'tree')],
            'context': context,
            'domain': [('id', 'in', new_ids)]
        }


class FleetVehicleDayTrip(models.TransientModel):
    _name = "fleet.vehicle.day.trip"
    _description = 'Daily Vehicle Trip Data'
    _rec_name = 'on_date'

    @api.depends('on_date')
    def _compute_bokeh_chart(self):
        for rec in self:
            on_date = self.on_date
            day_after = on_date + datetime.timedelta(days=1)

            day_points = self.env['fleet.vehicle.location.history'].search([
                ('vehicle_id', '=', self.vehicle_id.id),
                ('date_localization', '<', day_after),
                ('date_localization', '>=', on_date),
            ])
            if not day_points:
                return

            data = {
                'lat': [],
                'lon': [],
                'info': []
            }
            for point in day_points:
                data['lat'].append(point.vehicle_latitude)
                data['lon'].append(point.vehicle_longitude)
                data['info'].append(point.driver_name + ' - ' + point.date_localization.strftime("%Y-%m-%d %H:%M:%S"))

            map_options = GMapOptions(lat=data['lat'] and data['lat'][0] or 0,
                                      lng=data['lon'] and data['lon'][0] or 0, map_type="roadmap", zoom=11)

            gmaps_api_key = self.env['ir.config_parameter'].sudo().get_param('base_geolocalize.google_map_api_key')
            if not gmaps_api_key:
                raise UserError(_("You have not entered a Google Maps API key (under Fleet - Traccar Settings), "
                                  "please do so to view map views."))

            p = GMapPlot(api_key=gmaps_api_key, x_range=Range1d(), y_range=Range1d(),
                         map_options=map_options)  # , title="My Drive")

            source = ColumnDataSource(data=dict(data))
            path = Line(x="lon", y="lat", line_width=2, line_color='blue')

            p.add_glyph(source, path)
            p.add_tools(PanTool(), WheelZoomTool(), SaveTool(), HoverTool(tooltips=[("Info", "@info")]))
            p.sizing_mode = 'scale_width'

            script, div = components(p)
            rec.trip = '%s%s' % (div, script)

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True)
    on_date = fields.Date(string='On Date', default=fields.Date.today(), required=True, track_visibility='always')
    trip = fields.Text(
        string='Trip',
        compute=_compute_bokeh_chart, track_visibility='always')
