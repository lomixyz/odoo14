/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_redesign.ProductScreen', function (require) {
    "use strict";    
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    const { debounce } = owl.utils;
    const { useState } = owl.hooks;
    const { useRef } = owl.hooks;

    const PosResProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            constructor() {
                super(...arguments);
                var self = this;
                this.config = null
                setTimeout(function(){
                    if(self.env.pos){
                        self.config = self.env.pos.config
                        if (self.config.drawer_closed){
                            if($(".pos-drawer").hasClass("drawer-collapsed")){
                                $(".pos-rightheader").addClass("pos-rightheader-expanded")
                                if($(".subwindow-container-fix-theme.screens").hasClass("pos-subwindow-container-fix-dwr-expanded")){
                                    $(".subwindow-container-fix-theme.screens").removeClass("pos-subwindow-container-fix-dwr-expanded")
                                    $(".pos-rightheader").removeClass("pos-rightheader-expanded")
                                }
                            }
                        }
                    }
                },100);
                useListener('update-search', this._updateSearch);
                useListener('clear-search', this._clearSearch);

                this.searchTimeout = null;
                this.searchWordInput = useRef('search-word-input');
                this.updateSearch = debounce(this.updateSearch, 100);
                let status = this.showCashBoxOpening()
                this.state = useState({ cashControl: status, numpadMode: 'quantity', searchWord: ''});
            }
            async _clickProduct(event) {
                var self = this;
                super._clickProduct(event)
                setTimeout(function(){
                    self.showScreen('ClientListScreen')
                    self.showScreen('ProductScreen')
                },100)
            }
            clearSearch() {
                this.searchWordInput.el.value = '';
                this.trigger('clear-search');
            }
            updateSearch(event) {
                this.trigger('update-search', event.target.value);
            }
            _updateSearch(event) {
                this.state.searchWord = event.detail;
            }
            _clearSearch() {
                this.state.searchWord = '';
            }
            mounted(){
                $('#order_dropdown').addClass('oe_hidden');
                super.mounted();
                $('#order_select').on("mouseover", function(){
                    $('#order_dropdown').removeClass('oe_hidden');
                });
                $('#order_select').on("mouseout", function(){
                    $('#order_dropdown').addClass('oe_hidden');
                });
                $('.order-selector').on("click", '#order_select' , function(){
                    if($('#order_dropdown').hasClass('oe_hidden')){
                        $('#order_dropdown').removeClass('oe_hidden');
                    } else {
                        $('#order_dropdown').addClass('oe_hidden');
                    }
                });
                if(!$(".drawer-menu.dwr-home-menu").hasClass("drawer-btn-selected")){
                    $(".drawer-menu.dwr-home-menu").click();
                }
            }
        };

    Registries.Component.extend(ProductScreen, PosResProductScreen);
    return ProductScreen;
});
