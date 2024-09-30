# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


# -------------------------------------------------------------------------------------------------------->
# Example:
# Authenticate    : http://your_host:port/web/session/authenticate || Pass Data Into Body In Dictionary
# Read Data       : http://your_host:port/read_data/moduel_name
# Search By Id    : http://your_host:port/search_by_id/moduel_name/id
# Create Record   : http://your_host:port/create/moduel_name       || Pass Data Into Body In Dictionary
# Update Record   : http://your_host:port/update/module_name       || Pass Data Into Body In Dictionary
# Delete Record   : http://your_host:port/update/module_name       || Pass Data Into Body In Dictionary
# Destroy Session : http://your_host:port/web/session/destroy
# -------------------------------------------------------------------------------------------------------->

class OdooMobileApi(http.Controller):
    app_name = 'aklna-app'

    # Read Data
    @http.route('/{}/read_data/<string:model_name>'.format(app_name), type='json', auth='public', csrf=False)
    def read_data(self, model_name, **rec):
        records = request.env[model_name].search_read([])
        data = {'status': 200, 'response': records, 'message': 'Success'}
        return data

    # Search By ID
    @http.route('/{}/search_by_id/<string:model_name>/<int:search_id>'.format(app_name), type='json', auth='public',
                csrf=False)
    def search_by_id(self, model_name, search_id, **kw):
        records = request.env[model_name].search([('id', '=', search_id)]).read([])
        data = {'status': 200, 'response': records, 'message': 'Success'}
        return data

    # Create Record
    @http.route('/{}/create/<string:model_name>'.format(app_name), type='json', auth='public')
    def create(self, model_name, **rec):
        if request.jsonrequest:
            record_list = {}
            for key, value in rec.items():
                record_list[key] = value
            new_record = request.env[model_name].sudo().create(record_list)
            data = {'Success': True, 'message': 'Success', 'ID': new_record.id}
        return data

    # Update Record
    @http.route('/{}/update/<string:model_name>'.format(app_name), type='json')
    def update(self, model_name, **rec):
        if request.jsonrequest:
            if rec['id']:
                record = request.env[model_name].sudo().search([('id', '=', rec['id'])])
                if record:
                    record.sudo().write(rec)
                data = {'Success': True, 'message': 'Success'}
            return data

    # Delete Record
    @http.route('/{}/delete/<string:model_name>'.format(app_name), type='json')
    def delete(self, model_name, **rec):
        if request.jsonrequest:
            if rec['id']:
                user = request.env[model_name].sudo().search([('id', '=', rec['id'])])
                if user:
                    user.unlink()
                data = {'Success': True, 'message': 'Success'}
            return data
