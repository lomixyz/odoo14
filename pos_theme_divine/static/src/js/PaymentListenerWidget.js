odoo.define('point_of_sale.PaymentListenerWidget', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    var utils = require('web.utils');
    var round_pr = utils.round_precision;

    class PaymentListenerWidget extends PosComponent {
        constructor() {
            super(...arguments);
            var self = this;
        }
        paymentlinefocusout(event){
            $(event.currentTarget).blur()
        }
        get_journal_image_url(journal){
            return '/web/image?model=pos.payment.method&field=image&id='+journal.id;
        }
        convert_string(amount){
            if (typeof(amount) ==  'string'){
                return parseFloat(amount.replace(/,/g, '')).toFixed(2)
            }
            else{
                return amount
            }
        }
        show_payment_types(event){
            var self = this;
            var cid = $(event.currentTarget).data('cid')
            var lines = self.env.pos.get_order().get_paymentlines();
            for ( var i = 0; i < lines.length; i++ )
                if (lines[i].cid === cid)
                    self.env.pos.get_order().select_paymentline(lines[i]);
            $(".wk-payment-line").removeClass("wk-paymentline-table-selected")
            $(event.currentTarget).closest('.wk-payment-line').addClass("wk-paymentline-table-selected");
            if(! $(event.currentTarget).next(".journal-dropdown").is(":visible")){
                $('.journal-dropdown').hide();
                $(event.currentTarget).next(".journal-dropdown").slideDown(50);
            }
            else{
                $(event.currentTarget).next(".journal-dropdown").hide();
                // self.env.click_paymentline(cid);
            }
            setTimeout(function(){
                $(".payment-lines-container").scrollTop($('.payment-lines-container')[0].scrollHeight)
            }, 100);
        }
        click_delete_paymentline(event){
            this.click_delete_paymentline($(this).data('cid'));
        }
        set_payment_method(event){
            var self = this;
            var cid = $(event.currentTarget).data('cid')
            var payment_method_id = $(event.currentTarget).attr("data-payment_methods-id");
            var selected_payment_method = self.env.pos.payment_methods_by_id[payment_method_id];
            var current_order = self.env.pos.get_order();
            var lines = current_order.get_paymentlines();
            for ( var i = 0; i < lines.length; i++ ) {
                if (lines[i].cid === cid) {
                    lines[i].payment_method = selected_payment_method;
                    lines[i].name = selected_payment_method.name;
                    if(!selected_payment_method.is_cash_count || self.env.pos.config.iface_precompute_cash){
                        lines[i].amount = 0;
                        lines[i].set_amount( Math.max(current_order.get_due(),0) );
                        current_order.select_paymentline(lines[i]);
                        $('.wk-payment-line.selected .edit').val(lines[i].get_amount());
                        // self.env.reset_input();
                    }
                    if(selected_payment_method.is_cash_count){
                        lines[i].amount = 0;
                        if(self.env.pos.config.iface_precompute_cash)
                            lines[i].set_amount( Math.max(current_order.get_due(),0) );
                        else
                            lines[i].set_amount( Math.max(0,0) );
                        current_order.select_paymentline(lines[i]);
                        $('.wk-payment-line.selected .edit').val(lines[i].get_amount());
                        // self.env.reset_input();
                    }
                    // self.env.render_paymentlines();
                    // self.env.order_changes();
                    break;
                }
            }
            $('.journal-dropdown').hide();
        }
        get currentOrder() {
            return this.env.pos.get_order();
        }
        get get_due(){
            this.order_changes();
            return this.env.pos.format_currency(
                this.currentOrder.get_due() > 0 ? this.currentOrder.get_due() : 0
            );
        }
        get get_change(){
            this.order_changes();
            return this.env.pos.format_currency(this.currentOrder.get_change());
        }
        order_changes(){
            var self = this;
            var order = self.env.pos.get_order();
            if (!order)
                return;
            else if (order.is_paid())
                $('.wk-complete-order').addClass('wk-complete-order-active');
            else
                $('.wk-complete-order').removeClass('wk-complete-order-active');
        }
        get get_total_with_tax(){
            var order = this.env.pos.get_order();
            var total = 0;
            if (order.get_orderlines().length)
                total = order ? order.get_total_with_tax() : 0;
            return this.env.pos.format_currency(total)
        }
        get paymentlines(){
            var lines = this.env.pos.get_order().get_paymentlines();
            return lines
        }
    }
    PaymentListenerWidget.template = 'PaymentListenerWidget';

    Registries.Component.add(PaymentListenerWidget);

    return PaymentListenerWidget;
});
