/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

odoo.define('wk_backup_restore.backup_process', function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');
    var update_req = false;
    
    
    publicWidget.registry.BackupProcess = publicWidget.Widget.extend({
        selector: '.backup_process_main',
    
        events : {
            'click #create_backup_process' : '_onClickBackupProcessButton',
            'click .fre_cyc_button' : '_onClickFreqCycleButton',
            'click #create_process_button' : '_onClickCreateProcessButton',
            'click #update_backup_process' : '_onClickUpdateProcessButton',
            'click #cancel_backup_process' : '_onClickCancelBackupButton',
            'click .download' : '_onClickDownloadButton',
        },

        _onClickBackupProcessButton : function(ev){
            $("#create_backup_process_model").modal("toggle");
        },

        _onClickFreqCycleButton : function(ev){
            var freq_cycle = $(event.target).text();
            var freq_cycle_code = $(event.target).attr('data-code');
            $('#btn_frq_cycle_drpdwn').text(freq_cycle);
            $('#btn_frq_cycle_drpdwn').attr('data-code', freq_cycle_code);
        },

        _onClickCreateProcessButton : function(ev){

            var freq = 1;
            var freq_cycle_code = $('#btn_frq_cycle_drpdwn').attr('data-code');
            if (freq_cycle_code == 'half_day'){
                freq = 2;
            }
            var starting_date = $('#date_time_input').val();
            if (! starting_date){
                alert('Please Enter Starting Date and Time...')
                return;
            }
            var client_id = parseInt($('#create_process_button').attr('value'));
            rpc.query({
                model: 'saas.client',
                method: 'get_create_backup_process_data',
                args: [freq, freq_cycle_code, starting_date, update_req, client_id],
            })
            .then(function(data){
                update_req = false;
                location.href= '/my/backup/files/'+data['contract_id']+'?access_token='+data['token'];
            });  
        },

        _onClickUpdateProcessButton : function(ev){
            update_req = true;
            $("#create_backup_process_model").modal("toggle");
        },

        _onClickCancelBackupButton : function(ev){
            var answer = confirm("Are You Sure You want to cancel the Backup Process..?");
            if (answer == true){
                var client_id = parseInt($('#cancel_backup_process').attr('value'));
                rpc.query({
                    model: 'saas.client',
                    method: 'get_cancel_backup_process_call',
                    args: ['self', client_id],
                })
                .then(function(data){
                    location.href= '/my/backup/files';
                });  
            }
        },

        _onClickDownloadButton : function(ev){
            var client_id = $(ev.currentTarget).attr('client_id');
            var detail_id = $(ev.currentTarget).attr('detail_id');
            var name = $(ev.currentTarget).closest('.tbody_row').find('.name_text').text();
            rpc.query({
                model : 'saas.client',
                method : 'get_download_backup_zip_call',
                args : ['self', parseInt(client_id), parseInt(detail_id), name],
            }).then(function(data){
                if (data){
                    location.href=data;
                }
                else{
                    alert('Authentication Failed...');
                }
            });
        },
    });
});