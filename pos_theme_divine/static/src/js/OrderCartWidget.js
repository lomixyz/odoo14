odoo.define('point_of_sale.OrderCartWidget', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class OrderCartWidget extends PosComponent {
        constructor() {
            super(...arguments);
            var self = this;
            self.product_type_dict = {
                'consu' : 'Consumable',
                'service' : 'Service',
                'product' : 'Stockable Product'
            }
        }
        get imageUrl() {
            const product = this.props.product;
            return `/web/image?model=product.product&field=image_512&id=${product.id}&write_date=${product.write_date}&unique=1`;
        }
        get order() {
            return this.env.pos.get_order();
        }
        get orderlinesArray() {
            return this.order ? this.order.get_orderlines() : [];
        }
        back(event){
            this.showScreen('ProductListScreenWidget');
        }
    }
    OrderCartWidget.template = 'OrderCartWidget';

    Registries.Component.add(OrderCartWidget);

    return OrderCartWidget;
});
