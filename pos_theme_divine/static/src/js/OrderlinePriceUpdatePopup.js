odoo.define('point_of_sale.OrderlinePriceUpdatePopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    var utils = require('web.utils');
    var field_utils = require('web.field_utils');
    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;

    // formerly OrderlinePriceUpdatePopup
    class OrderlinePriceUpdatePopup extends AbstractAwaitablePopup {
        switch_to_discount_tab(event){
            $('.qty-update-section').hide();
            $('.price-update-section').hide();
            $('.discount-update-section').show();
            $('.orderline-update-popup-tab').removeClass('tab-selected');
            $(event.currentTarget).addClass("tab-selected");
        }
        switch_to_qty_tab(event){
            $('.discount-update-section').hide();
            $('.price-update-section').hide();
            $('.qty-update-section').show();
            $('.orderline-update-popup-tab').removeClass('tab-selected');
            $(event.currentTarget).addClass("tab-selected");
        }
        switch_to_price_tab(event){
            $('.qty-update-section').hide();
            $('.discount-update-section').hide();
            $('.price-update-section').show();
            $('.orderline-update-popup-tab').removeClass('tab-selected');
            $(event.currentTarget).addClass("tab-selected");
        }
        qty_step_up(event){
            var line = this.props.orderline;
            var qty_input = parseFloat($('.wk-line-qty').val());
            if(! $.isNumeric(qty_input))
                qty_input = parseFloat(line.get_quantity());
            qty_input += 1;
            qty_input = round_pr(qty_input, 0.001);
            var input_string = field_utils.format.float(round_di(qty_input, 2), {digits: [69, 2]});
            $('.wk-line-qty').val(input_string);
        }
        qty_step_down(event){
            var line = this.props.orderline;
            var qty_input = parseFloat($('.wk-line-qty').val());
            if(! $.isNumeric(qty_input))
                qty_input = parseFloat(line.get_quantity());
            qty_input -= 1;
            qty_input = round_pr(qty_input, 0.001);
            var input_string = field_utils.format.float(round_di(qty_input, 2), {digits: [69, 2]});
            $('.wk-line-qty').val(input_string);
        }
        set_line_quantity(event){
            var self = this;
            var new_qty = $('.wk-line-qty').val();
            if($.isNumeric(new_qty)){
                $(".wk-line-qty").css("box-shadow","");
                var line = this.props.orderline;
                line.set_quantity(new_qty);
                self.cancel();
            }else{
                $(".wk-line-qty").css("box-shadow","inset 0px 0px 0px 1px #ff4545");
                $(".wk-line-qty").addClass("text_shake");
                $(".wk-line-qty").css("box-shadow","inset 0px 0px 0px 1px #ff4545");
            }
        }
        add_discount(event){
            var self = this;
            var new_discount = $('.wk-line-discount').val();
            if($.isNumeric(new_discount) && new_discount >= 0 && new_discount <= 100){
                $(".wk-line-discount").css("box-shadow","");
                var line = this.props.orderline;
                line.set_discount(parseFloat(new_discount).toFixed(2));
                self.cancel();
            }else{
                $(".wk-line-discount").css("box-shadow","inset 0px 0px 0px 1px #ff4545");
                $(".wk-line-discount").addClass("text_shake");
                $(".wk-line-discount").css("box-shadow","inset 0px 0px 0px 1px #ff4545");
            }
        }
        add_price(event){
            var self = this;
            var new_price = $('.wk-line-price').val();
            if($.isNumeric(new_price)){
                $(".wk-line-price").css("box-shadow","");
                var line = this.props.orderline;
                line.set_unit_price(parseFloat(new_price));
                line.price = parseFloat(field_utils.format.float(round_di(line.price, 2), {digits: [69, 2]}));
                line.price_manually_set = true;
                self.cancel();
            }
            else{
                $(".wk-line-price").css("box-shadow","inset 0px 0px 0px 1px #ff4545");
                $(".wk-line-price").addClass("text_shake");
                $(".wk-line-price").css("box-shadow","inset 0px 0px 0px 1px #ff4545");
            }
        }
    }
    OrderlinePriceUpdatePopup.template = 'OrderlinePriceUpdatePopup';
    OrderlinePriceUpdatePopup.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: 'Confirm ?',
        body: '',
    };

    Registries.Component.add(OrderlinePriceUpdatePopup);

    class WebkulErrorPopup extends AbstractAwaitablePopup {
		click_password_ok_button(event){
			this.cancel();
		}
    }
    WebkulErrorPopup.template = 'WebkulErrorPopup';
    WebkulErrorPopup.defaultProps = {
        title: 'Confirm ?',
        value:''
    };
    Registries.Component.add(WebkulErrorPopup);

    class WkCustomDiscountPopup extends AbstractAwaitablePopup {
		click_discount(event){
			$('#error_div').hide();
		}
		click_current_product(event){
			if (($('#discount').val())>100 || $('#discount').val()<0){
				$('#error_div').show();
				$('#customize_error').html('<i class="fa fa-exclamation-triangle" aria-hidden="true"></i > Discount percent must be between 0 and 100.')
			}
			else{
				var wk_customize_discount = parseFloat($('#discount').val())
				var reason =($("#reason").val());
				var order = this.env.pos.get_order();
				order.get_selected_orderline().set_discount(wk_customize_discount);	
				order.get_selected_orderline().custom_discount_reason=reason;
				$('ul.orderlines li.selected div#custom_discount_reason').text(reason);
				this.cancel();
			}
		}
		click_whole_order(event){
			var order = this.env.pos.get_order();
			var orderline_ids = order.get_orderlines();
			if (($('#discount').val())>100 || $('#discount').val()<0){
				$('#error_div').show();
				$('#customize_error').html('<i class="fa fa-exclamation-triangle" aria-hidden="true"></i > Discount percent must be between 0 and 100.')
			}
			else{
				var wk_customize_discount = parseFloat($('#discount').val());
				var reason =($("#reason").val());
				for(var i=0; i< orderline_ids.length; i++){
						orderline_ids[i].set_discount(wk_customize_discount);
						orderline_ids[i].custom_discount_reason=reason;
					}
				$('ul.orderlines li div#custom_discount_reason').text(reason);
				this.cancel();
			}			
		}
    }
    WkCustomDiscountPopup.template = 'WkCustomDiscountPopup';
    WkCustomDiscountPopup.defaultProps = {
        title: 'Confirm ?',
        value:''
    };
    Registries.Component.add(WkCustomDiscountPopup);

    return OrderlinePriceUpdatePopup;
});
