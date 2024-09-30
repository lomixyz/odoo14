odoo.define('sh_account_parent.hierarchy_widget', function (require) {
    'use strict';
    
    var core = require('web.core');
    var Widget = require('web.Widget');
    
    var QWeb = core.qweb;
    
    var _t = core._t;

    var HierarchyWidget = Widget.extend({

        events: {
            'click span.sh_account_foldable': 'fold',
            'click span.sh_account_unfoldable': 'unfold',
        },

        init: function(parent,action) {
            this.given_context = parent.given_context;
            this._super.apply(this, arguments);
        },
        start: function() {
            QWeb.add_template("/sh_account_parent/static/src/xml/account_hierarchy_report_line.xml");
            return this._super.apply(this, arguments);
        },

        removeLine: function(element) {
            var self = this;
            var el, $el;
            var rec_id = element.data('id');
            var $accountEl = element.nextAll('tr[data-parent_id=' + rec_id + ']')
            for (el in $accountEl) {
                $el = $($accountEl[el]).find(".sh_account_domain_line_0, .sh_account_domain_line_1");
                if ($el.length === 0) {
                    break;
                }
                else {
                    var $nextEls = $($el[0]).parents("tr");
                    self.removeLine($nextEls);
                    $nextEls.remove();
                }
                $el.remove();
            }
            return true;
        },

        fold: function(e) {
            this.removeLine($(e.target).parents('tr'));
            var active_id = $(e.target).parents('tr').find('td.sh_account_reports_unfoldable').data('id');
            $(e.target).parents('tr').find('span.sh_account_foldable').replaceWith(QWeb.render("unfoldable", {lineId: active_id}));
            // $(e.target).parents('tr').toggleClass('o_coa_unfolded');
        },

        autounfold: function(target) {
            var self = this;
            var currentTd = $(target).parents('tr').find('td.sh_account_reports_unfoldable')
            var account_id = currentTd.data('id');
            var wizard_id = currentTd.data('wizard_id');
            var level = currentTd.data('level');
            var currentTr = $(target).parents('tr');
            this._rpc({
                model : 'sh.account.hierarchy.wizard',
                method: this.given_context.hierarchy_based_on  == 'account' ? 'get_account_line_data' : 'get_account_type_line_data',
                args: [parseInt(account_id),parseInt(level) + 1,this.given_context],
            })
            .then(function (lines){
                _.each(lines, function (line) { 
                    currentTr.after(QWeb.render("report_account_lines", {data: line}));
                    currentTr = currentTr.next();
                    if (line["auto_unfold"]) {
                       if (currentTr && line.unfoldable) {
                           self.autounfold(currentTr.find(".fa-caret-right"));
                       }
                    }
            	});

            });
        
            $(target).parents('tr').find('span.sh_account_unfoldable').replaceWith(QWeb.render("foldable", {lineId: account_id}));
            // $(target).parents('tr').toggleClass('o_coa_unfolded');
    
        },

        unfold: function(ev) {
            this.autounfold($(ev.target));
        },
    });

    return HierarchyWidget
});