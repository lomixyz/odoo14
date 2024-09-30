odoo.define('traccar_fleet_tracking.CalendarView', function (require) {
"use strict";

    var CalendarView = require('web.CalendarView');
    CalendarView.include({
        init: function (viewInfo, params) {
            this._super.apply(this, arguments);
            if (this.controllerParams.modelName == 'fleet.vehicle.day.trip' || this.controllerParams.modelName == 'fleet.vehicle.location.history') {
                this.loadParams.editable = false;
                this.loadParams.creatable = false;
            }
        },
    });

    return CalendarView;
});