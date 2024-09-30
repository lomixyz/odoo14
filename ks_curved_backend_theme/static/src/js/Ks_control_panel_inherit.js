odoo.define('ks_curved_backend_theme.Ks_control_panel_inherit.js', function (require) {
    "use strict";

   var control = require('web.ControlPanel')
   const ControlPanel = require('web.ControlPanel');
   var session = require("web.session");

   // Overrided to add a method which will return the flag that wether a user is using the system through mobile device or pc
   ControlPanel.patch('inherit_control', T => class extends T {

//         constructor() {
//            super(...arguments);
//            this.props['ks_breadcrumb_style'] = session['ks_breadcrumb_style']
//        }

        mounted() {
            super.mounted();
//            this._attachAdditionalContent();
            this.props['ks_breadcrumb_style'] = session['ks_breadcrumb_style'];
            // add breadcrumb class
            $('ol.ks_custom_breadcrumb').addClass(session['ks_breadcrumb_style']);
        }

        get KsIsMobileDevice() {
            return this.env.device.isMobile;
        }
   });
});


