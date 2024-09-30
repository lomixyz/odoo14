odoo.define('sh_account_parent.account_hierarchy', function (require) {
    'use strict';
    
    var Dialog = require("web.Dialog");
    var Widget = require("web.Widget");
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var session = require('web.session');
    var framework = require('web.framework');
    var rpc = require("web.rpc");
    var HierarchyWidget = require('sh_account_parent.hierarchy_widget');


    var AccountHierarchy = AbstractAction.extend({
        
        init: function(parent, action) {
            this.actionManager = parent;
            this.given_context = action.context;
            this._super.apply(this, arguments);
        },

        willStart: function() {
            return Promise.all([this._super.apply(this, arguments), this.get_html()]);
        },

        set_html: function() {
            var self = this;
            var def = Promise.resolve();
            console.log(this)
            if (!this.hierarchy_widget){
                this.hierarchy_widget = new HierarchyWidget(this,this.given_context)
                def = this.hierarchy_widget.appendTo(this.$('.o_content'));
            }

            return def.then(function () {
                self.hierarchy_widget.$el.html(self.html);
                
                if (self.given_context.auto_unfold) {
                    _.each(self.$el.find('.fa-caret-right'), function (line) {
                        self.hierarchy_widget.autounfold(line);
                    });
                }
            });
          
        },

        start: async function() {
            await this._super(...arguments);
            this.set_html();
        },

        get_html: async function() {
            var self = this
            var defs = [];
            return await this._rpc({
                args: [self.given_context],
                method: 'get_html',
                model: 'sh.account.hierarchy.wizard',
            })
            .then(function (result){
                self.html = result.html;
                self.renderButtons();
                self.update_cp();
            });
            
            // this.renderButtons();
        },

        update_cp: function() {
            if (!this.$buttons) {
                this.renderButtons();
            }
            var status = {
                cp_content: {$buttons: this.$buttons},
            };
            console.log(this.updateControlPanel(status),status)
            return this.updateControlPanel(status);
        },

        renderButtons: function() {

            var self = this;
            this.$buttons = $(core.qweb.render("AccountPrintReports.buttons", {}));
            
            return this.$buttons;

        },

        do_show: function() {
            this._super();
            this.update_cp();
        },

    });
    
    
    core.action_registry.add('account_hierarchy', AccountHierarchy);
    
    return AccountHierarchy;

});