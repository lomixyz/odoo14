odoo.define('mail.systray.UserNotificationMenu', function (require) {
    "use strict";

    var core = require('web.core');
    var mailUtils = require('mail.utils');

    var session = require('web.session');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;



    var mailUtils = require('mail.utils');
    var time = require('web.time');
    /**
     * Menu item appended in the systray part of the navbar, redirects to the next
     * activities of all app
     */
    var UserNotificationMenu = Widget.extend({
        name: 'firebase_menu',
        template: 'mail.systray.UserNotificationMenu',
        events: {
            'click .o_mail_preview': '_onPushNotificationClick',
            'click .sh_view_read_all_btn': '_onClickReadAllNotification',
            'click .sh_view_all_btn': '_onClickAllNotification',
            'show.bs.dropdown': '_onActivityMenuShow',
        },
        
        _onPushNotificationClick: function (event) {
            // fetch the data from the button otherwise fetch the ones from the parent (.o_mail_preview).
            var data = _.extend({}, $(event.currentTarget).data(), $(event.target).data());
            var context = {};
            var self = this;
            this._rpc({
                model: 'sh.user.push.notification',
                method: 'write',
                args: [data.id, { 'msg_read': true }],
            }).then(function () {                
                self._updateActivityPreview();
                self._updateCounter();
                if (data.res_model != '')
                    self.do_action({
                        type: 'ir.actions.act_window',
                        name: data.res_model,
                        res_model: data.res_model,
                        views: [[false, 'form'], [false, 'tree']],
                        search_view_id: [false],
                        domain: [['id', '=', data.res_id]],
                        res_id: data.res_id,
                        context: context,
                    }, {
                        clear_breadcrumbs: true,
                    });
            });

        },
        _onClickReadAllNotification: function (event) {

            var self = this;
            self._rpc({
                model: 'res.users',
                method: 'systray_get_firebase_all_notifications',
                args: [],
                kwargs: { context: session.user_context },
            }).then(function (data, counter) {

                self._notifications = data[0];

                _.each(data[0], function (each_data) {                   
                    self._rpc({
                        model: 'sh.user.push.notification',
                        method: 'write',
                        args: [each_data.id, { 'msg_read': true }],
                    }).then(function () {
                        self._updateActivityPreview();
                        self._updateCounter();
                    });
                });

            });

        },
        _onClickAllNotification: function (event) {
            this.do_action({
                type: 'ir.actions.act_window',
                name: 'Notifications',
                res_model: 'sh.user.push.notification',
                views: [[false, 'list']],
                view_mode: "list",
                target: 'current',
                domain: [['user_id', '=', session.uid]],
            }, {
                clear_breadcrumbs: true,
            });
        },

        _onNotification: function (notification) {
            var self = this;
            // Old versions passes single notification item here. Convert it to the latest format.
            for (var i = 0; i < notification.length; i++) {
                var channel = notification[i][0];
                if (channel[1] == 'sh.user.push.notifications') {
                    this._updateActivityPreview();
                    this._updateCounter();
                    $(document).find(".o_searchview_input").click()
                    $(document).click()
                }
            }
        },
        willStart: async function () {
            var self = this;
            // return $.when(this.call('mail_service', 'isReady'));
        },
        start: function () {
            var self = this;
            this._$activitiesPreview = this.$('.o_notification_systray_dropdown_items');
            this.call("bus_service", "updateOption", "sh.user.push.notifications", session.uid);
            this.call("bus_service", "onNotification", this, this._onNotification);
            this._updateActivityPreview();
            this._updateCounter();
            this._rpc({
                model: 'sh.user.push.notification',
                method: 'has_bell_notification_enabled',
                args: [],
            })
            .then(function (result){
                self.$el.find('.js_bell_notification');
                if (result.has_bell_notification_enabled){
                      self.$el.removeClass('d-none');
                  }else{
                      self.$el.addClass('d-none');
                  }
            });
            return this._super();
        },


        //--------------------------------------------------
        // Private
        //--------------------------------------------------
        /**
         * Make RPC and get current user's activity details
         * @private
         */
        _getActivityData: function () {
            var self = this;

            return self._rpc({
                model: 'res.users',
                method: 'systray_get_firebase_notifications',
                args: [],
                kwargs: { context: session.user_context },
            }).then(function (data, counter) {

                self._notifications = data[0];
                self._counter = data[1];

                _.each(data[0], function (each_data) {

                    each_data['datetime'] = mailUtils.timeFromNow(moment(time.auto_str_to_date(each_data['datetime'])))
                });
                self._updateCounter();
            });
        },
        /**
         * Get particular model view to redirect on click of activity scheduled on that model.
         * @private
         * @param {string} model
         */
        _getActivityModelViewID: function (model) {
            return this._rpc({
                model: model,
                method: 'get_activity_view_id'
            });
        },
        /**
         * Update(render) activity system tray view on activity updation.
         * @private
         */
        _updateActivityPreview: function () {
            var self = this;
            self._getActivityData().then(function () {
                self._$activitiesPreview.html(QWeb.render('mail.systray.FirebaseMenu.Previews', {
                    notifications: self._notifications
                }));                
            });
        },
        /**
         * update counter based on activity status(created or Done)
         * @private
         * @param {Object} [data] key, value to decide activity created or deleted
         * @param {String} [data.type] notification type
         * @param {Boolean} [data.activity_deleted] when activity deleted
         * @param {Boolean} [data.activity_created] when activity created
         */
        _updateCounter: function () {
            var counter = this._counter;
            if (counter > 0) {
                this.$('.o_notification_counter').text(counter);
            } else {
                this.$('.o_notification_counter').text('');
            }
        },

        /**
         * Redirect to specific action given its xml id
         * @private
         * @param {MouseEvent} ev
         */
        _onActivityActionClick: function (ev) {
            ev.stopPropagation();
            var actionXmlid = $(ev.currentTarget).data('action_xmlid');
            this.do_action(actionXmlid);
        },
        /**
         * @private
         */
        _onActivityMenuShow: async function () {
            await this._updateActivityPreview(); 
        },
    });

    SystrayMenu.Items.push(UserNotificationMenu);
    return UserNotificationMenu;

});