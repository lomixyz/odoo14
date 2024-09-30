odoo.define('point_of_sale.CartSummaryWidget', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class CartSummaryWidget extends PosComponent {
        constructor() {
            super(...arguments);
            var self = this;
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
        get get_line_count(){
            return this.env.pos.get_order().get_orderlines().length;
        }
        onClickClearCart(event){
            var self = this;
            // var current_order = this.env.pos.get_order();
            // while(current_order.get_orderlines().length != 0){
            //     current_order.remove_orderline(current_order.get_orderlines()[0]);
            // }
            // current_order.trigger("change");
            this.render();
            setTimeout(function(){
                self.showScreen('ClientListScreen')
                self.showScreen('ProductScreen')
                $('.rightpane-theme').hide();
            },100)
        }
        back(event){
            this.showScreen('ProductListScreenWidget');
        }
    }
    CartSummaryWidget.template = 'CartSummaryWidget';

    Registries.Component.add(CartSummaryWidget);

    return CartSummaryWidget;
});
