odoo.define('ks_curved_backend_theme.ks_pivot_controller_inherit', function(require) {
    "use strict";
    var ks_pivot_controller = require('web.PivotController');
    var session = require("web.session");

    ks_pivot_controller.include({
        events: _.extend({}, ks_pivot_controller.prototype.events, {
            "click button.reload_view": "_KsReloadView",
        }),

        _KsReloadView: function() {
            this.reload();
        },

});
});