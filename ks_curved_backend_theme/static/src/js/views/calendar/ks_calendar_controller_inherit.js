odoo.define('ks_curved_backend_theme.ks_calendar_controller_inherit', function(require) {
    "use strict";
    var ks_calendar_controller = require('web.CalendarController');
    var session = require("web.session");

    ks_calendar_controller.include({
        events: _.extend({}, ks_calendar_controller.prototype.events, {
            "click button.reload_view": "_KsReloadView",
        }),

        _KsReloadView: function() {
            this.reload();
        },

    });
});