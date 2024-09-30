odoo.define('point_of_sale.CartOrderline', function(require) {
    'use strict';
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class CartOrderline extends PosComponent {
        onClickUpdateOrderline(event){
            var self = this;
            var line = this.props.line 
            var cashier = self.env.pos.get('cashier') || self.env.pos.get_cashier();
            var has_price_control_rights = !self.env.pos.config.restrict_price_control || cashier.role == 'manager';
            if(!has_price_control_rights){
                this.showPopup("OrderlinePriceUpdatePopup",{
                    orderline: line,
                    has_price_control_rights: has_price_control_rights,
                });
            }
        }
        clickIncreaseQty(event){
            var self = this;
            var order = self.env.pos.get_order();
            var product = this.props.line.product 
            order.add_product(product)
        }
        clickDecreaseQty(event){
            var orderline = this.props.line
            if(orderline){
                let quantity = orderline.quantity-1
                orderline.set_quantity(orderline.quantity-1, true);
            }
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
        get_product_image_url(product){
            return '/web/image?model=product.product&field=image_256&id='+product.id;
        }
        onClickClearCart(event){
            var self = this;
            var current_order = this.env.pos.get_order();
            while(current_order.get_orderlines().length != 0){
                current_order.remove_orderline(current_order.get_orderlines()[0]);
            }
            current_order.trigger("change");
            this.render();
            setTimeout(function(){
                self.showScreen('ClientListScreen')
                self.showScreen('ProductScreen')
            },100)
        }
        remove_orderline(event){
            var self = this;
            this.env.pos.get_order().remove_orderline(this.props.line)
            this.render();
            setTimeout(function(){
                self.showScreen('ClientListScreen')
                self.showScreen('ProductScreen')
            },100)
        }
        wk_click_line(event){
            var self = this;
            var orderline = this.props.line;
            var order = self.env.pos.get_order();
            var cashier = self.env.pos.get('cashier') || self.env.pos.get_cashier();
            var has_price_control_rights = !self.env.pos.config.restrict_price_control || cashier.role == 'manager';
            if(order && !order.is_return_order){
                if(orderline.selected){
                    this.env.pos.get_order().select_order_line(orderline);
                } else {
                    // Update Price upto 2 decimal places
                    if(orderline && orderline.price){
                        orderline.price = parseFloat(orderline.price).toFixed(2)
                    }
                    this.env.pos.get_order().select_order_line(orderline);
                }
                this.render();
            }
            setTimeout(function(){
                self.showScreen('ClientListScreen')
                self.showScreen('ProductScreen')
            },100)
            // Hide Category List options
            this.product_category_list = $(".wk-category-list");
            if (!this.product_category_list.hasClass('wk-category-list-collapsed'))
                this.product_category_list.addClass("wk-category-list-collapsed");
            if(event.target && event.target &&  event.target.className && event.target.className.includes('oe_link_icon')){
                this.env.pos.get_order().select_orderline(orderline);
                var order = this.pos.get_order();
                order.display_lot_popup();
            }
        }
        back(event){
            this.showScreen('ProductListScreenWidget');
        }
    }
    CartOrderline.template = 'CartOrderline';
    Registries.Component.add(CartOrderline);
    return CartOrderline;
});
