odoo.define('wk_saas_tool.trial_information', function(require) {
    "use strict";
    var core = require('web.core');
    var WebClient = require('web.WebClient');
    var rpc = require('web.rpc');
    var _t = core._t;
    var count = 0;
    var remaining_days = 0;
    var clear;

    WebClient.include({
        init: function(parent, client_options) {
            this.remaining_days = 0;
            this._super(parent, client_options);
            this.check_instance_life();
        },

        check_instance_life: function() {
            var self = this;
            rpc.query({
                model: 'ir.config_parameter',
                method: 'get_config_data',
                args: [], 
            }).then(function(data) {
                if (data['contract.is_expired'] == 'True'){
                    $.blockUI({ message:'Your Plan Subscription is Expired, Please buy subscription for resuming services'});
                }
                else{
                    $.unblockUI();
                }
                if (data['trial.is_trial_enabled'] == 'True'){
                    var content = '<div class="wk-destroy-info hidden-xs" id="wk-destroy-info" style="display:flex; width:45%;">'
                    var expiry_text = null;
                    if (Number(data['trial.trial_period']) == 0){
                        expiry_text = '<div class="row m-0 p-0" style="padding-top: 2% !important; padding-left: 2% !important;padding-bottom: 2%; width: 76%;"><div><span class="trial_expired_span" id="trial_expired_span" style="font-size:15px;>Trial Expired</span><span class="wk-destroy-time"></span></div>'
                    }
                    else{
                        expiry_text = '<div class="row m-0 p-0" style="padding-top: 2% !important; padding-left: 2% !important;    padding-bottom: 2%; width: 76%;"><div><span class="trial_expired_span" id="trial_expired_span" style="font-size:15px;" >Your Trial Will Expire In </span><span class="wk-destroy-time"></span></div>'
                    }
                    var common_text = '<div style="width: 99% !important;"><p style="font-size:15px;" class="trial_expired_span">Satisfied With Odoo SaaS? Sign Up for your Unique Instance.</p></div></div>';
                    var time_content = '<div class="justify-content-center flex-column d-flex"><a id ="store_link" target="_blank" class="btn btn-light btn-sm" style=" font-size:14px;" href='    +data['trial.purchase_link']+'>Purchase Now</a></div></div>';
                    content = content + expiry_text + common_text + time_content;
                    $('body').append(content);
                    remaining_days = data['trial.trial_period'];
                    self.get_secondsToHms(data);
                    clear = setInterval(
                        function() { self.get_secondsToHms(data); },
                        8.64*(10**7)
                    );
                }
            });
        },
        get_secondsToHms: function(data) {
            var days = Number(remaining_days) - count;
            if(days > 0) {
                var days = Number(remaining_days) - count;
                var result = (days)
                if (result == 1){
                    result = result + ' Day '
                }else{
                    result = result + ' Days '
                }
                $('span.wk-destroy-time').text(result);
                count++;
            }else{
                clearInterval(clear);
                $('span.trial_expired_span').text('Trial Expired ');
                $('i.fa-clock-o').hide();   
                $('span.wk-destroy-time').hide();
            }
        }
    });
});
