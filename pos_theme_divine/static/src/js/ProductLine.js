odoo.define('point_of_sale.ProductLine', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class ProductLine extends PosComponent {
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
        get imageUrl() {
            const product = this.props.product;
            return `/web/image?model=product.product&field=image_128&id=${product.id}&write_date=${product.write_date}&unique=1`;
        }
        spaceClickProductAction(event){
            this.showScreen("ProductFormScreen", { product: this.props.product });
        }
    }
    ProductLine.template = 'ProductLine';

    Registries.Component.add(ProductLine);

    return ProductLine;
});
