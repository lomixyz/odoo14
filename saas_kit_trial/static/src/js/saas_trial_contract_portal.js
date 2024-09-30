odoo.define('odoo_saas_kit_trial.saas_trial_contract_portal', function(require){
    "user strict";
    var ajax = require('web.ajax');
    var contract_id = 0;


    $(document).ready(function() {
        $('.o_portal_wrap').each(function() {
            
            $('.pay_for_trial').click(function(ev){
                contract_id = $(event.target).attr('value');
            });

            $('#button_submit').click(function(ev){
                var radio_1 = $('#radio_1').is(':checked');
                var radio_2 = $('#radio_2').is(':checked');
                if (! contract_id){
                    return
                }
                if (radio_1){
                    var new_contract = false;
                    ajax.jsonRpc('/saa/trial/pay_now', 'call', {
                        contract_id: parseInt(contract_id),
                        from_trial: true,
                        new_contract: new_contract,
                    }).then(function(){
                        location.href="/shop/cart";
                    });
                }
                else if(radio_2){
                    var new_contract = true;
                    ajax.jsonRpc('/saa/trial/pay_now', 'call', {
                        contract_id: parseInt(contract_id),
                        from_trial: true,
                        new_contract: new_contract,
                    }).then(function(){
                        location.href="/shop/cart";
                    });
                }
            }); 
            
        });
    });



});