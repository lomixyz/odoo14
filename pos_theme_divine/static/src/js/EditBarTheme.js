odoo.define('pos_theme_divine.EditBarTheme', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useState } = owl.hooks;

    class EditBarTheme extends PosComponent {
        constructor() {
            super(...arguments);
            this.state = useState({ isColorPicker: false })
        }
    }
    EditBarTheme.template = 'EditBarTheme';

    Registries.Component.add(EditBarTheme);

    return EditBarTheme;
});