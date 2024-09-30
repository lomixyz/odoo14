odoo.define('point_of_sale.ClientDetailScreenWidget', function(require) {
    'use strict';
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class ClientDetailScreenWidget extends PosComponent {
        constructor() {
            super(...arguments);
            this.state = {
                query: null,
                selectedClient: this.props.partner,
                detailIsShown: false,
                isEditMode: false,
                editModeProps: {
                    partner: {
                        country_id: this.env.pos.company.country_id,
                        state_id: this.env.pos.company.state_id,
                    }
                },
            };
        }
        clickBack(event){
            var self = this;
            self.showScreen('ClientListScreen')
        }
        clickEditCustomer(event){
            var self = this;
            const partner = this.props.partner;
            if(partner){
                self.showScreen('ClientEditScreen', {
                    partner: partner
                })
            }
        }
        clickSetCustomer(event){
            var self = this;
            const partner = this.props.partner;
            if(partner){
                self.env.pos.get_order().set_client(partner)
                setTimeout(function(){
                    self.showScreen('ClientListScreen')
                    self.showScreen('ProductScreen')
                },100)
            } 
        }
        get pos_order_count(){

        }
        get imageUrl() {
            const partner = this.props.partner;
            return `/web/image?model=res.partner&field=image_512&id=${partner.id}`;
        }
        back(event){
            this.showScreen('ClientListScreen');
        }
    }

    ClientDetailScreenWidget.template = 'ClientDetailScreenWidget';
    Registries.Component.add(ClientDetailScreenWidget);
    return ClientDetailScreenWidget;
});
