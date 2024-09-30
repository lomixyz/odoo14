# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict
from odoo.http import request

class ScsFreightPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'freight_operation_count' in counters:
            freight_operation_count = request.env['freight.operation'].search_count([]) \
                if request.env['freight.operation'].check_access_rights('read', raise_exception=False) else 0
            values['freight_operation_count'] = freight_operation_count
        return values

        
    @http.route(['/my/freight_operations', '/my/freight_operations/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_freight_operations(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        FreightOperation = request.env['freight.operation']

        domain = [
            ('customer_id', '=',request.env.user.partner_id.id)
            # ('state', 'in', ['sent', 'cancel'])
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'order_date desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        freight_operation_count = FreightOperation.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/freight_operations",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=freight_operation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        freight_operation = FreightOperation.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_freight_operation_history'] = freight_operation.ids[:100]

        values.update({
            'date': date_begin,
            'freight_operations': freight_operation.sudo(),
            'page_name': 'freight_operation',
            'pager': pager,
            'default_url': '/my/freight_operations',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("scs_freight_portal.portal_my_freight_operation", values)