odoo.define('theme_prime.snippets.options', function (require) {
'use strict';

const {_t, qweb} = require('web.core');
const {HotspotMixns, ProductsMixin} = require('theme_prime.mixins');
const options = require('web_editor.snippets.options');
const website_options = require('website.editor.snippets.options');
const SnippetConfigurator = require('theme_prime.dialog.snippet_configurator_dialog');
const SnippetRegistry = require('theme_prime.snippet_registry');
const DialogWidgetRegistry = require('theme_prime.dialog_widgets_registry');
const {loadImageInfo} = require('web_editor.image_processing');
const weWidgets = require('wysiwyg.widgets');
const Select2Dialog = require('theme_prime.dialog.product_selector');

options.registry.TpImageHotspot = options.Class.extend({
    /**
     * @override
     */
    start() {
        this.$target.on('image_changed.TpImageHotspot', this._onImgChanged.bind(this));
        return this._super(...arguments);
    },
    /**
     * @override
     */
    async willStart() {
        const _super = this._super.bind(this);
        await this._loadAttachmentInfo();
        return _super(...arguments);
    },
    /**
     * @override
     */
    destroy() {
        this.$target.off('.TpImageHotspot');
        return this._super(...arguments);
    },
    /**
     * Loads the image's attachment info.
     *
     * @private
     */
    async _loadAttachmentInfo() {
        const img = this._getImage();
        // Used 'loadImageInfo' here thanks to image processing mechanism
        // You know i'm saying thank you to myself :) i've developed image processing logic for the cropimage feature in 2018.
        // https://github.com/odoo/odoo/commit/d66e260391ce6c55b55be358202fddfab4a9139d
        await loadImageInfo(img, this._rpc.bind(this));
        if (!img.dataset.originalId) {
            this.originalId = null;
            this.originalSrc = null;
            return;
        }
        this.originalId = img.dataset.originalId;
        this.originalSrc = img.dataset.originalSrc;
    },
    /**
     * @private
     */
    async _autoUpdateImage() {
        await this._loadAttachmentInfo();
        await this.updateUI();
    },
    /**
     * No need to write comment here Method name says everything.
     *
     * @private
     */
    toggleImgHotspot(previewMode, widgetValue, params) {
        const widgetVal = widgetValue ? JSON.parse(widgetValue) : false;
        if (widgetVal) {
            this.$target.wrap("<div class='d-flex tp-img-hotspot-wrapper'><div class='position-relative d-inline-block'></div></div>");
            // center image must remain in center
            if (this.$target.hasClass('mx-auto')) {
                let $target = this._getHotSpotWrapper();
                $target.find('.position-relative').addClass('mx-auto');
            }
        } else if (this._getHotSpotWrapper().length) {
            this._cleanHotspotNode();
        }
        // toggleClass at last so _cleanHotspotNode method have correct state
        this.$target.toggleClass('tp-img-hotspot-enable', widgetVal);
    },
    /**
     * @override
     */
    _computeVisibility() {
        const img = this._getImage();
        if (!['image/jpeg', 'image/png'].includes(img.dataset.mimetype)) {
            this._cleanHotspotNode();
            return false;
        }
        const src = img.getAttribute('src');
        return src && src !== '/';
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Add Pointer.
     *
     * @private
     */
    addHotspot(previewMode, widgetValue, params) {
        const hotspotID = _.uniqueId('tphotspot');
        let $wrapper = this._getHotSpotWrapper();
        const selector = _.str.sprintf(_t("#%s"), hotspotID);
        $wrapper.append($('<span/>', {'id': hotspotID, 'class': 'tp_hotspot tp_hotspot_style_1 tp-hotspot-primary position-absolute', 'style': 'top:50%;left:50%;'}));
        let $snippet = $wrapper.find(selector);
        let values = {hotspotType: 'static', titleText: "Your title", subtitleText: "Theme prime is best theme", buttonLink: '/', buttonText: 'SHOP NOW', imageSrc: '/theme_prime/static/src/img/s_config_data.png'};
        this._setDefaultValues($snippet, values);
        this.trigger_up('activate_snippet', {$snippet: $snippet});
    },
    /**
     * Add Pointer.
     *
     * @private
     */
    _cleanHotspotNode() {
        if (this._isHotspotEnable()) {
            this._getHotSpotWrapper().find('.tp_hotspot').remove();
            this.$target.unwrap().unwrap();
        }
    },
    /**
     * Returns the image that is currently being modified.
     *
     * @private
     * @returns {HTMLImageElement} the image to use for modifications
     */
    _getImage() {
        return this.$target[0];
    },
    /**
     * Returns wrapper.
     *
     * @private
     */
    _getHotSpotWrapper: function () {
        return this.$target.parents('.tp-img-hotspot-wrapper');
    },
    /**
     * @override
     */
    _computeWidgetState: function (methodName, params) {
        if (methodName === 'toggleImgHotspot') {
            return this._isHotspotEnable();
        }
        return this._super(...arguments);
    },
    /**
     * @override
     */
    _computeWidgetVisibility: function (widgetName, params) {
        switch (widgetName) {
            case 'add_hotspot': {
                return this._isHotspotEnable();
            }
        }
        return this._super(...arguments);
    },
    /**
     * @private
     */
    _isHotspotEnable: function () {
        return this.$target.hasClass('tp-img-hotspot-enable');
    },
    /**
     * @private
     */
    _setDefaultValues($snippet, values) {
        _.each(values, function(index, key) {
            $snippet[0].dataset[key] = values[key];
        });
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * Must need to reload image :)
     *
     * @private
     * @param {Event} ev
     */
    async _onImgChanged(ev) {
        this.trigger_up('snippet_edition_request', {exec: async () => {
            await this._autoUpdateImage();
        }});
    },
});

options.registry.TpImageHotspotConfig = options.Class.extend(HotspotMixns, ProductsMixin, {
    // Product widget is for dropdownTemplate in select2
    xmlDependencies: ['/theme_prime/static/src/xml/frontend/image_hotspot.xml', '/theme_prime/static/src/xml/editor/widgets/products_widget.xml'],
    /**
     * @override
     */
    start: function () {
        this.rangeWidgetTopId = _.uniqueId('rangeWidgetTop');
        this.rangeWidgetLeftId = _.uniqueId('rangeWidgetLeftId');
        this.$el.find('we-range[data-set-top] input[type="range"]').on(`input.${this.rangeWidgetTopId}`, _.throttle((ev) => {this.setTop(true, $(ev.currentTarget).val())}, 50));
        this.$el.find('we-range[data-set-left] input[type="range"]').on(`input.${this.rangeWidgetLeftId}`, _.throttle((ev) => {this.setLeft(true, $(ev.currentTarget).val())}, 50));
        this.PreviewEnabled = false;
        return this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    destroy: function () {
        this._super.apply(this, arguments);
        if (!this.$target.height()) {
            this._removeTpPopover(true);
        }
        this.$el.find('we-range[data-set-top] input[type="range"]').off(`.${this.rangeWidgetTopId}`);
        this.$el.find('we-range[data-set-left] input[type="range"]').off(`.${this.rangeWidgetLeftId}`);
    },

    //--------------------------------------------------------------------------
    // Options
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    setHotspotType(previewMode, widgetValue, params) {
        this._removeTpPopover();
        // Clean Attrs for other type
        if (widgetValue === 'dynamic' && !this.$target[0].dataset['onHotspotClick']) {
            this.$target[0].dataset['onHotspotClick'] = 'popover';
        }
    },
    /**
    * @private
    */
    setTitleText(previewMode, widgetValue, params) {
        this._removeTpPopover();
        this.$target[0].dataset['titleText'] = widgetValue;
    },
    /**
    * @private
    */
    setStaticImage(previewMode, widgetValue, params) {
        this._removeTpPopover();
        this.OpenMediaDialog();
    },
    /**
    * @private
    */
    setSubtitleText(previewMode, widgetValue, params) {
        this._removeTpPopover();
        this.$target[0].dataset['subtitleText'] = widgetValue;
    },
    /**
    * @private
    */
    setButtonText(previewMode, widgetValue, params) {
        this._removeTpPopover();
        this.$target[0].dataset['buttonText'] = widgetValue;
    },
    /**
    * @private
    */
    setButtonLink(previewMode, widgetValue, params) {
        this._removeTpPopover();
        this.$target[0].dataset['buttonLink'] = widgetValue;
    },
    /**
    * @private
    */
    setTop(previewMode, widgetValue, params) {
        this._removeTpPopover();
        this.$target.get(0).dataset.top = widgetValue;
        this.$target.css({top: widgetValue + '%'});
    },
    /**
    * @private
    */
    setLeft(previewMode, widgetValue, params) {
        this._removeTpPopover();
        this.$target.get(0).dataset.left = widgetValue;
        this.$target.css({left: widgetValue + '%'});
    },
    /**
     * @private
     */
    setProduct(previewMode, widgetValue, params) {
        let productId = this.$target.get(0).dataset.productId;
        if (productId) {
            this._fetchProductsData([productId]).then(data => {
                this._openDialog(parseInt(productId), data.products);
            });
        } else {
            this._openDialog();
        }
    },
    /**
    * @private
    */
    renderHotspotPreview(previewMode, widgetValue, params) {
        this.PreviewEnabled = !this.PreviewEnabled;
        this.$el.find('[data-name="hotspot_priview"] .fa-eye').toggleClass('text-success', this.PreviewEnabled);
        this._openPopover();
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _computeWidgetState(methodName, params) {
        switch (methodName) {
            case 'setTop':
                return this.$target.get(0).dataset.top || 50;
            case 'setLeft':
                return this.$target.get(0).dataset.left || 50;
            case 'setButtonLink':
                return this.$target.get(0).dataset.buttonLink || '/';
            case 'setButtonText':
                return this.$target.get(0).dataset.buttonText || 'SHOP NOW';
            case 'setSubtitleText':
                return this.$target.get(0).dataset.subtitleText || "Theme prime is best theme";
            case 'setTitleText':
                return this.$target.get(0).dataset.titleText || "Your title";
        }
        return this._super(...arguments);
    },
    /**
     * Open a mediaDialog to select/upload image.
     *
     * @private
     * @param {MouseEvent} ev
     */
    OpenMediaDialog: function (ev) {
        var self = this;
        var $image = $('<img/>');
        var mediaDialog = new weWidgets.MediaDialog(this, {
            onlyImages: true,
            res_model: 'ir.ui.view',
        }, $image[0]);
        mediaDialog.open();
        mediaDialog.on('save', this, function (image) {
            this.$target[0].dataset['imageSrc'] = $(image).attr('src');
        });
    },
    /**
     * Open popover.
     *
     * @private
     */
    _openPopover: function () {
        if (this.PreviewEnabled) {
            this.$target.popover({
                animation: true,
                container: 'body',
                html: true,
                trigger: 'manual',
                content: qweb.render('theme_prime.tp_img_static_template', {widget: this, data: this._getHotspotConfig()}),
            }).on('shown.bs.popover', function () {
                // $popover must be const otherwise it will crash the browser :|
                const $popover = $($(this).data("bs.popover").tip);
                $popover.addClass('tp-popover-element');
            }).popover('show');
        } else {
            this._removeTpPopover();
        }
    },
    /**
     * Open a mediaDialog to select/upload image.
     *
     * @private
     * @param {Boolean} force true if not $target in DOM
     */
    _removeTpPopover: function (force) {
        if (force) {
            $('.tp-popover-element').remove();
        } else {
            this.$target.popover('dispose');
        }
        this.PreviewEnabled = false;
        this.$el.find('[data-name="hotspot_priview"] .fa-eye').removeClass('text-success');
    },
    _openDialog: function (productID, products) {
        let ProductDialog = new Select2Dialog(this, {
            records: products,
            multiSelect: true,
            recordsIDs: productID ? [productID] : false,
            routePath: '/theme_prime/get_product_by_name',
            fieldLabel: _t("Select Product"),
            dropdownTemplate: 'd_select2_products_dropdown',
            select2Limit: 1,
        });
        ProductDialog.on('d_product_pick', this, function (ev) {
            let product = ev.data.result;
            if (product.length) {
                this.$target[0].dataset['productId'] = product[0];
            }
        });
        ProductDialog.open();
    },
});

options.registry.droggol_product_snippet = options.Class.extend({

    //--------------------------------------------------------------------------
    // Options
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    onBuilt: function () {
        this._super();
        this._openDialog();
    },
    /**
     * @see this.selectClass for parameters
     */
    setGrid: function (previewMode, value, $opt) {
        this._openDialog();
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _getConfiguratorParams: function () {
        this.usedAttrs = [];
        let self = this;
        let snippet = this.$target.attr('data-ds-id');
        let params = {};
        let snippetConfig = SnippetRegistry.get(snippet);
        let defaultValue = snippetConfig.defaultValue;
        _.each(snippetConfig.widgets, function (widget) {
            let attr = DialogWidgetRegistry.get(widget).prototype.d_attr;
            self.usedAttrs.push(attr);
            let attrValue = self.$target.attr(attr);
            let widgetVal = attrValue ? JSON.parse(attrValue) : false;
            if (defaultValue) {
                widgetVal = widgetVal || {};
                _.extend(widgetVal, defaultValue);
            }
            params[widget] = widgetVal;
        });
        return params;
    },
    /**
     * @private
     */
    _setConfiguratorParams: function (widgets) {
        var self = this;
        _.each(widgets, function (widget) {
            self.$target.attr(widget.d_attr, JSON.stringify(widget.value));
        });
    },
    /**
     * @private
     */
    _openDialog: function () {
        this.SnippetConfigurator = new SnippetConfigurator(this, {
            widgets: this._getConfiguratorParams()
        });
        this.SnippetConfigurator.on('d_final_pick', this, function (ev) {
            this._setConfiguratorParams(ev.data);
            this._refreshPublicWidgets();
        });
        this.SnippetConfigurator.on('cancel', this, function () {
            var self = this;
            var hasAttr = false;
            _.each(this.usedAttrs, function (attr) {
                if (self.$target[0].hasAttribute(attr)) {
                    hasAttr = true;
                }
            });
            if (!hasAttr) {
                // remove snippet on Discard
                this.$target.remove();
            }
        });
        this.SnippetConfigurator.open();
    },
});

});
