odoo.define('theme_prime.suggested_product_slider', function (require) {
'use strict';

const publicWidget = require('web.public.widget');
const { _t } = require('web.core');

publicWidget.registry.TpSuggestedProductSlider = publicWidget.Widget.extend({
    selector: '.tp-suggested-product-slider',
    start: function () {
        const $owlSlider = this.$('.owl-carousel');
        const responsiveParams = {0: {items: 2}, 576: {items: 2}, 768: {items: 2}, 992: {items: 2}, 1200: {items: 3}};
        if (!this.$target.data('two-block')) {
            _.extend(responsiveParams, {768: {items: 3}, 992: {items: 4}, 1200: {items: 5}});
        }
        $owlSlider.removeClass('d-none');
        $owlSlider.owlCarousel({
            dots: false,
            margin: 15,
            stagePadding: 6,
            autoplay: true,
            autoplayTimeout: 3000,
            autoplayHoverPause: true,
            rewind: true,
            rtl: _t.database.parameters.direction === 'rtl',
            responsive: responsiveParams,
        });
        this.$('.tp-prev').click(function() {
            $owlSlider.trigger('prev.owl.carousel');
        });
        this.$('.tp-next').click(function() {
            $owlSlider.trigger('next.owl.carousel');
        });
        return this._super.apply(this, arguments);
    },
});

});
