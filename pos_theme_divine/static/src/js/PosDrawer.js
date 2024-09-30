/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_theme_divine.PosDrawer', function (require) {
    "use strict";
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class PosDrawer extends PosComponent {
        constructor() {
            super(...arguments);
            var self = this;
            this.config = this.env.config;
        }
        spaceClickCustomerScreen(event) {
            const currentClient = this.env.pos.get_order().get_client();
            this.showScreen('ClientListScreen', 
                { client: currentClient }
            );
            this.select_menu_item();
        }
        spaceClickProductScreen() {
            this.showScreen('ProductScreen');
            this.select_menu_item();
        }
        spaceClickProductListScreen(){
            this.showScreen('ProductListScreenWidget');
            this.select_menu_item();
        }
        select_menu_item(){
            var self = this;
            event.stopPropagation();
            $(".drawer-menu").removeClass("drawer-btn-selected");
            $(".drawer-menu").css("background", '');
            $(event.currentTarget).addClass("drawer-btn-selected");
        }
        spaceClickCollapseSlider(event){
            var self = this;
            $(".pos-drawer").toggleClass("drawer-collapsed")
            $(".pos-rightheader").toggleClass("pos-rightheader-expanded")
            $(".subwindow-container-fix-theme.screens").toggleClass("pos-subwindow-container-fix-dwr-expanded");
            
            if(this.env.pos.config.drawer_closed){
                this.env.pos.config.drawer_closed = false
                $(".drawer-footer .drawer-btn-img").html("&lt;&lt;")

            } else {
                this.env.pos.config.drawer_closed = true
                $(".drawer-footer .drawer-btn-img").html("&gt;&gt;")
            }
        }
        get get_logo(){
            var self = this;
            if(self.env.pos && self.env.pos.config && !self.env.pos.config.pos_logo)
                return false;
            var img = new Image();
            img.onload = function() {
                var ratio = 1;
                var targetwidth = 300;
                var maxheight = 150;
                if( img.width !== targetwidth ){
                    ratio = targetwidth / img.width;
                }
                if( img.height * ratio > maxheight ){
                    ratio = maxheight / img.height;
                }
                var width  = Math.floor(img.width * ratio);
                var height = Math.floor(img.height * ratio);
                var c = document.createElement('canvas');
                    c.width  = width;
                    c.height = height;
                var ctx = c.getContext('2d');
                    ctx.drawImage(img,0,0, width, height);
                self.env.pos.pos_logo_base_64 = c.toDataURL();
            };
            if(self.env.pos && self.env.pos.config && self.env.pos.config.id){
                img.src = window.location.origin + '/web/image?model=pos.config&field=pos_logo&id='+self.env.pos.config.id;
                return window.location.origin + '/web/image?model=pos.config&field=pos_logo&id='+self.env.pos.config.id
            }
            else
                return false
        }
        get nGuests() {
            return this.currentOrder ? this.currentOrder.get_customer_count() : 0;
        }
        async spaceClickGuests(event){
            const { confirmed, payload: inputNumber } = await this.showPopup('NumberPopup', {
                startingValue: this.nGuests,
                cheap: true,
                title: this.env._t('Guests ?'),
            });

            if (confirmed) {
                this.env.pos.get_order().set_customer_count(parseInt(inputNumber, 10) || 1);
            }
        }
        async spaceClickDiscount(event){
            var self = this;
            const { confirmed, payload } = await this.showPopup('NumberPopup',{
                title: this.env._t('Discount Percentage'),
                startingValue: this.env.pos.config.discount_pc,
            });
            if (confirmed) {
                const val = Math.round(Math.max(0,Math.min(100,parseFloat(payload))));
                await self.apply_discount(val);
            }
        }
        async apply_discount(pc) {
            var order    = this.env.pos.get_order();
            var lines    = order.get_orderlines();
            var product  = this.env.pos.db.get_product_by_id(this.env.pos.config.discount_product_id[0]);
            if (product === undefined) {
                await this.showPopup('ErrorPopup', {
                    title : this.env._t("No discount product found"),
                    body  : this.env._t("The discount product seems misconfigured. Make sure it is flagged as 'Can be Sold' and 'Available in Point of Sale'."),
                });
                return;
            }

            // Remove existing discounts
            var i = 0;
            while ( i < lines.length ) {
                if (lines[i].get_product() === product) {
                    order.remove_orderline(lines[i]);
                } else {
                    i++;
                }
            }

            // Add discount
            // We add the price as manually set to avoid recomputation when changing customer.
            var base_to_discount = order.get_total_without_tax();
            if (product.taxes_id.length){
                var first_tax = this.pos.taxes_by_id[product.taxes_id[0]];
                if (first_tax.price_include) {
                    base_to_discount = order.get_total_with_tax();
                }
            }
            var discount = - pc / 100.0 * base_to_discount;

            if( discount < 0 ){
                order.add_product(product, {
                    price: discount,
                    lst_price: discount,
                    extras: {
                        price_manually_set: true,
                    },
                });
            }
        }
        async spacePrintKitchenOrder(event){
            const order = this.env.pos.get_order();
            if (order.hasChangesToPrint()) {
                const isPrintSuccessful = await order.printChanges();
                if (isPrintSuccessful) {
                    order.saveChanges();
                } else {
                    await this.showPopup('ErrorPopup', {
                        title: 'Printing failed',
                        body: 'Failed in printing the changes in the order',
                    });
                }
            }
        }
        spaceClickTransfer(event){
            this.env.pos.transfer_order_to_different_table();
        }
        get selectedOrderline() {
            return this.env.pos.get_order().get_selected_orderline();
        }
        async spaceOrderlineNote(event){
            if (!this.selectedOrderline) return;

            const { confirmed, payload: inputNote } = await this.showPopup('TextAreaPopup', {
                startingValue: this.selectedOrderline.get_note(),
                title: this.env._t('Add Note'),
            });

            if (confirmed) {
                this.selectedOrderline.set_note(inputNote);
            }
        }
        get currentOrder() {
            return this.env.pos.get_order();
        }
        async spaceClickPricelist(event){
            const selectionList = this.env.pos.pricelists.map(pricelist => ({
                id: pricelist.id,
                label: pricelist.name,
                isSelected: pricelist.id === this.currentOrder.pricelist.id,
                item: pricelist,
            }));

            const { confirmed, payload: selectedPricelist } = await this.showPopup(
                'SelectionPopup',
                {
                    title: this.env._t('Select the pricelist'),
                    list: selectionList,
                }
            );

            if (confirmed) {
                this.currentOrder.set_pricelist(selectedPricelist);
            }
            
        }
        async spaceClickFiscalPosition(event){
            const currentFiscalPosition = this.currentOrder.fiscal_position;
            const fiscalPosList = [
                {
                    id: -1,
                    label: this.env._t('None'),
                    isSelected: !currentFiscalPosition,
                },
            ];
            for (let fiscalPos of this.env.pos.fiscal_positions) {
                fiscalPosList.push({
                    id: fiscalPos.id,
                    label: fiscalPos.name,
                    isSelected: currentFiscalPosition
                        ? fiscalPos.id === currentFiscalPosition.id
                        : false,
                    item: fiscalPos,
                });
            }
            const { confirmed, payload: selectedFiscalPosition } = await this.showPopup(
                'SelectionPopup',
                {
                    title: this.env._t('Select Fiscal Position'),
                    list: fiscalPosList,
                }
            );
            if (confirmed) {
                this.currentOrder.fiscal_position = selectedFiscalPosition;
                // IMPROVEMENT: The following is the old implementation and I believe
                // there could be a better way of doing it.
                for (let line of this.currentOrder.orderlines.models) {
                    line.set_quantity(line.quantity);
                }
                this.currentOrder.trigger('change');
            }
        }
        async spaceClickPrintBill(event){
            const order = this.env.pos.get_order();
            if (order.get_orderlines().length > 0) {
                await this.showTempScreen('BillScreen');
            } else {
                await this.showPopup('ErrorPopup', {
                    title: this.env._t('Nothing to Print'),
                    body: this.env._t('There are no order lines'),
                });
            }
        }
        async spaceClickSplitBill(event){
            const order = this.env.pos.get_order();
            if (order.get_orderlines().length > 0) {
                this.showScreen('SplitBillScreen');
            }
        }
        async spaceClickTip(event){
            const tip = this.currentOrder.get_tip();
            const change = this.currentOrder.get_change();
            let value = tip.toFixed(this.env.pos.decimals);
            if (tip === 0 && change > 0) {
                value = change;
            }
            const { confirmed, payload } = await this.showPopup('NumberPopup', {
                title: tip ? this.env._t('Change Tip') : this.env._t('Add Tip'),
                startingValue: value,
            });
            if (confirmed) {
                this.currentOrder.set_tip(parseFloat(payload));
            }
        }
        get addedClasses() {
            if (!this.currentOrder) return {};
            const changes = this.currentOrder.hasChangesToPrint();
            const skipped = changes ? false : this.currentOrder.hasSkippedChanges();
            return {
                highlight: changes,
                altlight: skipped,
            };
        }
    }
    PosDrawer.template = 'PosDrawer';
    Registries.Component.add(PosDrawer);
    return PosDrawer;
});
