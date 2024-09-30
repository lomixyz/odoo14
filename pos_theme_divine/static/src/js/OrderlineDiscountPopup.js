odoo.define('point_of_sale.OrderlineDiscountPopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    var utils = require('web.utils');
    var field_utils = require('web.field_utils');
    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;
    
    class OrderlineDiscountPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            var discount_id = null;
            var wk_discount_list = this.env.pos.all_discounts;
            this.wk_discount_percentage=0;
            var discount_price=0;
            var wk_discount = null;
            setTimeout(function(){
                $(".button.apply").show();
                $(".button.apply_complete_order").show();
                $("#discount_error").hide();
            },100);
            // this.render();
        }
        async wk_ask_password(password){
            var self = this;
            var ret = new $.Deferred();
            if (password) {
                const { confirmed, payload: inputPin } = await this.showPopup('NumberPopup', {
                    isPassword: true,
                    title: this.env._t('Password ?'),
                    startingValue: null,
                });
                if (Sha1.hash(inputPin) !== password) {
                    Gui.showPopup('WebkulErrorPopup',{
                        'title':_t('Password Incorrect !!!'),
                        'body':_('Entered Password Is Incorrect ')
                    });
                } else {
                    ret.resolve();
                }
            } else {
                ret.resolve();
            }
            return ret;
        }
        click_wk_product_discount(event){
            var self = this;
            $("#discount_error").hide();
            $(".wk_product_discount").css('background','');
            $(event.currentTarget).css('background',self.env.pos.config.theme_color);
            var discount_id=parseInt($(event.currentTarget).attr('id'));
            var wk_discount_list = this.env.pos.all_discounts;
            for(var i=0; i<wk_discount_list.length; i++ ){
                if( wk_discount_list[i].id == discount_id){
                    var wk_discount = wk_discount_list[i] ;
                    this.wk_discount_percentage = this.env.pos.format_currency_no_symbol(wk_discount.discount_percent);
                }
            }
        }
        click_customize(event){
            var self = this;
            var employee = _.filter(self.env.pos.employees, function(employee){
                return employee.id == self.env.pos.get_cashier().id;
            });
            if(self.env.pos.config.allow_security_pin && employee && employee[0].pin){
                self.wk_ask_password(employee[0].pin).then(function(data){
                    Gui.showPopup('WkCustomDiscountPopup', {
                        'title': self.env._t("Customize Discount"),
                    });
                });
            }
            else{
                self.showPopup('WkCustomDiscountPopup', {
                    'title': self.env._t("Customize Discount")
                });
            }
        }
        click_apply_complete_order(event){
            var order = this.env.pos.get_order();
            if(this.wk_discount_percentage != 0){
                var orderline_ids = order.get_orderlines();
                for(var i=0; i< orderline_ids.length; i++){
                    orderline_ids[i].set_discount(this.wk_discount_percentage);
                    orderline_ids.custom_discount_reason='';
                }
                $('ul.orderlines li div#custom_discount_reason').text('');
                this.cancel();	
            }
            else{	
                $(".wk_product_discount").css("background-color","burlywood");
                setTimeout(function(){
                    $(".wk_product_discount").css("background-color","");
                },100);
                setTimeout(function(){
                    $(".wk_product_discount").css("background-color","burlywood");
                },200);
                setTimeout(function(){
                    $(".wk_product_discount").css("background-color","");
                },300);
                setTimeout(function(){
                    $(".wk_product_discount").css("background-color","burlywood");
                },400);
                setTimeout(function(){
                    $(".wk_product_discount").css("background-color","");
                },500);
                return;
            }
        }
        click_apply(event){
            var order = this.env.pos.get_order();
            if(this.wk_discount_percentage != 0){
                order.get_selected_orderline().set_discount(this.wk_discount_percentage);
                order.get_selected_orderline().custom_discount_reason='';
                $('ul.orderlines li.selected div#custom_discount_reason').text('');
                this.cancel();
            }
            else{			
                $(".wk_product_discount").css("background-color","burlywood");
                setTimeout(function(){
                    $(".wk_product_discount").css("background-color","");
                },100);
                setTimeout(function(){
                    $(".wk_product_discount").css("background-color","burlywood");
                },200);
                setTimeout(function(){
                    $(".wk_product_discount").css("background-color","");
                },300);
                setTimeout(function(){
                    $(".wk_product_discount").css("background-color","burlywood");
                },400);
                setTimeout(function(){
                    $(".wk_product_discount").css("background-color","");
                },500);
                return;
            }
        }
    }
    OrderlineDiscountPopup.template = 'OrderlineDiscountPopup';
    OrderlineDiscountPopup.defaultProps = {
        title: 'Confirm ?',
        value:''
    };
    Registries.Component.add(OrderlineDiscountPopup);

});