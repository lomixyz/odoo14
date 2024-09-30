# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Pos Divine Theme",
  "summary"              :  """Odoo POS Divine Theme makes your POS look attractive and pleasing to the user's eyes. The theme serves you all purpose from its creative outlook to the easy navigation for the best user experience.""",
  "category"             :  "Point of Sale",
  "version"              :  "1.0.0",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com",
  "description"          :  """Modern POS Theme Design
  Pos Redesign
  POS Brand New User Interface
  New POS Design
  POS New Theme
  Redesign POS Interface
  Design POS Modern Theme
  POS New Look
  Pos Divine Theme
  """,
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=pos_theme_divine&custom_url=/pos/web",
  "depends"              :  ['point_of_sale', 'pos_restaurant'],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/pos_config_view.xml',
                             'views/template.xml',
                            ],
  "qweb"                 :  ['static/src/xml/pos.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  199,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
