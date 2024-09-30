odoo.define('pos_dotmatrix_printer', function (require) {
"use strict";
    const models = require('point_of_sale.models');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const OrderReceipt = require('point_of_sale.OrderReceipt');

    class PosTicketFormat extends PosComponent {
        constructor() {
            super(...arguments);
            this._receiptEnv = this.props.order.getOrderReceiptEnv();
        }
        willUpdateProps(nextProps) {
            this._receiptEnv = nextProps.order.getOrderReceiptEnv();
        }
        get receipt() {
            return this.receiptEnv.receipt;
        }
        get orderlines() {
            return this.receiptEnv.orderlines;
        }
        get paymentlines() {
            return this.receiptEnv.paymentlines;
        }
        get isTaxIncluded() {
            return Math.abs(this.receipt.subtotal - this.receipt.total_with_tax) <= 0.000001;
        }
        get receiptEnv () {
          return this._receiptEnv;
        }
        isSimple(line) {
            return (
                line.discount === 0 &&
                line.unit_name === 'Units' &&
                line.quantity === 1 &&
                !(
                    line.display_discount_policy == 'without_discount' &&
                    line.price != line.price_lst
                )
            );
        }
        text_format(text,size){
        	var text_name = text.toString();
        	var text_len = size - text_name.length
        	for(var i=0;i<text_len;i++){
        		text_name+=" ";
        	}
            return text_name;
        }
        text_format_left(text,size){
        	var text_name = "";
        	var text_len = size - text.toString().length
        	for(var i=0;i<text_len;i++){
        		text_name+=" ";
        	}
        	text_name = text_name +''+ text.toString();
            return text_name;
        }
    }
    PosTicketFormat.template = 'PosTicketFormat';
    Registries.Component.add(PosTicketFormat);

    const PosReceiptScreen = (ReceiptScreen) =>
        class extends ReceiptScreen {
            async print_dotmatrix_receipt() {  
            	var url = this.env.pos.config.dotmatrix_printers_ip+"dotmatrix/print";
            	var order = this.env.pos.get_order();
                const fixture = document.createElement('div');
                const orderReceipt = new (Registries.Component.get(PosTicketFormat))(this, { order });
                await orderReceipt.mount(fixture);
                const p_data = orderReceipt.el.outerHTML;
                if (!p_data){
                    alert('No data to print. Please click Update Printer Data');
                    return;
                }
                console.log(p_data);
                $.ajax({
                    type: "POST",
                    url: url,
                    data: {
                        printer_data : p_data
                    },
                    success: function(data) {
                        alert('Success');
                        console.log(data);
                    },
                    error: function(data) {
                        alert('Failed');
                        console.log(data);
                    },
                });            
            }
        }

    Registries.Component.extend(ReceiptScreen, PosReceiptScreen);

    return PosTicketFormat;

});

