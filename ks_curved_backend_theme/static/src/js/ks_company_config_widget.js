odoo.define("ks_curved_backend_theme.ks_company_config_widget", function(require) {
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

    var KsCompanyConfigWidget = Widget.extend({
        template: "ks_company_settings",

        file_type_magic_word: {
            "/": "jpg",
            R: "gif",
            i: "png",
            P: "svg+xml",
        },

        events: {
            //            'change input': '_onInputChange',
            "change input": "_onInputChange",
            "click button.ks_setting_company_save": "_ksSettingSave",
            "click .ks_body_background_del_company, .ks_drawer_background_company_del": "_ksDelBackgroundImage",
            "click .ks_background_default_company": "_ksBackgroundDefault",
            "click .ks_drawer_background_default_company": "_ksDrawerDefault",
            "click button.ks_setting_cancel_company": "_ksSettingCancel",
            "click .ks_company_theme_edit": "_ksColorThemeEdit",
            "click button#ks_add_custom_theme_company": "_ksCustomColorThemeAdd",
            "click .ks_theme_edit_cancel": "_ksColorThemeCancel",
            "click .ks_new_theme_save": "_ksColorThemeSave",
            "click .ks_theme_edit_update": "_ksColorThemeUpdate",
            "click .ks_company_theme_delete": "_ksColorThemeDelete",
            "click .ks_company_reset_color_theme": "_ksColorThemeResetToDefault",
        },
        // Todo: Take reference from Ribbon widget
        init: function(parent, data, options) {
            this.ks_form_id = parent.state.data.id;
            this.ks_unsaved_setting = {};
            this.ks_dirty_data = {};
            this.ks_company_theme_fields = ["ks_body_background", "ks_menu", "ks_menu_hover", "ks_button", "ks_border", "ks_heading", "ks_link", "ks_primary_color", "ks_tooltip", ];
            this._super.apply(this, arguments);
        },

        /**
       * @override
       **/
        willStart: async function() {
            const _super = this._super.bind(this);
            const data = await this._rpc({
                route: "/render/theme/view/data",
                params: {
                    ks_setting_scope: "Company",
                    ks_rec_id: this.ks_form_id
                },
            });
            this.data = data;
            return _super(...arguments);
        },

        /**
       * @override
       */
        start: function() {
            var ks_self = this;
            return this._super.apply(this, arguments);
        },

        on_attach_callback: function() {
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
            this.ks_unsaved_setting = {};
            var default_color_theme = this.data.ks_color_theme.filter(x=>x.ks_default);
            if (default_color_theme.length) {
                this.ks_unsaved_setting['ks_theme_color'] = default_color_theme[0]['id'];
                this._ksSettingSave();
            }
        },

        _render: function() {
            this._super.apply(this, arguments);
            var ks_self = this;
        },

        //        _onInputChange: function(ev) {
        //            var self = this;
        //            var self = this;
        //            if (ev.target.name) {
        //                if (ev.target.type == 'checkbox') {
        //                    var _value = ev.target.checked;
        //                    var _field = ev.target.name;
        //                } else if (ev.target.type == 'radio') {
        //                    if (ev.target.attributes['data-value']) {
        //                        var _value = ev.target.attributes['data-value'].value;
        //                        var _field = ev.target.name;
        //                    } else
        //                        return;
        //                }
        //                this.ks_unsaved_setting[_field] = _value;
        //            }
        //        },

        _onInputChange: function(ev) {
            var self = this;
            if (ev.currentTarget.name && !$(ev.currentTarget).hasClass("ks_binary_field")) {
                if (ev.currentTarget.dataset.type == "field-boolean") {
                    this.ks_unsaved_setting[ev.currentTarget.name] = ev.currentTarget.checked;
                    self.ks_dirty_data[ev.currentTarget.name] = $(ev.currentTarget);
                } else {
                    if ($(ev.currentTarget).attr("class").includes("slider")) {
                        $(ev.currentTarget).siblings(".ks_opacity_value_max").html(ev.currentTarget.value);
                        this.ks_unsaved_setting[ev.currentTarget.name] = ev.currentTarget.value;
                        self.ks_dirty_data[ev.currentTarget.name] = $(ev.currentTarget);
                    } else {
                        this.ks_unsaved_setting[ev.currentTarget.name] = ev.currentTarget.dataset.value ? ev.currentTarget.dataset.value : ev.currentTarget.checked;
                        self.ks_dirty_data[ev.currentTarget.name] = $(ev.currentTarget);
                    }
                }
            } else if (ev.currentTarget.name && !$(ev.currentTarget).hasClass("ks_binary_field")) {
                delete this.ks_unsaved_setting[ev.currentTarget.name];
            }

            // Manage data for text fields.
            if (ev.currentTarget.name && ev.currentTarget.dataset.type == "ks-char") {
                this.ks_unsaved_setting[ev.currentTarget.name] = ev.currentTarget.value;
                self.ks_dirty_data[ev.currentTarget.name] = $(ev.currentTarget);
            }

            // Handle binary field fields.
            if ($(ev.currentTarget).hasClass("ks_binary_field")) {
                var file_node = ev.target;
                // Handle body background input change.
                // set active saved image.
                if (file_node.getAttribute("data-model")) {
                    var ks_img_src = $(file_node.nextElementSibling).find("img").attr("src");
                    var ks_value = self._ksDecodeURLToString(ks_img_src);
                    if (file_node.id.split("#")[1] && parseInt(file_node.id.split("#")[1])) {
                        ks_value = parseInt(file_node.id.split("#")[1]);
                    }
                    this.ks_unsaved_setting[file_node.name] = false;
                    this.ks_unsaved_setting[file_node.getAttribute("data-field-save")] = ks_value;
                    self.ks_dirty_data[file_node.name] = $(ev.currentTarget);
                    self.ks_dirty_data[file_node.getAttribute("data-field-save")] = $(ev.currentTarget);
                } else {
                    // add new image.
                    var file = file_node.files[0];
                    var field_name = ev.target.name;
                    utils.getDataURLFromFile(file).then(function(data) {
                        data = data.split(",")[1];
                        // Create url for file
                        var url = "data:image/" + (self.file_type_magic_word[data[0]] || "png") + ";base64," + data;
                        $("." + field_name + "_preview").prop("src", url);
                        // self.ks_unsaved_setting[field_name] = data;
                        if ($(ev.currentTarget).hasClass("ks_background_image")) {
                            ajax.jsonRpc("/ks_curved_backend_theme/add/images", "call", {
                                image_info: {
                                    key: field_name,
                                    value: data
                                },
                                scope: "company",
                                company_id: self.ks_form_id,
                            }).then(function(res) {
                                var ks_template_data = {};
                                self._KsGetImageDict(field_name, ks_template_data);
                                ks_template_data["ks_image_data"] = res;

                                var ks_image_container = QWeb.render("ks_theme_image_template", ks_template_data);

                                if (field_name == "ks_body_background_img") {
                                    $("div.ks_body_background_company_container").html(ks_image_container);
                                }
                                if (field_name == "ks_app_drawer_background_img") {
                                    $("div.ks_app_drawer_background_company_container").html(ks_image_container);
                                }
                                // function to reattach zoom functionality on image.
                                self.on_attach_callback();
                            });
                        } else{
                            $("." + field_name + "_preview").prop("src", url);
                            self.ks_unsaved_setting[field_name] = data;
                        }
                        // $(ev.currentTarget)
                        //   .parents(".ks-quick-card")
                        //   .find(".ks_bck_img")
                        //   .removeClass("d-none");
                    });
                }
            }
        },

        _KsGetImageDict: function(field_name, ks_template_data) {
            if (field_name == "ks_body_background_img") {
                ks_template_data["ks_image_for"] = "ks_body_background_company";
                ks_template_data["ks_image_save"] = "ks_body_background_img";
                ks_template_data["ks_image_del"] = "ks_body_background_del_company";
                ks_template_data["ks_image_add"] = "ks_body_background_company";
            }

            if (field_name == "ks_app_drawer_background_img") {
                ks_template_data["ks_image_for"] = "ks_app_drawer_background_company";
                ks_template_data["ks_image_save"] = "ks_app_drawer_background_img";
                ks_template_data["ks_image_del"] = "ks_drawer_background_company_del";
                ks_template_data["ks_image_add"] = "ks_app_drawer_background_company";
            }
        },

        _ksApplyTempColorTheme: function(field_name, field_val) {
            var ks_color_field_dict = {
                ks_body_background_company: "--body-background",
                ks_menu_company: "--nav-link-color",
                ks_menu_hover_company: "--ks-over-link",
                ks_button_company: "--primary-btn",
                ks_border_company: "--tab-bg",
                ks_heading_company: "--heading-color",
                ks_link_company: "--link-color",
                ks_primary_color_company: "--primary",
                ks_tooltip_company: "--tooltip-heading-bg",
            };

            if (document.body.style.getPropertyValue(ks_color_field_dict[field_name])) {
                document.body.style.setProperty(ks_color_field_dict[field_name], field_val);
            }
        },

        _ksDecodeURLToString: function(URL) {
            return URL.split(",")[1];
        },

        _ksSettingSave: function(ev) {
            var self = this;
            if (Object.keys(this.ks_unsaved_setting).length) {
                ajax.jsonRpc("/save/theme/settings", "call", {
                    ks_unsaved_setting: self.ks_unsaved_setting,
                    ks_origin_scope: "company",
                    record_id: this.ks_form_id,
                }).then(function() {
                    self.do_action("reload_context");
                });
            }
        },

        _ksDelBackgroundImage: function(ev) {
            var self = this;
            var ks_image_id = ev.currentTarget.getAttribute("data-id");
            ks_image_id = ks_image_id.split("#")[1];
            if (ev.target.classList.contains("ks_drawer_background_company_del")) {
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
                    ks_setting_scope: "Company",
                    ks_rec_id: this.ks_form_id,
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
                    ks_setting_scope: "Company",
                    ks_rec_id: this.ks_form_id,
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
            var self = this;
            var ks_session = this.data;
            var ks_splitter = "_company";
            for (var index in this.ks_unsaved_setting) {
                let ks_index = index.split(ks_splitter)[0];
                if (index == "ks_company_logo_enable_company") {
                    ks_index = "ks_company_logo_enable";
                }
                // Ignore unsupported fields.
                if (!["ks_app_drawer_background_img", "ks_app_drawer_background_opacity", "ks_body_background_img", "ks_body_background_opacity", "ks_company_logo", "ks_login_background_image", "ks_small_company_logo", "ks_website_title", "ks_app_drawer_background", "ks_body_background", "ks_company_logo", ].includes(ks_index)) {
                    if (typeof ks_session[ks_index] == "boolean") {
                        $(`input#${ks_index}${ks_splitter}`).prop("checked", ks_session[ks_index]);
                    } else {
                        $(`input#${ks_session[ks_index]}${ks_splitter}`).prop("checked", true);
                    }
                } else if (["ks_body_background_img", "ks_app_drawer_background_img"].includes(index)) {
                    $(`p.${index}_company`).addClass("d-none");
                }
                delete this.ks_unsaved_setting[index];
            }
            // Reset background image and color for background and app drawer.
            ["ks_body_background_company", "ks_app_drawer_background_company", ].forEach((element)=>{
                $(`input[name=${element}]:checked`).prop("checked", false);
                $(`input[name=${element}][checked=checked]`).prop("checked", true);
            }
            );
            // function called to revert view changes on app drawer body background and color theme
            this._KsResetDirtyData(ks_session, ks_splitter)
            this._ksColorThemeCancel();
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
                } else if(index && self.ks_dirty_data[index].data('field-save') && self.ks_dirty_data[index] && (self.ks_dirty_data[index].data('field-save')in ks_session && self.ks_dirty_data[index].hasClass('ks_cancel_radio'))){
                    $('input[name=' + self.ks_dirty_data[index].attr('name') + '][data-value="' + ks_session[self.ks_dirty_data[index].data('field-save')] + '"]').prop('checked', true);
                }
            }
            self.ks_dirty_data = {}
        },

        _ksColorThemeEdit: function(ev) {
            var self = this;
            var ks_theme_id = parseInt($(ev.currentTarget).attr("data-theme-id"));
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
                var ks_edit_section = QWeb.render("ks_theme_edit_section_company", {
                    ks_theme_data: arg[0],
                });
                $("div#company_theme_edit_section").html(ks_edit_section);
                self._scrollToDown();
            });
        },

        _scrollToDown: function() {
            // Scroll down div
            $("div.ks_color_theme_qweb_div_company").scrollTop($("div.ks_color_theme_qweb_div_company")[0].scrollHeight);
        },

        _ksCustomColorThemeAdd: function() {
            var self = this;
            var ks_edit_section = QWeb.render("ks_theme_edit_section_company", {
                ks_theme_data: {},
            });
            $("div#company_theme_edit_section").html(ks_edit_section);
            self._scrollToDown();
        },

        _ksColorThemeCancel: function() {
            $("div#company_theme_edit_section").html("");
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

        _ks_get_theme_data_dict: function() {
            var ks_data = {};
            this.ks_company_theme_fields.forEach((ks_element)=>{
                ks_data[ks_element] = $(`input#${ks_element}_company`).val();
            }
            );
            return ks_data;
        },

        _ksColorThemeSave: function() {
            var self = this;
            var ks_theme_data = this._ks_get_theme_data_dict();
            ks_theme_data["ks_company"] = self.ks_form_id;
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
                    self.data.ks_color_theme.custom.push(arg[0]);
                    var color_theme_temp = QWeb.render("ks_color_theme_qweb_template_company", {
                        widget: self,
                    });
                    $("div.ks_color_theme_qweb_div_company").html(color_theme_temp);
                });
            });
        },

        _ksColorThemeDelete: function(ev) {
            var self = this;
            var ks_theme_id = parseInt($(ev.currentTarget).attr("data-theme-id"));
            if (ks_theme_id) {
                Dialog.confirm(this, _t("Are you sure you want to delete this record ?"), {
                    confirm_callback: function() {
                        return this._rpc({
                            model: "ks.color.theme",
                            method: "unlink",
                            args: [ks_theme_id],
                        }).then(function() {
                            self._ksRemoveTheme(ks_theme_id);
                            var color_theme_temp = QWeb.render("ks_color_theme_qweb_template_company", {
                                widget: self,
                            });
                            $("div.ks_color_theme_qweb_div_company").html(color_theme_temp);
                        });
                    },
                });
            }
        },

        _ksRemoveTheme: function(ks_theme_id) {
            var result = false;
            var ks_custom_themes = _.filter(this.data.ks_color_theme.custom, function(theme) {
                return ks_theme_id != theme.id;
            });
            this.data.ks_color_theme.custom = ks_custom_themes;
            return result;
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
                    var color_theme_temp = QWeb.render("ks_color_theme_qweb_template_company", {
                        widget: self,
                    });
                    $("div.ks_color_theme_qweb_div_company").html(color_theme_temp);
                });
            });
        },

        _updateThemeData: function(updated_data) {
            var ks_updated_data = _.map(this.data.ks_color_theme.custom, function(theme) {
                if (theme.id == updated_data.id)
                    return updated_data;
                else
                    return theme;
            });
            this.data.ks_color_theme.custom = ks_updated_data;
        },

        on_detach_callback: function() {
            this._ksColorThemeCancel();
        },
    });

    widgetRegistry.add("ks_company_config_widget", KsCompanyConfigWidget);

    return KsCompanyConfigWidget;
});
