odoo.define("ks_curved_backend_theme.Ks_darkmode_toggle", function(require) {
    "use strict";

    var SystrayMenu = require("web.SystrayMenu");
    var Widget = require("web.Widget");
    var ajax = require("web.ajax");
    var session = require("web.session");
    var quick_settings = require("ks_curved_backend_theme.ks_quick_settings_widget")
    var widgetRegistry = require("web.widget_registry");
    var core = require("web.core");
    var _t = core._t;
    var mail_activity_menu = require("mail.systray.ActivityMenu");
    var mail_message_menu = require("mail/static/src/widgets/messaging_menu/messaging_menu.js");

    mail_message_menu.include({
      sequence: 5,
    });
    mail_activity_menu.include({
      sequence: 4,
    });
    var ks_toggle_switch = Widget.extend({
        template: "ks_toggle_switch",
        events: {
            "change input#ks_menubar_dark_mode": "_onInputChange",
        },

        sequence: 7,

        willStart: async function() {
            const _super = this._super.bind(this);

            const data = await this._rpc({
                route: "/render/theme/view/data",
                params: {
                    ks_setting_scope: "User"
                },
            });
            this.data = data;
            return _super;
        },

        _onInputChange: function(ev) {
            var self = this;
            var args = {};
            var _value = ev.target.checked;

            args[$(ev.target).data('name')] = _value
            if(! _value && this.data.ks_auto_dark_mode){
                $(ev.target).prop('checked', true);
                this.do_warn(
                      _t("Error"),
                      _t("Please first turn off the auto dark mode to use this feature!")
                );
                return;
            }
            if (_value) {
                // Show auto dark mode.
                $("div#ks_auto_dark_mode_div").css("display", "block");
            } else {
                // Hide.
                $("div#ks_auto_dark_mode_div").css("display", "none");
            }

            ajax.jsonRpc("/save/theme/settings", "call", {
                ks_unsaved_setting: args,
                ks_origin_scope: "user",
            }).then(function() {
                self._KsInitiateModeChangeProcess(_value)
            });

        },

        _KsInitiateModeChangeProcess: function(_value) {
            var self = this;
            var ks_apply_dark_mode = _value;
            $('#ks_dark_mode').prop('checked', _value)
            if (this.data.ks_auto_dark_mode && this.data.ks_sun_time_info && ks_apply_dark_mode) {
                // Check theme light/dark mode based on sun time.
                var ks_current_datetime = new Date();
                var ks_sunrise_datetime = new Date("01 Jan 2000 " + this.data.ks_sun_time_info.sunrise);
                var ks_sunset_datetime = new Date("01 Jan 2000 " + this.data.ks_sun_time_info.sunset);

                //          self.trigger_up("ksCompareTime", {
                //                'ks_sunrise_datetime': ks_sunrise_datetime,
                //                'ks_sunset_datetime': ks_sunset_datetime,
                //                'ks_current_datetime': ks_current_datetime
                //            })
                if (self._ksCompareTime(ks_sunrise_datetime, ks_sunset_datetime, ks_current_datetime)) {
                    ks_apply_dark_mode = false;
                }
            }
            if (ks_apply_dark_mode)
                $("html").attr("data-color-mode", "ks-dark");
            else
                $("html").attr("data-color-mode", "ks-light");
            session.ks_current_color_mode = $("html").attr("data-color-mode");
            var quick_settings_obj = new quick_settings();
            self._ksManageCurrentColorTheme(quick_settings_obj._ksGetHeaderIconColor(session.ks_color_theme["body-background"]));
            if (document.body.classList.contains("ks_appsmenu_active"))
                self.trigger_up("ks_manage_drawer", {
                    drawer_status: 'open'
                });
        },

        /*
       * Function to compare two datetime based on times
       * return true if ks_datetime_1 < ks_datetime, otherwise false.
       */
        _ksCompareTime: function(ks_sunrise_datetime, ks_sunset_datetime, ks_current_datetime) {
            var ks_hours = ks_current_datetime.getHours();
            var ks_minutes = ks_current_datetime.getMinutes();
            var ks_seconds = ks_current_datetime.getSeconds();
            var ks_curr_time = new Date("01 Jan 2000 " + ks_hours + ":" + ks_minutes + ":" + ks_seconds);
            if (ks_sunrise_datetime < ks_curr_time && ks_curr_time < ks_sunset_datetime) {
                return true;
            }
            return false;
        },

        _ksManageCurrentColorTheme(background) {
            var ks_current_theme = session.ks_color_theme;
            var ks_header_icon_clr = background;

            // Change header icons color for light and when body color is dark.
            if (session.ks_current_color_mode == "ks-light" && ks_header_icon_clr == "white") {
                session.ks_color_theme.ks_header_icon_clr = ks_header_icon_clr;
                // Change header font icons to white.
                $("ul.o_menu_systray").addClass("ks_color_theme_dark_header");
                $(".o_main_navbar button.phone-menu-btn").addClass("ks_color_theme_dark_header");
                $(".ks_left_sidebar_panel .ks_app_sidebar .inner-sidebar button.phone-menu-btn").addClass("ks_color_theme_dark_header");
            } else if (session.ks_current_color_mode == "ks-dark" && ks_header_icon_clr == "white") {
                $("ul.o_menu_systray").removeClass("ks_color_theme_dark_header");
                $(".o_main_navbar button.phone-menu-btn").removeClass("ks_color_theme_dark_header");
                $(".ks_left_sidebar_panel .ks_app_sidebar .inner-sidebar button.phone-menu-btn").removeClass("ks_color_theme_dark_header");

            }

            // Control view bg color.
            if (session.ks_current_color_mode == "ks-light" && !ks_current_theme.default_theme) {
                document.body.style.setProperty("--ks-main-control-bg", "#FFFFFF");
                if (ks_header_icon_clr == "white") {
                    document.body.style.setProperty("--app-drawar", "#FFFFFF");
                }
            } else if (session.ks_current_color_mode == "ks-dark") {
                document.body.style.removeProperty("--ks-main-control-bg");
                document.body.style.removeProperty("--app-drawar");
            }

            if (ks_current_theme.primary) {
                document.body.style.setProperty("--primary", ks_current_theme.primary);
                if (ks_current_theme["body-background"] == ks_current_theme.primary && session.ks_current_color_mode == "ks-light") {
                    document.body.style.setProperty("--nav-primary", "#ffffff");
                } else {
                    document.body.style.removeProperty("--nav-primary");
                    document.body.style.setProperty("--nav-primary", ks_current_theme.primary);
                }
            }

            if (ks_current_theme["primary-btn"]) {
                document.body.style.setProperty("--primary-btn", ks_current_theme["primary-btn"]);
            }

            if (ks_current_theme["tooltip-heading-bg"]) {
                document.body.style.setProperty("--tooltip-heading-bg", ks_current_theme["tooltip-heading-bg"]);
            }

            if (ks_current_theme["link-color"]) {
                document.body.style.setProperty("--link-color", ks_current_theme["link-color"]);
            }

            if (ks_current_theme["heading-color"]) {
                document.body.style.setProperty("--heading-color", ks_current_theme["heading-color"]);
            }

            if (session.ks_current_color_mode == "ks-light") {
                if (ks_current_theme["body-background"]) {
                    document.body.style.setProperty("--body-background", ks_current_theme["body-background"]);
                }

                // Only apply this variable if not background image is active.
                if (!this.data.ks_body_background_image_enable) {
                    if (ks_current_theme["nav-link-color"]) {
                        document.body.style.setProperty("--nav-link-color", ks_current_theme["nav-link-color"]);
                    }
                    if (ks_current_theme["ks-over-link"]) {
                        document.body.style.setProperty("--ks-over-link", ks_current_theme["ks-over-link"]);
                    }
                } else if (this.data.ks_body_background_image_enable && !this.data.ks_body_background_img.filter((ks_data)=>{
                    return ks_data.ks_active == true;
                }
                ).length) {
                    if (ks_current_theme["nav-link-color"]) {
                        document.body.style.setProperty("--nav-link-color", ks_current_theme["nav-link-color"]);
                    }
                    if (ks_current_theme["ks-over-link"]) {
                        document.body.style.setProperty("--ks-over-link", ks_current_theme["ks-over-link"]);
                    }
                } else {
                    $("ul.o_menu_systray").removeClass("ks_color_theme_dark_header");
                    $(".o_main_navbar button.phone-menu-btn").removeClass("ks_color_theme_dark_header");
                    $(".ks_left_sidebar_panel .ks_app_sidebar .inner-sidebar button.phone-menu-btn").removeClass("ks_color_theme_dark_header");
                }

                if (ks_current_theme["tab-bg"]) {
                    document.body.style.setProperty("--tab-bg", ks_current_theme["tab-bg"]);
                }
            } else {
                // Make Dark theme
                if (ks_current_theme["body-background"]) {
                    document.body.style.removeProperty("--body-background");
                }

                // Only apply this variable if not background image is active.
                if (!this.data.ks_body_background_image_enable) {
                    if (ks_current_theme["nav-link-color"]) {
                        document.body.style.removeProperty("--nav-link-color");
                    }
                    if (ks_current_theme["ks-over-link"]) {
                        document.body.style.removeProperty("--ks-over-link");
                    }
                } else if (this.data.ks_body_background_image_enable && !this.data.ks_body_background_img.filter((ks_data)=>{
                    return ks_data.ks_active == true;
                }
                ).length) {
                    if (ks_current_theme["nav-link-color"]) {
                        document.body.style.removeProperty("--nav-link-color");
                    }
                    if (ks_current_theme["ks-over-link"]) {
                        document.body.style.removeProperty("--ks-over-link");
                    }
                }
                if (ks_current_theme["tab-bg"]) {
                    document.body.style.removeProperty("--tab-bg");
                }
            }
        },
    });

    SystrayMenu.Items.push(ks_toggle_switch);
    return ks_toggle_switch;
});
