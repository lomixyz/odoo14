odoo.define('point_of_sale.ProductFormScreen', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class ProductFormScreen extends PosComponent {
        constructor() {
            super(...arguments);
            var self = this;
            self.product_type_dict = {
                'consu' : 'Consumable',
                'service' : 'Service',
                'product' : 'Stockable Product'
            }
        }
        get price() {
            const formattedUnitPrice = this.env.pos.format_currency(
                this.props.product.get_price(this.env.pos.get_order().pricelist, 1),
                'Product Price'
            );
            if (this.props.product.to_weight) {
                return `${formattedUnitPrice}/${
                    this.env.pos.units_by_id[this.props.product.uom_id[0]].name
                }`;
            } else {
                return formattedUnitPrice;
            }
        }
        get cost_price(){
            return this.env.pos.format_currency(this.props.product.standard_price)
        }
        get imageUrl() {
            const product = this.props.product;
            return `/web/image?model=product.product&field=image_512&id=${product.id}&write_date=${product.write_date}&unique=1`;
        }
        back(event){
            this.showScreen('ProductListScreenWidget');
        }
    }
    ProductFormScreen.template = 'ProductFormScreen';

    Registries.Component.add(ProductFormScreen);

    return ProductFormScreen;
});
