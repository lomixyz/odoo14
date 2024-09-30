/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_redesign.ClientLine', function (require) {
    "use strict";  
    const ClientLine = require('point_of_sale.ClientLine');
    const Registries = require('point_of_sale.Registries');
    const ClientListScreen = require('point_of_sale.ClientListScreen');

    const PosResClientLine = (ClientLine) =>
        class extends ClientLine {
            constructor() {
                super(...arguments);
                this.state = {
                    detailIsShown: false,
                    editModeProps: {
                        partner: {
                            country_id: this.env.pos.company.country_id,
                            state_id: this.env.pos.company.state_id,
                        }
                    },
                };
            }
            view_customer_details(event){
                var partner = this.props.partner;
                this.showScreen("ClientDetailScreenWidget", { partner: partner });
            }
        };
    Registries.Component.extend(ClientLine, PosResClientLine);

    const PosResClientListScreen = (ClientListScreen) =>
        class extends ClientListScreen {
            constructor() {
                super(...arguments);
            }
            activateEditMode(event) {
                if(this.env.pos.config.enable_pos_theme){
                    this.showScreen('ClientAddScreen', {})
                } else {
                    super.activateEditMode(event)
                }
            }
            back() {
                if(this.env.pos.config.enable_pos_theme)
                    this.showScreen('ProductScreen');
                else
                    super.back();
            }
            confirm(){
                var self = this;
                if(this.env.pos.config.enable_pos_theme){
                    var currenctOrder = self.env.pos.get_order()
                    if($(".client-line.highlight").data('id')){
                        if (this.props.client && !this.state.selectedClient){
                            this.env.pos.get_order().set_client()
                            if (currenctOrder && currenctOrder.get_screen_data() && (currenctOrder.get_screen_data().name == 'PaymentScreen')){
                                this.showScreen('PaymentScreen');
                            } else {
                                this.showScreen('ProductScreen');
                            }
                        } else {
                            var partner = this.env.pos.db.partner_by_id[$(".client-line.highlight").data('id')]
                            this.env.pos.get_order().set_client(partner)
                            if (currenctOrder && currenctOrder.get_screen_data() && (currenctOrder.get_screen_data().name == 'PaymentScreen')){
                                this.showScreen('PaymentScreen');
                            } else {
                                this.showScreen('ProductScreen');
                            }
                        }
                    }
                } else
                    super.confirm();
            }
        };
    Registries.Component.extend(ClientListScreen, PosResClientListScreen);

    return ClientLine;
});