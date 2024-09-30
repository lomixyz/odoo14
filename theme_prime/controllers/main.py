# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol. (<https://www.droggol.com/>)

import hashlib
import json

from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale_wishlist.controllers.main import WebsiteSaleWishlist
from odoo.osv import expression


class ThemePrimeWebsiteSale(WebsiteSale):

    def _check_float(self, val):
        try:
            return float(val)
        except ValueError:
            pass
        return False

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True, search_in_brand=True):
        domains = super(ThemePrimeWebsiteSale, self)._get_search_domain(search, category, attrib_values, search_in_description)

        # Price
        min_price = request.httprequest.args.get('min_price')
        max_price = request.httprequest.args.get('max_price')
        if min_price:
            min_price = self._check_float(min_price)
            if min_price:
                domains = expression.AND([domains, [('list_price', '>=', min_price)]])
        if max_price:
            max_price = self._check_float(max_price)
            if max_price:
                domains = expression.AND([domains, [('list_price', '<=', max_price)]])

        # Brand
        if search_in_brand:
            brand = request.httprequest.args.getlist('brand')
            if brand:
                domains = expression.AND([domains, [('dr_brand_id', 'in', [int(x) for x in brand])]])

        # Tag
        tag = request.httprequest.args.getlist('tag')
        if tag:
            domains = expression.AND([domains, [('dr_tag_ids', 'in', [int(x) for x in tag])]])

        # Rating
        ratings = request.httprequest.args.getlist('rating')
        if ratings:
            result = request.env['rating.rating'].sudo().read_group([('res_model', '=', 'product.template')], ['rating:avg'], groupby=['res_id'], lazy=False)
            rating_product_ids = []
            for rating in ratings:
                rating_product_ids.extend([item['res_id'] for item in result if item['rating'] >= int(rating)])
            if rating_product_ids:
                domains = expression.AND([domains, [('id', 'in', rating_product_ids)]])

        return domains

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        response = super(ThemePrimeWebsiteSale, self).shop(page, category, search, ppg, **post)
        theme_id = request.website.sudo().theme_id
        if theme_id and theme_id.name.startswith('theme_prime'):
            brands = request.env['dr.product.brand'].search(request.website.website_domain())
            tags = request.env['dr.product.tags'].search(request.website.website_domain())

            prices = request.env['product.template'].read_group(request.website.website_domain(), ['max_price:max(list_price)', 'min_price:min(list_price)'], [])[0]
            min_price = float(prices['min_price'] or 0)
            max_price = float(prices['max_price'] or 0)
            keep = QueryURL(
                '/shop',
                category=category and int(category),
                search=search,
                attrib=request.httprequest.args.getlist('attrib'),
                ppg=ppg,
                order=post.get('order'),
                min_price=request.httprequest.args.get('min_price'),
                max_price=request.httprequest.args.get('max_price'),
                brand=request.httprequest.args.getlist('brand'),
                tag=request.httprequest.args.getlist('tag'),
            )

            # Grid Sizing
            bins = []
            for product in response.qcontext.get('products'):
                bins.append([{
                    'ribbon': product.website_ribbon_id,
                    'product': product,
                    'x': 1,
                    'y': 1
                }])

            attrib_list = request.httprequest.args.getlist('attrib')
            attrib_values = [[int(x) for x in v.split('-')] for v in attrib_list if v]
            attributes_ids = [v[0] for v in attrib_values]  # Custom created

            if request.website._get_dr_theme_config('json_shop_filters')['show_category_count']:
                Product = request.env['product.template'].with_context(bin_size=True)
                domain = self._get_search_domain(search, None, attrib_values)
                search_product = Product.search(domain)
                get_category_count = request.env['product.template']._get_product_category_count(website_ids=request.website.ids, product_ids=search_product.ids)
                response.qcontext.update(
                    get_category_count=get_category_count,
                )
            if request.website._get_dr_theme_config('json_shop_filters')['show_attrib_count']:
                # Attributes
                Product = request.env['product.template'].with_context(bin_size=True)
                domain = self._get_search_domain(search, category, [])
                search_product = Product.search(domain)
                get_attrib_count = request.env['product.template']._get_product_attrib_count(website_ids=request.website.ids, product_ids=search_product.ids, attrib_values=attrib_values)
                response.qcontext.update(
                    get_attrib_count=get_attrib_count,
                )
                # Brand
                domain = self._get_search_domain(search, category, attrib_values, True, False)
                brand_counts = request.env['product.template'].read_group(domain, ['dr_brand_id'], 'dr_brand_id')
                response.qcontext.update(
                    get_brands_count=dict([(x['dr_brand_id'][0], x['dr_brand_id_count']) for x in brand_counts if x['dr_brand_id']]),
                )

            response.qcontext.update(
                brands=brands,
                tags=tags,
                keep=keep,
                min_price=min_price,
                max_price=max_price,
                bins=bins,
                attributes_ids=attributes_ids,
                selected_brands=[int(x) for x in request.httprequest.args.getlist('brand')],
                selected_tags=[int(x) for x in request.httprequest.args.getlist('tag')],
                selected_ratings=[int(x) for x in request.httprequest.args.getlist('rating')],
            )
        return response

    @http.route(['/shop/cart'], type='http', auth='public', website=True, sitemap=False)
    def cart(self, access_token=None, revive='', **post):
        res = super(ThemePrimeWebsiteSale, self).cart(access_token=access_token, revive=revive, **post)
        if post.get('type') == 'tp_cart_sidebar_request':
            order = request.website.sale_get_order()
            if order and order.state != 'draft':
                request.session['sale_order_id'] = None
            return request.render('theme_prime.cart_sidebar', {'order': order}, headers={'Cache-Control': 'no-cache'})
        return res

    @http.route('/theme_prime/search_sidebar', type='http', auth='public', website=True, sitemap=False)
    def search_sidebar(self, access_token=None, revive='', **post):
        return request.render('theme_prime.search_sidebar', headers={'Cache-Control': 'no-cache'})

    @http.route('/theme_prime/get_category_sidebar', type='http', auth='public', website=True, sitemap=False)
    def _get_category_sidebar(self, access_token=None, revive='', **post):
        return request.render('theme_prime.category_sidebar', headers={'Cache-Control': 'no-cache'})

    @http.route('/theme_prime/get_quick_view_html', type='json', auth='public', website=True)
    def get_quick_view_html(self, options, **kwargs):
        productID = options.get('productID')
        variantID = options.get('variantID')
        product = False
        if variantID:
            productID = request.env['product.product'].browse(variantID).product_tmpl_id.id

        domain = expression.AND([request.website.sale_product_domain(), [('id', '=', productID)]])
        product = request.env['product.template'].search(domain, limit=1)
        # If moved to another website or delete
        if not product:
            return []

        # If request ask `add_if_single_variant` param
        # Do not return if there is only one varient
        is_single_product = options.get('add_if_single_variant') and product.product_variant_count == 1

        values = self._prepare_product_values(product, category='', search='', **kwargs)
        Website = request.website
        result = Website._get_theme_prime_shop_config()
        values.update(result)
        if result.get('is_rating_active'):
            values['rating'] = Website._get_theme_prime_rating_template(product.rating_avg, product.rating_count)
        values['d_url_root'] = request.httprequest.url_root[:-1]

        if options.get('mini'):
            values['auto_add_product'] = is_single_product
            return request.env["ir.ui.view"]._render_template('theme_prime.product_mini', values=values)

        if options.get('right_panel'):
            values['auto_add_product'] = is_single_product
            return request.env["ir.ui.view"]._render_template('theme_prime.tp_product_right_panel', values=values)
        return request.env["ir.ui.view"]._render_template('theme_prime.tp_product_quick_view', values=values)

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['GET', 'POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        response = super(ThemePrimeWebsiteSale, self).cart_update(product_id, add_qty, set_qty, **kw)
        sale_order = request.website.sale_get_order(force_create=True)

        if kw.get('express'):
            return response

        monetary_options = {
            'display_currency': sale_order.pricelist_id.currency_id,
        }

        FieldMonetary = request.env['ir.qweb.field.monetary']
        cart_amount_html = FieldMonetary.value_to_html(sale_order.amount_total, monetary_options)

        if kw.get('dr_cart_flow'):
            product = request.env['product.product'].browse(int(product_id))
            return json.dumps({
                'cart_quantity': sale_order.cart_quantity,
                'product_name': product.name,
                'product_id': int(product_id),
                'cart_amount_html': cart_amount_html,
                'accessory_product_ids': product.accessory_product_ids and product.accessory_product_ids.mapped('product_tmpl_id').ids or []
            })

        return response

class DroggolWishlist(WebsiteSaleWishlist):
    @http.route('/theme_prime/wishlist_general', auth="public", type='json', website=True)
    def wishlist_general(self, product_id=False, **post):
        res = {}
        if product_id:
            res['wishlist_id'] = self.add_to_wishlist(product_id).id
        res.update({
            'products': request.env['product.wishlist'].with_context(display_default_code=False).current().mapped('product_id').ids,
            'name': request.env['product.product'].browse(product_id).name
        })
        return res

class ThemePrimeMainClass(http.Controller):

    # ----------------------------------------------------------
    # Helper methods
    # ----------------------------------------------------------

    def _get_products(self, domain=None, fields=[], limit=25, order=None):
        pricelist = request.website.get_current_pricelist()
        rating_in_fields = False
        offer_in_fields = False
        website_sale_domain = request.website.sale_product_domain()
        final_domain = expression.AND([website_sale_domain, domain])
        products = request.env['product.template'].with_context(pricelist=pricelist.id).search(final_domain, limit=limit, order=order)
        default_fields = ['id', 'name', 'website_url']
        fields = set(default_fields + fields)

        # rating is not a real field
        if 'rating' in fields:
            rating_in_fields = True
            fields.remove('rating')
        # rating is not a real field
        if 'offer_data' in fields:
            offer_in_fields = True
            fields.remove('offer_data')

        result = products.read(fields)
        FieldMonetary = request.env['ir.qweb.field.monetary']
        monetary_options = {
            'display_currency': pricelist.currency_id,
        }

        for res_product, product in zip(result, products):
            combination_info = product._get_combination_info(only_template=True)
            res_product.update(combination_info)
            res_product['price_raw'] = res_product['price']
            res_product['list_price_raw'] = res_product['list_price']
            res_product['price'] = FieldMonetary.value_to_html(res_product['price'], monetary_options)
            res_product['list_price'] = FieldMonetary.value_to_html(res_product['list_price'], monetary_options)
            res_product['product_variant_id'] = product._get_first_possible_variant_id()

            sha = hashlib.sha1(str(getattr(product, '__last_update')).encode('utf-8')).hexdigest()[0:7]
            # Images
            res_product['img_small'] = '/web/image/product.template/' + str(product.id) + '/image_256?unique=' + sha
            res_product['img_medium'] = '/web/image/product.template/' + str(product.id) + '/image_512?unique=' + sha
            res_product['img_large'] = '/web/image/product.template/' + str(product.id) + '/image_1024?unique=' + sha

            # short Description
            if 'description_sale' in fields:
                description = res_product.get('description_sale')
                res_product['short_description'] = description[:200] + '...' if description and len(description) > 200 else description or False
            # label and color
            if 'dr_label_id' in fields and product.dr_label_id:
                res_product['label'] = product.dr_label_id.name
                res_product['lable_color'] = product.dr_label_id.color
                res_product['label_style'] = product.dr_label_id.style
            # rating
            if offer_in_fields:
                offer = product._get_product_pricelist_offer()
                if offer:
                    rule = offer.get('rule')
                    res_product['offer_data'] = {
                        'date_end': offer.get('date_end'),
                        'offer_msg': rule.dr_offer_msg,
                        'offer_finish_msg': rule.dr_offer_finish_msg
                    }

            if rating_in_fields:
                res_product['rating'] = self._get_rating_template(product.rating_avg)
                res_product['rating_avg'] = product.rating_avg
            # images
            if 'product_variant_ids' in fields:
                res_product['images'] = product.product_variant_ids.ids
            # website_category
            if 'public_categ_ids' in fields and product.public_categ_ids:
                first_category = product.public_categ_ids[0]
                res_product['category_info'] = {
                    'name': first_category.name,
                    'id': first_category.id,
                    'website_url': '/shop/category/' + str(first_category.id),
                }

        return result

    def _get_shop_related_data(self, options):
        shop_data = {}
        if (options.get('shop_config_params')):
            shop_data['shop_config_params'] = self.get_shop_config()
        if (options.get('wishlist_enabled')) and shop_data.get('shop_config_params', {}).get('is_wishlist_active'):
            shop_data['wishlist_products'] = request.env['product.wishlist'].with_context(display_default_code=False).current().mapped('product_id').ids
        return shop_data

    def _get_rating_template(self, rating_avg, rating_count=False):
        return request.website._get_theme_prime_rating_template(rating_avg, rating_count)

    def _get_category_names(self, categoryIDs):
        domain = expression.AND([request.website.website_domain(), [('id', 'in', categoryIDs)]])
        return request.env['product.public.category'].search_read(domain, fields=['name', 'display_name', 'id'])

    def _get_products_for_top_categories(self, params):
        result = {}
        categoryIDs = params.get('categoryIDs')
        order = params.get('sortBy')
        operator = '='
        if params.get('includesChild'):
            operator = 'child_of'
        initial_domain = expression.AND([request.website.website_domain(), [('website_published', '=', True)]])
        pricelist = request.website.get_current_pricelist()
        for id in categoryIDs:
            domain = expression.AND([initial_domain, [['public_categ_ids', operator, id]]])
            products = request.env['product.template'].with_context(pricelist=pricelist.id).search_read(domain=domain, fields=['id'], limit=3, order=order)
            result[id] = [product['id'] for product in products]
        return result

    def _get_d_products_manually(self, collection, fields, limit, order, **kwargs):
        domain = [['id', 'in', collection.get('productIDs', [])]]
        return self._get_products(domain, fields, limit, order)

    def _get_d_products_advance(self, collection, fields, **kwargs):
        domain_params = collection.get('domain_params')
        domain = domain_params.get('domain')
        limit = domain_params.get('limit', 25)
        order = domain_params.get('sortBy', None)
        return self._get_products(domain, fields, limit, order)

    @http.route('/theme_prime/get_product_by_name', type='http', website=True)
    def get_product_by_name(self, term='', **post):
        domains = [request.website.sale_product_domain(), [('website_published', '=', True)]]
        subdomains = [
            [('name', 'ilike', (term or ''))],
            [('product_variant_ids.default_code', 'ilike', (term or ''))]
        ]
        domains.append(expression.OR(subdomains))
        fields = ['description_sale']
        result = self._get_products(expression.AND(domains), fields, 25, 'is_published desc, website_sequence ASC, id desc')
        return json.dumps(result)

    # TO-DO remove viewref logic someday and adapt everything new ways
    @http.route('/theme_prime/get_shop_config', type='json', auth='public', website=True)
    def get_shop_config(self):
        return request.website._get_theme_prime_shop_config()

    @http.route('/theme_prime/get_products_data', type='json', auth='public', website=True)
    def get_products_data(self, domain, fields=[], options={},  limit=25, order=None, **kwargs):
        result = {
            'products': self._get_products(domain, fields, limit, order),
        }
        result.update(self._get_shop_related_data(options))
        return result

    @http.route('/theme_prime/get_category_by_name', type='http', website=True)
    def get_category_by_name(self, term='', category_id=False, **post):
        domain = expression.AND([request.website.website_domain(), [('name', 'ilike', (term or ''))]])
        if category_id:
            domain = expression.AND([domain, [('id', 'child_of', int(category_id))]])
        result = request.env['product.public.category'].search_read(domain, fields=['name', 'display_name', 'id'], limit=10)
        return json.dumps(result)

    @http.route('/theme_prime/get_products_by_category', type='json', auth='public', website=True)
    def get_products_by_category(self, domain, fields=[], options={}, **kwargs):
        final_domain = expression.AND([[('website_published', '=', True)], domain])
        result = {
            'products': self._get_products(domain=final_domain, fields=fields, order=options.get('order', False), limit=options.get('limit', False)),
        }
        result.update(self._get_shop_related_data(options))
        if (options.get('get_categories')):
            # get category names for snippet
            result['categories'] = self._get_category_names(options.get('categoryIDs'))
        return result

    @http.route('/theme_prime/get_top_categories', type='json', auth='public', website=True)
    def get_top_categories(self, options={}):
        params = options.get('params')
        result = []
        pricelist = request.website.get_current_pricelist()
        website_sale_domain = request.website.sale_product_domain()
        FieldMonetary = request.env['ir.qweb.field.monetary']
        monetary_options = {
            'display_currency': pricelist.currency_id,
        }
        if params:
            categoryIDs = params.get('categoryIDs')
            if categoryIDs:
                category_names = {i['id']: i['name'] for i in self._get_category_names(categoryIDs)}
                # Update categoryIDs if already set category moved to other website
                categoryIDs = category_names.keys()
                params['categoryIDs'] = categoryIDs
                categories = self._get_products_for_top_categories(params)
                for category_id in categoryIDs:
                    category_data = {}
                    product_ids = categories.get(category_id)
                    category_data['name'] = category_names.get(category_id)
                    category_data['id'] = category_id
                    category_data['website_url'] = '/shop/category/' + str(category_id)
                    category_data['productIDs'] = product_ids
                    final_domain = expression.AND([website_sale_domain, [('public_categ_ids', 'child_of', category_id)]])
                    product_price = request.env['product.template'].with_context(pricelist=pricelist.id).read_group(final_domain, fields=['min_price:min(list_price)'], groupby=['active'])
                    if len(product_price):
                        product_price[0].get('price')
                        category_data['min_price'] = FieldMonetary.value_to_html(product_price[0].get('min_price'), monetary_options)
                    result.append(category_data)
        return result

    @http.route('/theme_prime/get_products_by_collection', type='json', auth='public', website=True)
    def get_products_by_collection(self, fields=[], limit=25, order=None, options={}, **kwargs):
        collections = options.get('collections')
        result = []
        shop_config_params = self.get_shop_config()
        for collection in collections:
            res = {}
            res['title'] = collection.get('title', '')
            res['is_rating_active'] = shop_config_params.get('is_rating_active', False)
            res['products'] = self._get_products_from_collection(collection.get('data'), fields, limit, order)
            result.append(res)
        return result

    @http.route('/theme_prime/_get_products_from_collection', type='json', auth='public', website=True)
    def _get_products_from_collection(self, collection, fields=[], limit=25, order=None, **kwargs):
        selection_type = collection.get('selectionType')
        if selection_type == 'manual':
            return self._get_d_products_manually(collection, fields, limit, order)
        elif selection_type == 'advance':
            return self._get_d_products_advance(collection, fields)

    @http.route('/theme_prime/save_website_config', type='json', auth='user', website=True)
    def save_website_config(self, configs, **post):
        request.env['dr.theme.config']._save_config(request.website.id, configs)
        return {'result': True}

    @http.route('/theme_prime/get_categories_info', type='json', auth='public', website=True)
    def get_categories_info(self,  fields=[], options={}, **kwargs):
        categoryIDs = options.get('categoryIDs', [])
        fields = ['name', 'display_name', 'id'] + fields
        domain = expression.AND([request.website.website_domain(), [('id', 'in', categoryIDs)]])
        categories = request.env['product.public.category'].search(domain)
        result = categories.read(fields)
        if options.get('getCount', False):
            get_category_count = request.env['product.template']._get_product_category_count(website_ids=request.website.ids)
        for res_category, category in zip(result, categories):
            if 'dr_category_label_id' in fields and category.dr_category_label_id:
                category_label = category.dr_category_label_id
                res_category['category_lable_info'] = {
                        'name': category_label.name,
                        'color': category_label.color,
                        'id': category_label.id,
                    }
            if options.get('getCount', False):
                res_category['count'] = get_category_count.get(category.id)
            res_category['website_url'] = '/shop/category/' + str(category.id)
            res_category['image_url'] = '/web/image?model=product.public.category&id=%d&field=image_128' % (category.id)
            res_category['cover_image'] = '/web/image?model=product.public.category&id=%d&field=dr_category_cover_image' % (category.id)
        return result

    @http.route('/theme_prime/get_brands', type='json', auth='public', website=True)
    def get_brands(self, fields=['id'], options={}):
        return request.env['dr.product.brand'].search_read(request.website.website_domain(), limit=options.get('limit', 12), fields=fields)
