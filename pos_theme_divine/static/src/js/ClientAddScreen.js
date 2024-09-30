odoo.define('point_of_sale.ClientAddScreen', function(require) {
    'use strict';

    const { getDataURLFromFile } = require('web.utils');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    var rpc = require('web.rpc');
    var utils = require('web.utils');

    class ClientAddScreen extends PosComponent {
        constructor() {
            super(...arguments);
            this.intFields = ['country_id', 'state_id', 'property_product_pricelist'];
            this.changes = {};
        }
        clickBack(){
            this.showScreen('ClientListScreen');
        }
        mounted() {
            this.env.bus.on('save-customer', this, this.saveChanges);
        }
        willUnmount() {
            this.env.bus.off('save-customer', this);
        }
        clickCreateCustomer(){
            var self = this;
            let processedChanges = {};
            for (let [key, value] of Object.entries(this.changes)) {
                if (this.intFields.includes(key)) {
                    processedChanges[key] = parseInt(value) || false;
                } else {
                    processedChanges[key] = value;
                }
            }
            processedChanges.id = false;

            rpc.query({
                model: 'res.partner',
                method: 'create_from_ui',
                args: [processedChanges],
            })
            .then(function(result){
                processedChanges["id"] = result
                self.env.pos.db.partner_by_id[result] = processedChanges
                var partner_search_string = "";

                if (self.env.pos.db.partner_by_id[result]) {
                    var partner = self.env.pos.db.partner_by_id[result];

                    partner.address = (partner.street ? partner.street + ', ': '') +
                                    (partner.zip ? partner.zip + ', ': '') +
                                    (partner.city ? partner.city + ', ': '') +
                                    (partner.state_id ? partner.state_id[1] + ', ': '') +
                                    (partner.country_id ? partner.country_id[1]: '');
                    self.env.pos.db.partner_search_string += utils.unaccent(self._partner_search_string(partner));
                }
                self.showScreen("ClientDetailScreenWidget", { partner: self.env.pos.db.partner_by_id[result] });
            })
            .catch(function (reason){
                var error = reason.message;
                self.showPopup('ErrorTracebackPopup', {
                    title: error,
                    body: error,
                });
            });
        }
        _partner_search_string(partner){
            var str =  partner.name || '';
            if(partner.barcode){
                str += '|' + partner.barcode;
            }
            if(partner.address){
                str += '|' + partner.address;
            }
            if(partner.phone){
                str += '|' + partner.phone.split(' ').join('');
            }
            if(partner.mobile){
                str += '|' + partner.mobile.split(' ').join('');
            }
            if(partner.email){
                str += '|' + partner.email;
            }
            if(partner.vat){
                str += '|' + partner.vat;
            }
            str = '' + partner.id + ':' + str.replace(':','') + '\n';
            return str;
        }
        get partnerImageUrl() {
            // We prioritize image_1920 in the `changes` field because we want
            // to show the uploaded image without fetching new data from the server.
            if (this.changes.image_1920) {
                return this.changes.image_1920;
            } else {
                return false;
            }
        }
        captureChange(event) {
            this.changes[event.target.name] = event.target.value;
        }
        saveChanges() {
            let processedChanges = {};
            for (let [key, value] of Object.entries(this.changes)) {
                if (this.intFields.includes(key)) {
                    processedChanges[key] = parseInt(value) || false;
                } else {
                    processedChanges[key] = value;
                }
            }
            processedChanges.id = this.props.partner.id || false;
            this.trigger('save-changes', { processedChanges });
        }
        async uploadImage(event) {
            const file = event.target.files[0];
            if (!file.type.match(/image.*/)) {
                await this.showPopup('ErrorPopup', {
                    title: this.env._t('Unsupported File Format'),
                    body: this.env._t(
                        'Only web-compatible Image formats such as .png or .jpeg are supported.'
                    ),
                });
            } else {
                const imageUrl = await getDataURLFromFile(file);
                const loadedImage = await this._loadImage(imageUrl);
                if (loadedImage) {
                    const resizedImage = await this._resizeImage(loadedImage, 800, 600);
                    this.changes.image_1920 = resizedImage.toDataURL();
                    // Rerender to reflect the changes in the screen
                    this.render();
                }
            }
        }
        _resizeImage(img, maxwidth, maxheight) {
            var canvas = document.createElement('canvas');
            var ctx = canvas.getContext('2d');
            var ratio = 1;

            if (img.width > maxwidth) {
                ratio = maxwidth / img.width;
            }
            if (img.height * ratio > maxheight) {
                ratio = maxheight / img.height;
            }
            var width = Math.floor(img.width * ratio);
            var height = Math.floor(img.height * ratio);

            canvas.width = width;
            canvas.height = height;
            ctx.drawImage(img, 0, 0, width, height);
            return canvas;
        }
        /**
         * Loading image is converted to a Promise to allow await when
         * loading an image. It resolves to the loaded image if succesful,
         * else, resolves to false.
         *
         * [Source](https://stackoverflow.com/questions/45788934/how-to-turn-this-callback-into-a-promise-using-async-await)
         */
        _loadImage(url) {
            return new Promise((resolve) => {
                const img = new Image();
                img.addEventListener('load', () => resolve(img));
                img.addEventListener('error', () => {
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Loading Image Error'),
                        body: this.env._t(
                            'Encountered error when loading image. Please try again.'
                        ),
                    });
                    resolve(false);
                });
                img.src = url;
            });
        }
    }
    ClientAddScreen.template = 'ClientAddScreen';

    Registries.Component.add(ClientAddScreen);

    return ClientAddScreen;
});
