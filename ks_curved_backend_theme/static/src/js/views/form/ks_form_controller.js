odoo.define('ks_curved_backend_theme.ks_form_controller', function(require) {
    "use strict";
    var ks_form_controller = require('web.FormController');
    var session = require("web.session");

    ks_form_controller.include({
        events: _.extend({}, ks_form_controller.prototype.events, {
            "click button.reload_form_view": "_KsReloadView",
        }),

        _KsReloadView: function() {
            this.reload();
        },

//        _KsReloadListController: function() {
//            var list_controller = Object.keys(this.getParent().controllers).filter(x=>(this.getParent().controllers[x] && this.getParent().controllers[x].viewType == 'list'))
//            if (list_controller && list_controller.length) {
//                this.getParent().controllers[list_controller[0]].widget.reload({}, false);
//            }
//        },

//        update: async function(params, options, reload_controller=true) {
//            this.mode = params.mode || this.mode;
//            var res = this._super(params, options);
//            if (reload_controller && session['ks_split_view'] && session['ks_split_view'] != 'no_split') {
//                this._KsReloadListController();
//            }
//            return res;
//        },

    });

});
