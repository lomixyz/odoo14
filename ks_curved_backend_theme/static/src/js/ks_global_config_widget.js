odoo.define("ks_curved_backend_theme.ks_global_config_widget", function(require) {
    "use strict";

    var core = require("web.core");
    var Widget = require("web.Widget");
    var widgetRegistry = require("web.widget_registry");
    var ajax = require("web.ajax");
    var utils = require("web.utils");
    var Dialog = require("web.Dialog");
    var session = require("web.session");
    var QWeb = core.qweb;
    var _t = core._t;

    var QWeb = core.qweb;

    var KsGlobalConfigWidget = Widget.extend({
        template: "ks_global_settings",

        file_type_magic_word: {
            "/": "jpg",
            R: "gif",
            i: "png",
            P: "svg+xml",
        },

        events: _.extend({}, Widget.prototype.events, {
            "click .ks_global_apply_scope": "_ksApplyScope",
            "change input": "_onInputChange",
            "click .ks_save_global_data": "_ksSaveGlobalData",
            "click .ks_body_background_del_global, .ks_drawer_background_global_del": "_ksDelBackgroundImage",
            "click .ks_login_background_image_del": "_ksDelLoginBackgroundImage",
            "click .ks_login_background_color_del": "_ksDelLoginBackgroundColor",
            "click .ks_background_default_global": "_ksBackgroundDefault",
            "click .ks_drawer_background_default_global": "_ksDrawerDefault",
            "click button.ks_setting_cancel_global": "_ksSettingCancel",
            "click .ks_global_theme_edit": "_ksColorThemeEdit",
            "click button#ks_add_custom_theme_global": "_ksCustomColorThemeAdd",
            "click .ks_theme_edit_cancel": "_ksColorThemeCancel",
            "click .ks_new_theme_save": "_ksColorThemeSave",
            "click .ks_theme_edit_update": "_ksColorThemeUpdate",
            "click .ks_global_theme_delete": "_ksColorThemeDelete",
            "click .ks_global_reset_color_theme": "_ksColorThemeResetToDefault",
            "click .ks_add_login_color": "_ksLoginPageBgColor",
        }),
        // Todo: Take reference from Ribbon widget
        init: function(parent, data, options) {
            this.ks_unsaved_data = {};
            this.ks_unsaved_theme_global_data = {};
            this.ks_dirty_data = {}
            this.ks_global_theme_fields = ["ks_body_background", "ks_menu", "ks_menu_hover", "ks_button", "ks_border", "ks_heading", "ks_link", "ks_primary_color", "ks_tooltip", "name", ];
            this._super.apply(this, arguments);
        },

        /**
       * @override
       **/
        willStart: async function() {
            const _super = this._super.bind(this);
            const data = await this._rpc({
                args: [],
                method: "ks_get_config_values",
                model: "ks.global.config",
            });
            const ks_theme_global_data = await this._rpc({
                route: "/render/theme/view/data",
                params: {
                    ks_setting_scope: "Global"
                },
            });
            if (data) {
                this.data = data;
            }
            if (ks_theme_global_data) {
                this.ks_color_theme_scope = ks_theme_global_data.ks_color_theme_scope == "Global" ? true : false;
                this.ks_theme_global_data = ks_theme_global_data;
            }
            return _super(...arguments);
        },

        on_attach_callback: function() {
            this._ksAttachImageZoom();
        },

        _ksAttachImageZoom(){
            $(".ks_image_hover").attr("data-zoom", 1);
            $(".ks_image_hover").zoomOdoo({
                event: "mouseenter",
                attach: ".ks_back_img_hover",
                zoom: true,
                attachToTarget: true,
                beforeAttach: function() {
                    this.$flyout.css({
                        width: "125px",
                        height: "125px"
                    });
                },
            });
        },

        _ksColorThemeResetToDefault: function() {
            this.ks_unsaved_data = {}
            var default_color_theme = this.ks_theme_global_data.ks_color_theme.predefined.filter(x=>x.ks_default)
            if (default_color_theme.length) {
                this.ks_unsaved_theme_global_data['ks_theme_color'] = default_color_theme[0]['id'];
                this._ksSaveGlobalData();
            }
        },

        _render: function() {
            this._super.apply(this, arguments);
            var ks_self = this;
        },

        _ksApplyScope: function() {
            var self = this;
            if (this.ks_unsaved_data) {
                this._rpc({
                    args: [this.ks_unsaved_data],
                    method: "ks_save_apply_scope",
                    model: "ks.global.config",
                }).then(function() {
                    self.do_action("reload_context");
                });
            }
        },

        _onInputChange: function(ev) {
            var self = this;
            if (!$(ev.currentTarget).parents('#global_theme_edit_section').length) {
                if (ev.currentTarget.name && ev.currentTarget.dataset.value != this.data[ev.currentTarget.name] && ev.currentTarget.hasAttribute("ks_curve_scope_input")) {
                    this.ks_unsaved_data[ev.currentTarget.name] = ev.currentTarget.dataset.value;
                    self.ks_dirty_data[ev.currentTarget.name] = $(ev.currentTarget);
                } else if (ev.currentTarget.name) {
                    delete this.ks_unsaved_data[ev.currentTarget.name];
                }

                // Condition to change global setting fields and boolean fields.
                if (ev.currentTarget.name.split("scope").length < 2 && !$(ev.currentTarget).hasClass("ks_binary_field")) {
                    this.ks_unsaved_theme_global_data[ev.currentTarget.name] = ev.currentTarget.dataset.value ? ev.currentTarget.dataset.value : ev.currentTarget.checked;
                    self.ks_dirty_data[ev.currentTarget.name] = $(ev.currentTarget);
                }
                if ($(ev.currentTarget).attr("class") && $(ev.currentTarget).attr("class").includes("slider")) {
                    $(ev.currentTarget).siblings(".ks_opacity_value_max").html(ev.currentTarget.value);
                    this.ks_unsaved_theme_global_data[ev.currentTarget.name] = ev.currentTarget.value;
                    self.ks_dirty_data[ev.currentTarget.name] = $(ev.currentTarget);
                }

                // Manage data for text fields.
                if (ev.currentTarget.name && ev.currentTarget.dataset.type == "ks-char") {
                    this.ks_unsaved_theme_global_data[ev.currentTarget.name] = ev.currentTarget.value;
                    self.ks_dirty_data[ev.currentTarget.name] = $(ev.currentTarget);
                }

                // Handle binary field fields.
                // Set background image active true.
                if ($(ev.currentTarget).hasClass("ks_binary_field")) {
                    var file_node = ev.target;
                    // Handle body background input change.
                    if (file_node.getAttribute("data-model")) {
                        var ks_img_src = $(file_node.nextElementSibling).find("img").attr("src");
                        var ks_value = self._ksDecodeURLToString(ks_img_src);
                        if (file_node.id.split("#")[1] && parseInt(file_node.id.split("#")[1])) {
                            ks_value = parseInt(file_node.id.split("#")[1]);
                        }
                        this.ks_unsaved_theme_global_data[file_node.name] = false;
                        this.ks_unsaved_theme_global_data[file_node.getAttribute("data-field-save")] = ks_value;
                        self.ks_dirty_data[file_node.name] = $(ev.currentTarget);
                        self.ks_dirty_data[file_node.getAttribute("data-field-save")] = $(ev.currentTarget);
                    } else {
                        // create background image data.
                        var file = file_node.files[0];
                        var field_name = ev.target.name;
                        utils.getDataURLFromFile(file).then(function(data) {
                            data = data.split(",")[1];
                            // Create url for file
                            var url = "data:image/" + (self.file_type_magic_word[data[0]] || "png") + ";base64," + data;
                            $("." + field_name + "_preview").prop("src", url);
                            // self.ks_unsaved_theme_global_data[field_name] = data;
                            if ($(ev.currentTarget).hasClass("ks_background_image")) {
                                ajax.jsonRpc("/ks_curved_backend_theme/add/images", "call", {
                                    image_info: {
                                        key: field_name,
                                        value: data
                                    },
                                    scope: "global",
                                }).then(function(res) {
                                    var ks_template_data = {};
                                    self._KsGetImageDict(field_name, ks_template_data);
                                    ks_template_data["ks_image_data"] = res;

                                    var ks_image_container = QWeb.render("ks_theme_image_template", ks_template_data);

                                    if (field_name == "ks_body_background_img") {
                                        $("div.ks_body_background_global_container").html(ks_image_container);
                                    }
                                    if (field_name == "ks_app_drawer_background_img") {
                                        $("div.ks_app_drawer_background_global_container").html(ks_image_container);
                                    }
                                    // function to reattach zoom functionality on image.
                                    self._ksAttachImageZoom();
                                });
                            }

                            if($(ev.currentTarget).hasClass("ks_login_background_image")){
                                ajax.jsonRpc("/ks_curved_backend_theme/add/login/images", "call", {
                                    image_info: {
                                        key: field_name,
                                        value: data
                                    }
                                }).then(function(res) {
                                    var ks_template_data = {};
                                    self._KsGetImageDict(field_name, ks_template_data);
                                    ks_template_data["ks_login_image"] = res;

                                    var ks_image_container = QWeb.render("ks_login_background_image_template", ks_template_data);

                                    if (field_name == "ks_login_background_image") {
                                        $("div.ks_login_background_img_container").html(ks_image_container);
                                    }
                                    // function to reattach zoom functionality on image.
                                    self._ksAttachImageZoom();
                                });
                            }
                            else {
                                $("." + field_name + "_preview").prop("src", url);
                                self.ks_unsaved_theme_global_data[field_name] = data;
                            }
                        });
                    }
                }
            } else {
                // Handle color theme input
                var ks_color_theme_fields = ["ks_body_background_global", "ks_menu_global", "ks_menu_hover_global", "ks_button_global", "ks_border_global", "ks_heading_global", "ks_link_global", "ks_primary_color_global", "ks_tooltip_global", ];

                if (ks_color_theme_fields.includes(ev.currentTarget.name)) {
                    this._ksApplyTempColorTheme(ev.currentTarget.name, ev.currentTarget.value);
                }
            }
        },

        _KsGetImageDict: function(field_name, ks_template_data) {
            if (field_name == "ks_body_background_img") {
                ks_template_data["ks_image_for"] = "ks_body_background_global";
                ks_template_data["ks_image_save"] = "ks_body_background_img";
                ks_template_data["ks_image_del"] = "ks_body_background_del_global";
                ks_template_data["ks_image_add"] = "ks_body_background_img_global";
            }

            if (field_name == "ks_app_drawer_background_img") {
                ks_template_data["ks_image_for"] = "ks_app_drawer_background_global";
                ks_template_data["ks_image_save"] = "ks_app_drawer_background_img";
                ks_template_data["ks_image_del"] = "ks_drawer_background_global_del";
                ks_template_data["ks_image_add"] = "ks_app_drawer_background_global";
            }
        },

        _ksApplyTempColorTheme: function(field_name, field_val) {
            var ks_color_field_dict = {
                ks_body_background_global: "--body-background",
                ks_menu_global: "--nav-link-color",
                ks_menu_hover_global: "--ks-over-link",
                ks_button_global: "--primary-btn",
                ks_border_global: "--tab-bg",
                ks_heading_global: "--heading-color",
                ks_link_global: "--link-color",
                ks_primary_color_global: "--primary",
                ks_tooltip_global: "--tooltip-heading-bg",
            };

            if (document.body.style.getPropertyValue(ks_color_field_dict[field_name])) {
                document.body.style.setProperty(ks_color_field_dict[field_name], field_val);
            }
        },

        _ksDecodeURLToString: function(URL) {
            return URL.split(",")[1];
        },

        _ksSaveGlobalData: function(ev) {
            var self = this;
            if (Object.keys(this.ks_unsaved_theme_global_data).length) {
                ajax.jsonRpc("/save/theme/settings", "call", {
                    ks_unsaved_setting: this.ks_unsaved_theme_global_data,
                    ks_origin_scope: "global",
                }).then(function() {
                    self.do_action("reload_context");
                });
            }
        },

        _ksDelBackgroundImage: function(ev) {
            var self = this;
            var ks_image_id = ev.currentTarget.getAttribute("data-id");
            ks_image_id = ks_image_id.split("#")[1];
            if (ev.target.classList.contains("ks_drawer_background_global_del")) {
                var ks_model = "ks.drawer.background";
            } else {
                var ks_model = "ks.body.background";
            }
            if (ks_image_id) {
                Dialog.confirm(this, _t("Are you sure you want to delete this record ?"), {
                    confirm_callback: function() {
                        return this._rpc({
                            model: ks_model,
                            method: "unlink",
                            args: [ks_image_id],
                        }).then(function() {
                            $(ev.currentTarget.parentElement.parentElement).remove();
                            // self.do_action("reload_context");
                        });
                    },
                });
            }
        },

        _ksDelLoginBackgroundImage: function(ev){
            var self = this;
            var ks_image_id = ev.currentTarget.getAttribute("data-id");
            ks_image_id = ks_image_id.split("#")[1];
            if (ks_image_id) {
                Dialog.confirm(this, _t("Are you sure you want to delete this record ?"), {
                    confirm_callback: function() {
                        return this._rpc({
                            model: "ks.login.background.image",
                            method: "unlink",
                            args: [ks_image_id],
                        }).then(function() {
                            $(ev.currentTarget.parentElement.parentElement).remove();
                            // self.do_action("reload_context");
                        });
                    },
                });
            }
        },

        _ksDelLoginBackgroundColor: function(ev){
            var self = this;
            var ks_color_id = ev.currentTarget.getAttribute("data-id");
            ks_color_id = ks_color_id.split("#")[1];
            debugger;
            if (ks_color_id) {
                Dialog.confirm(this, _t("Are you sure you want to delete this record ?"), {
                    confirm_callback: function() {
                        return this._rpc({
                            model: "ks.login.background.color",
                            method: "unlink",
                            args: [ks_color_id],
                        }).then(function() {
                            $(ev.currentTarget.parentElement.parentElement).remove();
                        });
                    },
                });
            }
        },

        _ksBackgroundDefault: function(ev) {
            var self = this;
            this._rpc({
                route: "/kstheme/background/default",
                params: {
                    ks_setting_scope: "Global",
                    ks_default_info: {
                        field: "ks_body_background",
                        model: "ks.body.background",
                    },
                },
            }).then(function() {
                self.do_action("reload_context");
            });
        },

        _ksDrawerDefault: function(ev) {
            var self = this;
            this._rpc({
                route: "/kstheme/background/default",
                params: {
                    ks_setting_scope: "Global",
                    ks_default_info: {
                        field: "ks_app_drawer_background",
                        model: "ks.drawer.background",
                    },
                },
            }).then(function() {
                self.do_action("reload_context");
            });
        },

        _ksSettingCancel: function() {
            this._ksResetValues();
            this._ksColorThemeCancel();
        },

        _ksResetValues: function() {
            var self = this;
            var ks_session = this.ks_theme_global_data;
            var ks_splitter = "_global";
            for (var index in this.ks_unsaved_theme_global_data) {
                let ks_index = index.split(ks_splitter)[0];
                // Ignore unsupported fields.
                if (!["ks_app_drawer_background_img", "ks_app_drawer_background_opacity", "ks_body_background_img", "ks_body_background_opacity", "ks_company_logo", "ks_login_background_image", "ks_small_company_logo", "ks_website_title", ].includes(ks_index)) {
                    if (typeof ks_session[ks_index] == "boolean") {
                        $(`input#${ks_index}${ks_splitter}`).prop("checked", ks_session[ks_index]);
                    } else if (!["ks_app_drawer_background", "ks_body_background"].includes(ks_index)) {
                        $(`input#${ks_session[ks_index]}${ks_splitter}`).prop("checked", true);
                    }
                } else if (["ks_body_background_img", "ks_app_drawer_background_img"].includes(index)) {
                    $(`p.${index}_global`).addClass("d-none");
                }
                delete this.ks_unsaved_theme_global_data[index];
            }
            // Reset background image and color for background and app drawer.
            ["ks_body_background_global", "ks_app_drawer_background_global", ].forEach((element)=>{
                $(`input[name=${element}]:checked`).prop("checked", false);
                $(`input[name=${element}][checked=checked]`).prop("checked", true);
            }
            );
            // function called to revert view changes  body background and color theme
            self._KsResetDirtyData(ks_session, ks_splitter);
        },
        _KsResetDirtyData: function(ks_session, ks_splitter) {
            var self = this;
            for (var index in self.ks_dirty_data) {
                if (index && self.ks_dirty_data[index] && (index.split(ks_splitter)[0]in ks_session) && self.ks_dirty_data[index].attr('type') == 'range') {
                    //Handled toggle button case
                    self.ks_dirty_data[index].val(ks_session[index.split(ks_splitter)[0]])
                } else if (index && self.ks_dirty_data[index] && (self.ks_dirty_data[index].data('field-save')in ks_session) && self.ks_dirty_data[index].data('field-save') && self.ks_dirty_data[index].hasClass('ks_radio_list')) {
                    //Handled color theme and body background case
                    var active_rec = [];
                    if (Array.isArray(ks_session[self.ks_dirty_data[index].data('field-save')])) {
                        var active_rec = ks_session[self.ks_dirty_data[index].data('field-save')].filter(x=>x.ks_active)
                    } else {
                        for (var key in ks_session[self.ks_dirty_data[index].data('field-save')]) {
                            active_rec = ks_session[self.ks_dirty_data[index].data('field-save')][key].filter(x=>x.ks_active);
                            if (active_rec && active_rec.length)
                                break;
                        }
                    }
                    if (active_rec && active_rec.length) {
                        $('input[name=' + self.ks_dirty_data[index].attr('name') + '][data-value="' + active_rec[0]['id'] + '"]').prop('checked', true);
                    } else {
                        $.each($('input[name=' + self.ks_dirty_data[index].attr('name') + ']'), function(e) {
                            $(this).prop('checked', false);
                        });
                    }
                }else if (index && self.ks_dirty_data[index] && (self.ks_dirty_data[index].data('field-save')in ks_session) && self.ks_dirty_data[index].data('field-save') && self.ks_dirty_data[index].hasClass('ks_cancel_radio')) {
                    $('input[name=' + self.ks_dirty_data[index].attr('name') + '][data-value="' + ks_session[self.ks_dirty_data[index].data('field-save')] + '"]').prop('checked', true);
                }
            }
            self.ks_dirty_data = {}

        },

        _ksColorThemeEdit: function(ev) {
            var self = this;
            var ks_theme_id = parseInt($(ev.currentTarget).attr("data-theme-id"));
            $("div.ks_theme_selected").removeClass("ks_theme_selected");
            $(ev.currentTarget.parentElement.parentElement).addClass("ks_theme_selected");
            this._rpc({
                model: "ks.color.theme",
                method: "search_read",
                kwargs: {
                    domain: [["id", "=", ks_theme_id]],
                    fields: [],
                },
            }).then(function(arg) {
                if (arg[0].ks_template_id.length) {
                    arg[0].id = false;
                }
                var ks_edit_section = QWeb.render("ks_theme_edit_section_global", {
                    ks_theme_data: arg[0],
                });
                $("div#global_theme_edit_section").html(ks_edit_section);
                self._scrollToDown();
            });
        },

        _scrollToDown: function() {
            // Scroll down div
            $("div.ks_color_theme_qweb_div_global").scrollTop($("div.ks_color_theme_qweb_div_global")[0].scrollHeight);
        },

        _ksCustomColorThemeAdd: function() {
            var self = this;
            var ks_edit_section = QWeb.render("ks_theme_edit_section_global", {
                ks_theme_data: {},
            });
            $("div#global_theme_edit_section").html(ks_edit_section);
            self._scrollToDown();
        },

        _ksColorThemeCancel: function() {
            $("div#global_theme_edit_section").html("");
            $("div.ks_theme_selected").removeClass("ks_theme_selected");
            this._ksResetColorTheme();
        },

        _ksResetColorTheme() {
            var ks_color_field_dict = {
                ks_body_background: "body-background",
                ks_menu: "nav-link-color",
                ks_menu_hover: "ks-over-link",
                ks_button: "primary-btn",
                ks_border: "tab-bg",
                ks_heading: "heading-color",
                ks_link: "link-color",
                ks_primary_color: "primary",
                ks_tooltip: "tooltip-heading-bg",
            };
            _.each(ks_color_field_dict, (value,key)=>{
                if (document.body.style.getPropertyValue("--" + value)) {
                    document.body.style.setProperty("--" + value, session.ks_color_theme[value]);
                }
            }
            );
        },

        _ksColorThemeSave: function() {
            var self = this;
            var ks_theme_data = this._ks_get_theme_data_dict();
            ks_theme_data["ks_global"] = true;
            this._rpc({
                model: "ks.color.theme",
                method: "create",
                args: [ks_theme_data],
            }).then(function(create_id) {
                self._rpc({
                    model: "ks.color.theme",
                    method: "search_read",
                    kwargs: {
                        domain: [["id", "=", create_id]],
                        fields: [],
                    },
                }).then(function(arg) {
                    self.ks_theme_global_data.ks_color_theme.custom.push(arg[0]);
                    var color_theme_temp = QWeb.render("ks_color_theme_qweb_template_global", {
                        widget: self,
                    });
                    $("div.ks_color_theme_qweb_div_global").html(color_theme_temp);
                });
            });
        },

        _ks_get_theme_data_dict: function() {
            var ks_data = {};
            this.ks_global_theme_fields.forEach((ks_element)=>{
                ks_data[ks_element] = $(`input#${ks_element}_global`).val();
            }
            );
            return ks_data;
        },

        _ksColorThemeUpdate: function(ev) {
            var self = this;
            var ks_theme_data = this._ks_get_theme_data_dict();
            var ks_theme_id = parseInt($(ev.currentTarget).attr("data-theme-id"));
            this._rpc({
                model: "ks.color.theme",
                method: "write",
                args: [[ks_theme_id], ks_theme_data],
            }).then(function(arg) {
                self._rpc({
                    model: "ks.color.theme",
                    method: "search_read",
                    kwargs: {
                        domain: [["id", "=", ks_theme_id]],
                        fields: [],
                    },
                }).then(function(arg) {
                    self._updateThemeData(arg[0]);
                    var color_theme_temp = QWeb.render("ks_color_theme_qweb_template_global", {
                        widget: self,
                    });
                    $("div.ks_color_theme_qweb_div_global").html(color_theme_temp);
                });
            });
        },

        _updateThemeData: function(updated_data) {
            var ks_updated_data = _.map(this.ks_theme_global_data.ks_color_theme.custom, function(theme) {
                if (theme.id == updated_data.id)
                    return updated_data;
                else
                    return theme;
            });
            this.ks_theme_global_data.ks_color_theme.custom = ks_updated_data;
        },

        _ksColorThemeDelete: function(ev) {
            var self = this;
            var ks_theme_id = parseInt($(ev.currentTarget).attr("data-theme-id"));
            $("div.ks_theme_selected").removeClass("ks_theme_selected");
            $(ev.currentTarget.parentElement.parentElement).addClass("ks_theme_selected");
            if (ks_theme_id) {
                Dialog.confirm(this, _t("Are you sure you want to delete this record ?"), {
                    confirm_callback: function() {
                        return this._rpc({
                            model: "ks.color.theme",
                            method: "unlink",
                            args: [ks_theme_id],
                        }).then(function() {
                            self._ksRemoveTheme(ks_theme_id);
                            var color_theme_temp = QWeb.render("ks_color_theme_qweb_template_global", {
                                widget: self,
                            });
                            $("div.ks_color_theme_qweb_div_global").html(color_theme_temp);
                        });
                    },
                    cancel_callback: ()=>{
                        $("div.ks_theme_selected").removeClass("ks_theme_selected");
                    }
                    ,
                });
            }
        },

        _ksRemoveTheme: function(ks_theme_id) {
            var result = false;
            var ks_custom_themes = _.filter(this.ks_theme_global_data.ks_color_theme.custom, function(theme) {
                return ks_theme_id != theme.id;
            });
            this.ks_theme_global_data.ks_color_theme.custom = ks_custom_themes;
            return result;
        },

        on_detach_callback: function() {
            this._ksColorThemeCancel();
        },

        _ksLoginPageBgColor: function(){
            var ks_selected_color = $('#ks_login_bg_color_add').val();
            ajax.jsonRpc("/ks_curved_backend_theme/add/login/color", "call", {
                data: {
                   value: ks_selected_color
                },
            }).then(function(res) {
                var ks_template_data = {};
                ks_template_data["ks_login_colors"] = res;
                var ks_color_container = QWeb.render("ks_login_background_color_template", ks_template_data);
                $("div.ks_login_background_color_container").html(ks_color_container);
            });
        },
    });

    widgetRegistry.add("ks_global_config_widget", KsGlobalConfigWidget);

    return KsGlobalConfigWidget;
});
