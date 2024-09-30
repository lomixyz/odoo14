odoo.define('ks_curved_backend_theme.ks_graph_controller_inherit', function(require) {
    "use strict";
    var ks_graph_controller = require('web.GraphController');
    var session = require("web.session");

    ks_graph_controller.include({
        events: _.extend({}, ks_graph_controller.prototype.events, {
            "click button.reload_view": "_KsReloadView",
        }),

        _KsReloadView: function() {
            this.reload();
        },

});
});