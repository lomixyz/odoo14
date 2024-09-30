odoo.define('point_of_sale.ProductListScreenWidget', function(require) {
    'use strict';

    const { debounce } = owl.utils;
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    var utils = require('web.utils');

    class ProductListScreenWidget extends PosComponent {
        constructor() {
            super(...arguments);
            var self = this;
            this.config = null
            self.config = self.env.pos.config
            this.state = {
                query: null,
            };
            this.updateProductList = debounce(this.updateProductList, 70);
            setTimeout(function(){
                if($('.product-listview').is(":visible")){
                    $('.product-kanbanview').hide();
                    self.render_listview();
                }
                else if($('.product-kanbanview').is(":visible")){
                    $('.product-listview').hide();
                    self.render_kanbanview();
                }
            }, 200);
        }
        render_listview(){
            var self = this;
            $(".wk-product-listview-switch").addClass("product-view-switch-active");
            $(".wk-product-kanbanview-switch").removeClass("product-view-switch-active");

        }
        render_kanbanview(){
            var self = this;
            $(".wk-product-kanbanview-switch").removeClass("product-view-switch-active");
            $(".wk-product-listview-switch").addClass("product-view-switch-active");

        }
        click_list_view(event){
            $('table.product-listview').show();
            $('div.product-kanbanview').hide();
            $(".wk-product-kanbanview-switch").removeClass("product-view-switch-active");
            $(".wk-product-listview-switch").addClass("product-view-switch-active");
        }
        click_kanban_view(event){
            $('table.product-listview').hide();
            $('div.product-kanbanview').show();
            $(".wk-product-kanbanview-switch").addClass("product-view-switch-active");
            $(".wk-product-listview-switch").removeClass("product-view-switch-active");
        }
        back() {
            this.showScreen('ProductScreen');
        }
        create_product(){
            this.showScreen('ProductAddScreen');
        }
        get clients() {
            if (this.state.query && this.state.query.trim() !== '') {
                return this.env.pos.db.search_product_in_category(0, this.state.query.trim())
            } else {
                var product_ids  = this.env.pos.db.product_by_category_id[0];
                var list = [];
                if (product_ids) {
                    for (var i = 0, len = Math.min(product_ids.length, this.env.pos.db.limit); i < len; i++) {
                        list.push(this.env.pos.db.product_by_id[product_ids[i]]);
                    }
                }
                return list;
            }
        }
        updateProductList(event) {
            this.state.query = event.target.value;
            const clients = this.clients;
            this.render();
        }
    }
    
    ProductListScreenWidget.template = 'ProductListScreenWidget';

    Registries.Component.add(ProductListScreenWidget);

    return ProductListScreenWidget;
});
