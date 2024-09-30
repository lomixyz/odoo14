/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_theme_divine.models', function (require) {
    "use strict";
    var pos_model = require('point_of_sale.models');
    var rpc = require('web.rpc');
    var SuperOrder = pos_model.Order.prototype;
    var model_list = pos_model.PosModel.prototype.models;
    var config_model = null;
    var journal_model = null;
    var product_model = null;
    var category_model = null;

    pos_model.load_fields('res.partner', ['street2','pos_order_count', 'lang', 'property_product_pricelist']);

    pos_model.load_models([{
		model:'pos.custom.discount',
		field: [],
		domain:function(self){
			return [['id','in',self.config.discount_ids]];
		},
		loaded: function(self,result) {
			self.all_discounts = result;
		}
	}]);

    //--Fetching model dictionaries--
    for(var i = 0,len = model_list.length;i<len;i++){
        if(model_list[i].model == "pos.config")
            config_model = model_list[i];
        if(model_list[i].model == "pos.payment.method")
            journal_model = model_list[i];
        if(model_list[i].model == "product.product")
            product_model = model_list[i];
        if(model_list[i].model == "pos.category")
            category_model = model_list[i];
        if(config_model != null && journal_model != null && product_model != null && category_model != null)
            break;
    }
    
    // //--Updating model dictionaries--
    var super_config_loaded = config_model.loaded;
    var super_journal_loaded = journal_model.loaded;
    var super_product_loaded = product_model.loaded;
    var super_category_loaded = category_model.loaded;

    journal_model.loaded = function(self, journals){
        super_journal_loaded.call(this,self, journals);
        self.db.pos_cash_journal = null;
        journals.forEach(function(journal){
            if(journal.is_cash_count)
                self.db.pos_cash_journal = journal;
        });
    };

    config_model.loaded = function(self,configs){
        super_config_loaded.call(this,self,configs);
        if(self.config.enable_pos_theme == true){
            // Load Screen
            // $.getScript( "/pos_theme_divine/static/src/js/ProductItemTheme.js" )
            //     .done(function( script, textStatus ) {
            //         console.log( textStatus );
            //     })
            //     .fail(function( jqxhr, settings, exception ) {
            //         $( "div.log" ).text( "Triggered ajaxError handler." );
            // });

            // Load Css chrome.css
            var fileref=document.createElement("link")
            fileref.setAttribute("rel", "stylesheet")
            fileref.setAttribute("type", "text/css")

            if(self.config.theme_color == '#FC4078'){
                fileref.setAttribute("href", '/pos_theme_divine/static/src/css/colorOption1.css')
            } else if (self.config.theme_color == '#1CCEF4') {
                fileref.setAttribute("href", '/pos_theme_divine/static/src/css/colorOption2.css')
            } else if (self.config.theme_color == '#F15F6B') {
                fileref.setAttribute("href", '/pos_theme_divine/static/src/css/colorOption3.css')
            } else if (self.config.theme_color == '#FE7D35') {
                fileref.setAttribute("href", '/pos_theme_divine/static/src/css/colorOption4.css')
            } else if (self.config.theme_color == '#18DB70') {
                fileref.setAttribute("href", '/pos_theme_divine/static/src/css/colorOption5.css')
            } else if (self.config.theme_color == '#755FFF') {
                fileref.setAttribute("href", '/pos_theme_divine/static/src/css/colorOption6.css')
            } else if (self.config.theme_color == '#0FDDFF') {
                fileref.setAttribute("href", '/pos_theme_divine/static/src/css/colorOption7.css')
            } else if (self.config.theme_color == '#9757D7') {
                fileref.setAttribute("href", '/pos_theme_divine/static/src/css/colorOption8.css')
            } else if (self.config.theme_color == '#27C499') {
                fileref.setAttribute("href", '/pos_theme_divine/static/src/css/colorOption9.css')
            } else if (self.config.theme_color == '#FF592C') {
                fileref.setAttribute("href", '/pos_theme_divine/static/src/css/colorOption10.css')
            } else if (self.config.theme_color == '#D3AC5F') {
                fileref.setAttribute("href", '/pos_theme_divine/static/src/css/colorOption11.css')
            } else if (self.config.theme_color == '#78A660') {
                fileref.setAttribute("href", '/pos_theme_divine/static/src/css/colorOption12.css')
            } else {
                fileref.setAttribute("href", '/pos_theme_divine/static/src/css/colorOption13.css')
            }

            // fileref.setAttribute("href", '/pos_theme_divine/static/src/css/pos.css')
            // console.log("fileref=================",fileref)
            document.getElementsByTagName("head")[0].appendChild(fileref);
            
            var fileref=document.createElement("link")
            fileref.setAttribute("rel", "stylesheet")
            fileref.setAttribute("type", "text/css")
            fileref.setAttribute("href", '/pos_theme_divine/static/src/css/pos_theme_divine.css')
            document.getElementsByTagName("head")[0].appendChild(fileref);

            rpc.query({
                model: 'pos.config',
                method: 'get_languages',
            })
            .then(function(lang_dict){
                self.lang_dict = lang_dict;
                self.langs = [];
                var lang_keys = Object.keys(lang_dict);
                _.each(lang_keys, function(key){
                    var vals = {};
                    vals['key'] = key;
                    vals['value']= lang_dict[key];
                    self.langs.push(vals)
                });
            })
        }
    };

    product_model.loaded = function(self, products){
        super_product_loaded.call(this,self,products);
        self.all_products = products;
    };

    category_model.loaded = function(self, categories){
        super_category_loaded.call(this,self,categories);
        self.db.wk_categories = categories.sort(function(a,b){
            return a.id - b.id;
        });
        self.wk_categories = categories.sort(function(a,b){
            return a.id - b.id;
        });
    };

    pos_model.Order = pos_model.Order.extend({
        select_order_line: function(line){
            if(this.selected_orderline){
                this.selected_orderline.set_selected(false)
            }
            if(line){
                if(line !== this.selected_orderline){
                    if(this.selected_orderline){
                        this.selected_orderline.set_selected(false);
                    }
                    // *******************************************
                    this.selected_orderline = line;
                    this.selected_orderline.set_selected(true);
                    // *******************************************
                } else {
                    if(this.selected_orderline){
                        this.selected_orderline.set_selected(true)
                    }
                }
            } else {
                this.selected_orderline = undefined;
            }
        },
    })
    
});