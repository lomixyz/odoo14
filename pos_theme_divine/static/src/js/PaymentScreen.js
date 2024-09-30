/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_redesign.PosResPaymentScreen', function (require) {
    "use strict";  

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    var core = require('web.core');
    var _t = core._t;

    const PosResPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            constructor() {
                super(...arguments);
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
            get orderlinesArray() {
                return this.env.pos.get_order() ? this.env.pos.get_order().get_orderlines() : [];
            }
            get_product_image_url(product) {
                return `/web/image?model=product.product&field=image_512&id=${product.id}&write_date=${product.write_date}&unique=1`;
            }
            back() {
                this.showScreen('ProductScreen');
            }
            add_payment_line(event){
                this.env.pos.get_order().add_paymentline(this.env.pos.db.pos_cash_journal);
                $('.wk-paymentline-table-selected .wk-line-amount').focus();
            }
            generate_invoice(event){
                var order = this.env.pos.get_order();
                order.set_to_invoice(!order.is_to_invoice());
                if (order.is_to_invoice())
                    $('.wk-generate-invoice').addClass('invoice-active');
                else
                    $('.wk-generate-invoice').removeClass('invoice-active');
            }
            validatecompleteorder(event){
                var order = this.env.pos.get_order();
                if (order.get_orderlines().length === 0) {
                    this.showPopup('ErrorTracebackPopup',{
                        'title': _t('Empty Order'),
                        'body':  _t('There must be at least one product in your order before it can be validated'),
                    });
                }
                else{
                    this.validate_order();
                    if(order && order.get_client()){
                        var partner_id = order.get_client().id
                        if(partner_id){
                            let partner = this.env.pos.db.partner_by_id[partner_id]
                            if(partner)
                                partner.pos_order_count+=1
                        }
                    }
                }
            }
            async selectClient() {
                if (this.env.pos.config.enable_pos_theme){
                    const currentClient = this.currentOrder.get_client();
                    this.showScreen('ClientListScreen', { client: currentClient });
                } else {
                    super.selectClient();
                }
            }
        };

    Registries.Component.extend(PaymentScreen, PosResPaymentScreen);

    return PaymentScreen;
});
