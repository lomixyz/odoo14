odoo.define('traccar_fleet_tracking', function (require) {
    var fieldRegistry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');

    var BokehMap = AbstractField.extend({
        start: function() {
            var val = this.value;
            this.$el.html(val);
        }
    });

    fieldRegistry.add('bokeh_map', BokehMap);
    return BokehMap;
});
