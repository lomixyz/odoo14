odoo.define('theme_prime.product_detail', function (require) {
'use strict';

require('website_sale.website_sale');
const publicWidget = require('web.public.widget');
const { ProductCarouselMixins } = require('theme_prime.mixins');


publicWidget.registry.TpProductRating = publicWidget.Widget.extend({
    selector: '.tp-product-rating',
    events: {
        'click': '_onClickProductRating',
    },
    _onClickProductRating: function () {
        $('.nav-link[href="#tp-product-rating-tab"]').click();
        $('html, body').animate({scrollTop: $('.tp-product-details-tab').offset().top});
    }
});

// TODO: Move below code to core files
publicWidget.registry.WebsiteSale.include({
    _updateProductImage: function ($productContainer, displayImage, productId, productTemplateId, newCarousel, isCombinationPossible) {
        var $carousel = $productContainer.find('.d_shop_product_details_carousel');
        if ($carousel.length) {
            if (window.location.search.indexOf('enable_editor') === -1) {
                var $newCarousel = $(newCarousel);
                $carousel.after($newCarousel);
                $carousel.remove();
                $carousel = $newCarousel;
                $carousel.carousel(0);
                this._startZoom();
                this.trigger_up('widgets_start_request', {$target: $carousel});
                ProductCarouselMixins._updateIDs($productContainer);
            }
            $carousel.toggleClass('css_not_available', !isCombinationPossible);
        } else {
            $carousel = $productContainer.find('#o-carousel-product');
            this._super.apply(this, arguments);
        }

        let $container = $productContainer.parents('.tp-show-variant-image');
        if ($container.length) {
            let src = $carousel.find('.tp-drift-zoom-img:first').attr('src');
            if (src !== $container.find('.tp-variant-image').attr('src')) {
                $container.find('.tp-variant-image').fadeOut(400);
                _.delay(function () {$container.find('.tp-variant-image').attr('src', src).fadeIn(650);}, 400);
            }
        }
    },
});

});
