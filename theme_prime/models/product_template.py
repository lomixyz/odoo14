# -*- coding: utf-8 -*-

from odoo import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_product_category_count(self, website_ids, product_ids=[]):
        product_str = ' '
        if product_ids:
            product_str = ' FILTER (WHERE product_template.id in %(product_ids)s ) '
        else:
            product_str = ' FILTER (WHERE product_template.active = true AND (product_template.website_id in %(website_ids)s OR product_template.website_id is NULL))'

        query = """
            SELECT
                count(product_template.id) """ + product_str + """,
                min(product_public_category.parent_path) as path,
                min(product_public_category.parent_id) as parent_id,
                product_public_category.id as product_public_category_id
            FROM product_public_category_product_template_rel
                JOIN product_template ON product_template.id = product_public_category_product_template_rel.product_template_id
                RIGHT JOIN product_public_category ON product_public_category.id = product_public_category_product_template_rel.product_public_category_id
            GROUP BY product_public_category.id;
        """

        self.env.cr.execute(query, {'website_ids': tuple(website_ids), 'product_ids': tuple(product_ids)})
        query_res = self.env.cr.dictfetchall()

        result_count = dict([(line.get('product_public_category_id'), 0) for line in query_res])

        for line in query_res:
            for line2 in query_res:
                if line.get('parent_id'):
                    path_pattern = '/%s/' % line.get('product_public_category_id')
                    if path_pattern in line2.get('path'):
                        result_count[line.get('product_public_category_id')] += line2.get('count')
                else:
                    path_pattern = '%s/' % line.get('product_public_category_id')
                    if line2.get('path').startswith(path_pattern):
                        result_count[line.get('product_public_category_id')] += line2.get('count')

        return result_count

    def _get_product_attrib_count(self, website_ids, product_ids=[], attrib_values=[]):

        product_str = ' '
        if product_ids:
            product_str = ' product_template_attribute_line.product_tmpl_id in %(product_ids)s '

        if not product_ids:
            return {}

        query = """
            SELECT
                array_agg(product_template_attribute_line.product_tmpl_id)
                    FILTER (WHERE """ + product_str + """ ) as product_tmpl_ids,
                min(product_template_attribute_line.attribute_id) as product_attrib_id,
                product_attribute_value.id
            FROM product_template_attribute_line
            JOIN product_attribute_value_product_template_attribute_line_rel
                ON product_attribute_value_product_template_attribute_line_rel.product_template_attribute_line_id = product_template_attribute_line.id
            JOIN product_attribute_value
                ON product_attribute_value.id = product_attribute_value_product_template_attribute_line_rel.product_attribute_value_id
            GROUP BY product_attribute_value.id
            ORDER BY product_attrib_id;
        """

        self.env.cr.execute(query, {'website_ids': tuple(website_ids), 'product_ids': tuple(product_ids)})
        query_res = self.env.cr.dictfetchall()

        result_count = {}

        if attrib_values:

            attrib_values_ids = [v[1] for v in attrib_values]
            attrib_ids = [v[0] for v in attrib_values]
            attrib_value_list = dict([(line.get('id'), line.get('product_tmpl_ids') or []) for line in query_res])

            # Attribute -> Attribute Vals map
            attrib_vals_map = {}
            for line in query_res:
                if not attrib_vals_map.get(line['product_attrib_id']):
                    attrib_vals_map[line['product_attrib_id']] = []
                attrib_vals_map[line['product_attrib_id']].append(line['id'])


            # Attribute -> active product list
            attrib_p_list = {}
            for line in query_res:

                value_id_1 = line.get('id')
                product_ids_1 = line.get('product_tmpl_ids') or []
                attrib_id_1 = line.get('product_attrib_id')

                if not attrib_p_list.get(attrib_id_1):
                    attrib_p_list[attrib_id_1] = set()

                if value_id_1 in attrib_values_ids:
                    attrib_p_list[attrib_id_1] = attrib_p_list[attrib_id_1] | set(product_ids_1)


            # Attribute -> final list
            attrib_product_list = {}
            for line in query_res:
                value_id_1 = line.get('id')
                product_ids_1 = line.get('product_tmpl_ids') or []
                attrib_id_1 = line.get('product_attrib_id')

                if not attrib_product_list.get(value_id_1):
                    attrib_product_list[value_id_1] = set(product_ids_1)

                for line_2 in query_res:
                    value_id_2 = line_2.get('id')
                    product_ids_2 = line_2.get('product_tmpl_ids') or []
                    attrib_id_2 = line_2.get('product_attrib_id')

                    if value_id_2 not in attrib_vals_map.get(attrib_id_1, []) and value_id_2 in attrib_values_ids:
                        attrib_product_list[value_id_1] = attrib_product_list[value_id_1] & attrib_p_list.get(attrib_id_2, set())

            result_count = dict([(val_id, len(product_ids)) for val_id, product_ids in attrib_product_list.items()])
        else:
            result_count = dict([(line.get('id'), len(line.get('product_tmpl_ids') or [])) for line in query_res])
        return result_count
