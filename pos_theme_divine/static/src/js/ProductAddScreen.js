odoo.define('point_of_sale.ProductAddScreen', function(require) {
    'use strict';

    var pos_model = require('point_of_sale.models');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    var rpc = require('web.rpc');

    class ProductAddScreen extends PosComponent {
        constructor() {
            super(...arguments);
            setTimeout(function(){
                $('.wk-category-list').hide()
                $('.wk-product-type-list').hide()
                $('.wk-product-categ-list').hide()
                $(".wk-product-edit-input").val("")
            }, 100);
        }
        product_category_dropdown(event){
            event.preventDefault();
            if($('.wk-category-list').is(":visible"))
                $('.wk-category-list').hide();
            else{
                $('.pos-category-dropdown-element').hide();
                $('.wk-category-list').show();
                $('.wk-product-type-list').hide();
                $('.wk-product-categ-list').hide();
            }
        }
        select_product_category(event){
            var lang_key = $(event.currentTarget).attr('lang_key');
            var language = (lang_key != 0 ? this.env.pos.db.category_by_id[lang_key] : 'N/A');
            $('.client-language-text').attr('lang_key',lang_key);
            if(language == 'N/A') 
                $('.client-language-text').text(language);
            else
                $('.client-language-text').text(language.name);
        }

        product_type_dropdown(event){
            if($('.wk-product-type-list').is(":visible"))
                $('.wk-product-type-list').hide();
            else{
                $('.pos-product-type-dropdown-element').hide();
                $('.wk-product-type-list').show();
                $('.wk-product-categ-list').hide();
                $('.wk-category-list').hide();
            }
        }
        select_product_type(event){
            var value = $(event.currentTarget).attr('value');
            $('.product-type-text').attr('value',value);
            if(value){
                if(value == 'none')
                    $('.product-type-text').text('N/A');
                else if(value == 'consu')
                    $('.product-type-text').text('Consumable');
                else if(value == 'service')
                    $('.product-type-text').text('Service');
                else if(value == 'product')
                    $('.product-type-text').text('Stockable Product');
            }
        }

        product_categ_dropdown(event){
            if($('.wk-product-categ-list').is(":visible"))
                $('.wk-product-categ-list').hide();
            else{
                $('.product-categ-dropdown-element').hide();
                $('.wk-product-categ-list').show();
                $('.wk-product-type-list').hide();
                $('.wk-category-list').hide();
            }
        }
        select_product_categ(event){
            var self = this;
            var lang_key = $(event.currentTarget).attr('lang_key');
            var language = 'N/A'
            if(lang_key !=0){
                _.each(self.env.pos.product_categories, function(categ){
                    if(categ && categ.id == lang_key){
                        language = categ
                    }
                });
            }
            $('.product-categ-text').attr('lang_key',lang_key);
            if(language == 'N/A') 
                $('.product-categ-text').text(language);
            else
                $('.product-categ-text').text(language.name);
        }

        save_product_data(event){
            var self = this;
            var product_name = $('.product-name-input').val()
            var product_price = $('.product-price-input').val()
            var product_barcode = $('.product-barcode-input').val()
            var product_internal_ref = $('.product-internal-ref-input').val()
            var product_cost =  $('.product-cost-input').val()
            var product_pos_categ_id = $('.client-language-text').attr('lang_key')
            var product_type = $('.product-type-text').attr('value')
            var product_category = $('.product-categ-text').attr('lang_key')

            var fields = {}
            fields['name'] = product_name
            fields['lst_price'] = product_price 
            if(product_barcode){
                fields['barcode'] = product_barcode
            }
            fields['default_code'] = product_internal_ref
            fields['standard_price'] = product_cost
            fields['available_in_pos'] = true
            if(product_pos_categ_id != '0'){
                fields['pos_categ_id'] = parseInt(product_pos_categ_id)
            }
            else{
                fields['pos_categ_id'] = false
            }
            fields['type'] = product_type
            fields['categ_id'] = product_category

            if(product_barcode){
                let barcode_product_exist = self.env.pos.db.get_product_by_barcode(product_barcode);
                if(barcode_product_exist){
                    self.showPopup('ErrorPopup',{
                        'title': 'Barcode Error !!',
                        'body':  "Barcode already Exist."
                    });
                    return;
                }
            }

            if(!fields['name']){
                $(".product-name-input").css("box-shadow","inset 0px 0px 0px 1px #ff4545");
                $(".product-name-input").addClass("text_shake");
                return;
            }
            if(!fields['lst_price']){
                $(".product-price-input").css("box-shadow","inset 0px 0px 0px 1px #ff4545");
                $(".product-price-input").addClass("text_shake");
                return;
            }

            rpc.query({
                model: 'product.product',
                method: 'create',
                args: [fields],
            })
            .then(function(product_id){
                fields['id'] = product_id
                fields['taxes_id'] = []
                fields['tracking'] = 'none'
                var product =  new pos_model.Product({}, fields);
                
                if(product_id){
                    product.taxes_id = []
                    product.tracking = 'none'
                    product.display_name = product_name
                    self.env.pos.db.product_by_id[product.id] = product;
                    self.env.pos.db.product_by_category_id[0].unshift(product.id);
                    if(product.pos_categ_id && product.pos_categ_id.length){
                        if(self.env.pos.db.product_by_category_id[product.pos_categ_id[0]])
                            self.env.pos.db.product_by_category_id[product.pos_categ_id[0]].unshift(product.id);
                        self.env.pos.db.category_search_string[self.env.pos.db.root_category_id] += self.env.pos.db._product_search_string(product)
                        self.env.pos.db.category_search_string[product.pos_categ_id[0]] += self.env.pos.db._product_search_string(product)
                    }
                    else
                        self.env.pos.db.category_search_string[self.env.pos.db.root_category_id] += self.env.pos.db._product_search_string(product)
                    if(product.barcode)
                        self.env.pos.db.product_by_barcode[product.barcode] = product;
                    self.env.pos.all_products.unshift(self.env.pos.db.product_by_id[product_id])
                }
                if(product_id)
                    self.showScreen('ProductListScreenWidget')
            })
            .catch(function (reason){
                var error = reason.message;
                self.showPopup('ErrorTracebackPopup', {
                    title: error,
                    body: error,
                });
            });
        }
        
        back(event){
            this.showScreen('ProductListScreenWidget');
        }
    }
    ProductAddScreen.template = 'ProductAddScreen';

    Registries.Component.add(ProductAddScreen);

    return ProductAddScreen;
});
