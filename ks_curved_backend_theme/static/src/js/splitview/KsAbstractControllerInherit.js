odoo.define('ks_curved_backend_theme.KsAbstractControllerInherit', function (require) {
"use strict";

var AbstractController = require('web.AbstractController');
const { ComponentWrapper } = require('web.OwlCompatibility');
var session = require("web.session");

AbstractController.include({
    start: async function () {
        // Overrrided to add split view classes
        var res = this._super.apply(this, arguments);
        if(session['ks_split_view'] && session['ks_split_view'] != 'no_split'){
            if(this.viewType == 'form'){
                this.$el.addClass('ks_splitted_page');
            }else if(this.viewType == 'list'){
                $('body').removeClass('ks_splitter horizontal-split');
            }
        }
        return res
    },
});
return AbstractController;
});