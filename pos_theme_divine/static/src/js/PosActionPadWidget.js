odoo.define('point_of_sale.PosActionPadWidget', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class PosActionPadWidget extends PosComponent {
        constructor() {
            super(...arguments);
            var self = this;
            this.config = null
            setTimeout(function(){
                if(self.env.pos){
                    self.config = self.env.pos.config
                }
            },100);
        }
        get get_grand_total(){
            var order = this.env.pos.get_order();
            var total = 0;
            if (order.get_orderlines().length) {
                total = order ? order.get_total_with_tax() : 0;
            }
            return this.env.pos.format_currency(total)
        }
        get get_subtotal(){
            var order = this.env.pos.get_order();
            var subtotal = 0;
            if (order.get_orderlines().length) {
                subtotal = order ? order.get_total_without_tax() : 0;
            }
            return this.env.pos.format_currency(subtotal)
        }
        get get_tax(){
            var order = this.env.pos.get_order();
            var total = 0;
            if (order.get_orderlines().length) {
                total = order ? order.get_total_with_tax() : 0;
            }
            var tax = order ? total - order.get_total_without_tax() : 0;
            return this.env.pos.format_currency(tax)
        }
        onClickPayment(event){
            this.showScreen('PaymentScreen');
        }
        onClickDiscount(event){
            if(this.env.pos.get_order().get_orderlines().length){
                this.showPopup('OrderlineDiscountPopup')
            }
        }
    }
    PosActionPadWidget.template = 'PosActionPadWidget';

    Registries.Component.add(PosActionPadWidget);

    return PosActionPadWidget;
});
