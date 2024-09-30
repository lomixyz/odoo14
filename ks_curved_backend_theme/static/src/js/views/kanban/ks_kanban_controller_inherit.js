odoo.define('ks_curved_backend_theme.ks_kanban_controller_inherit', function(require) {
    "use strict";
    var ks_kanban_controller = require('web.KanbanController');
    var session = require("web.session");

    ks_kanban_controller.include({
        events: _.extend({}, ks_kanban_controller.prototype.events, {
            "click button.reload_view": "_KsReloadView",
        }),

        _KsReloadView: function() {
            this.reload();
        },

});
});