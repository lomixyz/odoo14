/*
    This module create by: thanhchatvn@gmail.com
 */
odoo.define('pos_retail.offline', function (require) {
    const models = require('point_of_sale.models');
    const core = require('web.core');
    const retailModel = require('pos_retail.model')
    const bigData = require('pos_retail.big_data')
    const productItem = require('pos_retail.ProductItem')

    let _super_PosModel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        load_server_data: function () {
            console.log('load_server_data for offline mode')
            const self = this;
            this.offlineModel = false
            return _super_PosModel.load_server_data.apply(this, arguments).then(function () {
                console.log('load_server_data for offline started')
                core.bus.on('connection_lost', self, self._onConnectionLost);
                core.bus.on('connection_restored', self, self._onConnectionRestored);
            })
        },

        _onConnectionLost() {
            console.error('Network of odoo server turn off. Please checking your network or waiting Odoo Server online back')
            this.offlineModel = true
            this.set_synch('disconnected', 'Offline')
        },

        _onConnectionRestored() {
            console.warn('Network of odoo server Restored')
            this.offlineModel = false
            this.set_synch('connected', '')
        },

        _save_to_server: function (orders, options) {
            if (!this.offlineModel) {
                return _super_PosModel._save_to_server.call(this, orders, options)
            } else {
                console.error('_save_to_server() Network of odoo server turn off. Please checking your network or waiting Odoo Server online back')
                this.set_synch('disconnected', 'Offline')
                return Promise.resolve([]);
            }
        },

        getStockDatasByLocationIds(product_ids = [], location_ids = []) {
            if (!this.offlineModel) {
                return _super_PosModel.getStockDatasByLocationIds.call(this, product_ids, location_ids)
            } else {
                console.error('getStockDatasByLocationIds() Network of odoo server turn off. Please checking your network or waiting Odoo Server online back')
                return Promise.resolve(null);
            }
        },

    })
})