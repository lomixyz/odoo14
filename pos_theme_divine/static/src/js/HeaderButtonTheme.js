odoo.define('point_of_sale.HeaderButtonTheme', function(require) {
    'use strict';

    const { useState } = owl;
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    // Previously HeaderButtonWidget
    // This is the close session button
    class HeaderButtonTheme extends PosComponent {
        constructor() {
            super(...arguments);
            this.state = useState({ label: 'LOGOUT' });
            this.confirmed = null;
        }
        get translatedLabel() {
            return this.env._t(this.state.label);
        }
        onClick() {
            if (!this.confirmed) {
                this.state.label = 'CONFIRM';
                this.confirmed = setTimeout(() => {
                    this.state.label = 'LOGOUT';
                    this.confirmed = null;
                }, 2000);
            } else {
                this.trigger('close-pos');
            }
        }
    }
    HeaderButtonTheme.template = 'HeaderButtonTheme';

    Registries.Component.add(HeaderButtonTheme);

    return HeaderButtonTheme;
});
