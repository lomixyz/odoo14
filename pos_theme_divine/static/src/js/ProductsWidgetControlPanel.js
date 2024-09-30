/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_redesign.ProductsWidgetControlPanel', function (require) {
    "use strict";    
    const ProductsWidgetControlPanel = require('point_of_sale.ProductsWidgetControlPanel');
    const Registries = require('point_of_sale.Registries');

    const PosResProductsWidgetControlPanel = (ProductsWidgetControlPanel) =>
        class extends ProductsWidgetControlPanel {
            clickCart(event) {
                var self = this;
                $('.rightpane-theme').show();
            }
            get get_items_count(){
                var order = this.env.pos.get_order();
                var lines = order.get_orderlines();
                var count=0;
                lines.forEach(function(orderline){
                    count+=orderline.quantity;
                });
                order.items_count = count;
                return count;
            }
        };

    Registries.Component.extend(ProductsWidgetControlPanel, PosResProductsWidgetControlPanel);

    return ProductsWidgetControlPanel;
});
