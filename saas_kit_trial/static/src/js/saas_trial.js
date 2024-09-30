odoo.define('odoo_saas_kit_trial.saas_trial', function(require){
    "user strict";
    var rpc = require('web.rpc');
    var ajax = require('web.ajax');

    $(document).ready(function() {
        $('.oe_website_sale').each(function () {
            $('.get_trial').on('click',function(event){
                var product_id = $(".product_id").attr('value');
                var quantity = $(".quantity").val();
                var saas_users = parseInt($('#new_min_user').val());
                ajax.jsonRpc("/saas/trial/add/product", 'call', {
                    'product_id': product_id,
                    'quantity': quantity,
                    'saas_users': saas_users,
                }).then(function(a){
                    location.href='/shop/cart';
                });
            });
        });
    });

});