/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_redesign.PosResClientListScreen', function (require) {
    "use strict";  
    const ClientListScreen = require('point_of_sale.ClientListScreen');
    const Registries = require('point_of_sale.Registries');
    var core = require('web.core');
    var _t = core._t;

    const PosResClientListScreen = (ClientListScreen) =>
        class extends ClientListScreen {
            constructor() {
                super(...arguments);
            }
            confirm() {
                if(this.env.pos.config.enable_pos_theme){
                    this.env.pos.get_order().set_client(this.state.selectedClient)
                    this.showScreen('ProductScreen')
                } else {
                    super.confirm();
                }
            }
            back() {
                if(this.env.pos.config.enable_pos_theme){
                    this.showScreen('ProductScreen');
                } else {
                    super.back();
                }
            }
        };

    Registries.Component.extend(ClientListScreen, PosResClientListScreen);
    return ClientListScreen;
});
