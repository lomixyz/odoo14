odoo.define('point_of_sale.OrderSelectorButtons', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { posbus } = require('point_of_sale.utils');

    class OrderSelectorButtons extends PosComponent {
        constructor() {
            super(...arguments);
        }
        get get_order_list() {
            if(this.env.pos)
                return this.env.pos.get_order_list()
            else
                return []
        }
        clickOrder(order){
            var self = this;
            this._setOrder(order);
            if (order === this.env.pos.get_order()) {
                this.env.pos.trigger('change:selectedOrder', this.env.pos, order);
            }
            setTimeout(function(){
                self.showScreen('ClientListScreen');
                self.showScreen('ProductScreen')
            })
        }
        _setOrder(order) {
            this.env.pos.set_order(order);
        }
        getDate(order) {
            return moment(order.creation_date).format('hh:mm');
        }
        clickAddNewOrder(event){
            var self = this;
            this.env.pos.add_new_order();
            setTimeout(function(){
                self.showScreen('ClientListScreen')
                self.showScreen('ProductScreen')
            },100)
        }
        async clickDeleteOrder(event){
            var self = this;
            var table = self.env.pos.table
            if (table){
                var order_counts = 0
                _.each(self.env.pos.get('orders').models, function(order){
                    if(order.table.id == table.id){
                        order_counts = order_counts + 1
                    }
                })

                if (order_counts == 1){
                    var order = this.env.pos.get_order()
                    if (order){
                        const screen = order.get_screen_data();
                        if (['ProductScreen', 'PaymentScreen'].includes(screen.name) && order.get_orderlines().length > 0) {
                            const { confirmed } = await this.showPopup('ConfirmPopup', {
                                    title: 'Existing orderlines',
                                    body: `${order.name} has total amount of ${this.getTotal(
                                        order
                                    )}, are you sure you want delete this order?`,
                                });
                                if (!confirmed) return;
                        }
                        if (order) {
                            order.destroy({ reason: 'abandon' });
                        }
                        posbus.trigger('order-deleted');
                    }
                    setTimeout(function(){
                        self.showScreen('FloorScreen')
                    },100)
                }
                else{
                    var order = this.env.pos.get_order()
                    if (order){
                        const screen = order.get_screen_data();
                        if (['ProductScreen', 'PaymentScreen'].includes(screen.name) && order.get_orderlines().length > 0) {
                            const { confirmed } = await this.showPopup('ConfirmPopup', {
                                    title: 'Existing orderlines',
                                    body: `${order.name} has total amount of ${this.getTotal(
                                        order
                                    )}, are you sure you want delete this order?`,
                                });
                                if (!confirmed) return;
                        }
                        if (order) {
                            order.destroy({ reason: 'abandon' });
                        }
                        posbus.trigger('order-deleted');
                    }
                    setTimeout(function(){
                        self.showScreen('ClientListScreen')
                        self.showScreen('ProductScreen')
                    },100)
                }
            }
            else{
                var order = this.env.pos.get_order()
                if (order){
                    const screen = order.get_screen_data();
                    if (['ProductScreen', 'PaymentScreen'].includes(screen.name) && order.get_orderlines().length > 0) {
                        const { confirmed } = await this.showPopup('ConfirmPopup', {
                                title: 'Existing orderlines',
                                body: `${order.name} has total amount of ${this.getTotal(
                                    order
                                )}, are you sure you want delete this order?`,
                            });
                            if (!confirmed) return;
                    }
                    if (order) {
                        order.destroy({ reason: 'abandon' });
                    }
                    posbus.trigger('order-deleted');
                }
                setTimeout(function(){
                    self.showScreen('ClientListScreen')
                    self.showScreen('ProductScreen')
                },100)
            }
        }
        getTotal(order) {
            return this.env.pos.format_currency(order.get_total_with_tax());
        }
    }
    OrderSelectorButtons.template = 'OrderSelectorButtons';

    Registries.Component.add(OrderSelectorButtons);

    return OrderSelectorButtons;
});