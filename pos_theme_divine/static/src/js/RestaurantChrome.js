/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_redesign.RestaurantChrome', function (require) {
    "use strict";  
    const RestaurantChrome = require("pos_restaurant.chrome");
    const Registries = require('point_of_sale.Registries');

    const PosResRestaurantChrome = (RestaurantChrome) =>
        class extends RestaurantChrome {
            _actionAfterIdle() {
                super._actionAfterIdle();
                $(".pos-drawer ").hide()
                $(".subwindow-container div").addClass("subwindow-container-fix-floors")
                $(".subwindow-container div").removeClass("pos-subwindow-container-fix-dwr-expanded")
                $(".order-selector").hide();
                $(".table-seats").hide();
                $(".table-seats-theme").show();
            }
        };
    Registries.Component.extend(RestaurantChrome, PosResRestaurantChrome);
});