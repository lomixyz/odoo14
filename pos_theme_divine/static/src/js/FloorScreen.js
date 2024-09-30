/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_redesign.PosResFloorScreen', function (require) {
    "use strict";  

    const FloorScreen = require('pos_restaurant.FloorScreen');
    const Registries = require('point_of_sale.Registries');
    var core = require('web.core');
    var _t = core._t;

    const PosResFloorScreen = (FloorScreen) =>
        class extends FloorScreen {
            constructor() {
                super(...arguments);
                setTimeout(function(){
                    if($(".floor-screen.screen").is(":visible")){
                        $(".pos-drawer ").hide()
                        $(".subwindow-container div").addClass("subwindow-container-fix-floors")
                        $(".subwindow-container div").removeClass("pos-subwindow-container-fix-dwr-expanded")
                        $(".order-selector").hide();
                        $(".table-seats").hide();
                        $(".table-seats-theme").show();
                    }
                },100);
            }
            mounted(){
                super.mounted();
                if($(".floor-screen.screen").is(":visible")){
                    $(".pos-drawer ").hide()
                    $(".subwindow-container div").addClass("subwindow-container-fix-floors")
                    $(".subwindow-container div").removeClass("pos-subwindow-container-fix-dwr-expanded")
                    $(".order-selector").hide();
                    $(".table-seats").hide();
                    $(".table-seats-theme").show();
                }
            }
            willUnmount() {
                clearInterval(this.tableLongpolling);
                $(".pos-drawer ").show()
                $(".subwindow-container div").removeClass("subwindow-container-fix-floors")
                $(".subwindow-container-fix-theme").addClass("pos-subwindow-container-fix-dwr-expanded")
                $(".order-selector").show()
            }
            table_style_background(){
                var table = this.table;
                function unit(val){ return '' + val + 'px'; }
                var style = {
                    'width':        unit(table.width*1.47 -1),
                    'height':       unit(table.height*1.8),
                    'line-height':  unit(table.height),
                    'margin-left':  unit(-(table.width*1.5)/2),
                    'margin-top':   unit(-(table.height*1.5)/2),
                    'top':          unit(table.position_v + table.height/2),
                    'left':         unit(table.position_h + table.width/2),
                    'border-radius': table.shape === 'round' ? unit(Math.max(table.width,table.height)/2) : '3px',
                    'box-shadow': 'none',
                    'transition': 'none',
                    'overflow': 'inherit',
                    'box-shadow': '0px 0px 8px rgba(0, 0, 0, 0.1)',
                    'border-radius': '30px',
                    'border': '1px solid gray',
                };
                if(table.shape === 'round'){
                    style = {
                        'width':        unit(table.width*1.38),
                        'height':       unit(table.height*1.5),
                        'line-height':  unit(table.height),
                        'margin-left':  unit(-(table.width*1.5)/2),
                        'margin-top':   unit(-(table.height*1.5)/2),
                        'top':          unit(table.position_v + table.height/1.5),
                        'left':         unit(table.position_h + table.width/1.8),
                        'border-radius': table.shape === 'round' ? unit(Math.max(table.width,table.height)/2) : '3px',
                        'box-shadow': 'none',
                        'transition': 'none',
                        'overflow': 'inherit',
                        'border': '1px solid gray',
                    }
                }
                if (table.color) {
                    style.background = "white";
                }
                if (table.height >= 150 && table.width >= 150) {
                    style['font-size'] = '32px';
                }
                return style;
            }
            get table_background(){
                var style = this.table_style_background();
                var str = "";
                var s;
                for (s in style) {
                    str += s + ":" + style[s] + "; ";
                }
                return str;
            }
            get style_chair(){
                var style = { 'stroke': this.table.color, }
                var str = "";
                var s;
                for (s in style) {
                    str += s + ":" + style[s] + "; ";
                }
                return str;
            }
            table_style_topleft(){
                var table = this.table;
                function unit(val){ return '' + val + 'px'; }
                var style = {
                    'width':        unit(((table.width)/2)),
                    'height':       unit(((table.height)/2)),
                    'line-height':  unit(table.height),
                    'margin-left':  unit((-table.width/2)*2),
                    'margin-top':   unit((-table.height/2)*2),
                    'top':          unit(table.position_v + table.height/1.8),
                    'left':         unit(table.position_h + table.width/1.4),
                    'border-radius': table.shape === 'round' ? unit(Math.max(table.width,table.height)/2) : '3px',
                    'box-shadow': 'none',
                    'transition': 'none',
                    'overflow': 'inherit',
                };
                if(table.shape === 'round'){
                    style = {
                        'width':        unit(((table.width)/2)),
                        'height':       unit(((table.height)/2)),
                        'line-height':  unit(table.height),
                        'margin-left':  unit((-table.width/2)*1.82),
                        'margin-top':   unit((-table.height/2)*1.82),
                        'top':          unit(table.position_v + table.height/1.8),
                        'left':         unit(table.position_h + table.width/1.4),
                        'border-radius': table.shape === 'round' ? unit(Math.max(table.width,table.height)/2) : '3px',
                        'box-shadow': 'none',
                        'transition': 'none',
                        'overflow': 'inherit',
                    }
                }
                if (table.color) {
                    style.background = "none";
                }
                if (table.height >= 150 && table.width >= 150) {
                    style['font-size'] = '32px';
                }
                return style;
            }
            get table_style_str_topleft(){
                var style = this.table_style_topleft();
                var str = "";
                var s;
                for (s in style) {
                    str += s + ":" + style[s] + "; ";
                }
                return str;
            }
            table_style_topright(){
                var table = this.table;
                function unit(val){ return '' + val + 'px'; }
                var style = {
                    'width':        unit(((table.width)/2)),
                    'height':       unit(((table.height)/2)),
                    'line-height':  unit(table.height),
                    'margin-left':  unit((-table.width/2)*-0.1),
                    'margin-top':   unit((-table.height/2)*2),
                    'top':          unit(table.position_v + table.height/1.8),
                    'left':         unit(table.position_h + table.width/1.4),
                    'border-radius': table.shape === 'round' ? unit(Math.max(table.width,table.height)/2) : '3px',
                    'box-shadow': 'none',
                    'transition': 'none',
                    'overflow': 'inherit',
                };
                if(table.shape === 'round'){
                    style = {
                        'width':        unit(((table.width)/2)),
                        'height':       unit(((table.height)/2)),
                        'line-height':  unit(table.height),
                        'margin-left':  unit((-table.width)*0.12),
                        'margin-top':   unit((-table.height/2)*1.9),
                        'top':          unit(table.position_v + table.height/1.6),
                        'left':         unit(table.position_h + table.width/1.2),
                        'border-radius': table.shape === 'round' ? unit(Math.max(table.width,table.height)/2) : '3px',
                        'box-shadow': 'none',
                        'transition': 'none',
                        'overflow': 'inherit',
                    }
                }
                if (table.color) {
                    style.background = "none";
                }
                if (table.height >= 150 && table.width >= 150) {
                    style['font-size'] = '32px';
                }
    
                return style;
            }
            get table_style_str_topright(){
                var style = this.table_style_topright();
                var str = "";
                var s;
                for (s in style) {
                    str += s + ":" + style[s] + "; ";
                }
                return str;
            }
            table_style_bottomright(){
                var table = this.table;
                function unit(val){ return '' + val + 'px'; }
                var style = {
                    'width':        unit(((table.width)/2)),
                    'height':       unit(((table.height)/2)),
                    'line-height':  unit(table.height),
                    'margin-left':  unit((-table.width/2)*-0.1),
                    'margin-top':   unit((-table.height/2)*-0.1),
                    'top':          unit(table.position_v + table.height/1.9),
                    'left':         unit(table.position_h + table.width/1.4),
                    'border-radius': table.shape === 'round' ? unit(Math.max(table.width,table.height)/2) : '3px',
                    'box-shadow': 'none',
                    'transition': 'none',
                    'overflow': 'inherit',
                };
                if(table.shape === 'round'){
                    style = {
                        'width':        unit(((table.width)/2)),
                        'height':       unit(((table.height)/2)),
                        'line-height':  unit(table.height),
                        'margin-left':  unit((-table.width)*-0.1),
                        'margin-top':   unit((-table.height/2)*-0.1),
                        'top':          unit(table.position_v + table.height/2.8),
                        'left':         unit(table.position_h + table.width/1.65),
                        'border-radius': table.shape === 'round' ? unit(Math.max(table.width,table.height)/2) : '3px',
                        'box-shadow': 'none',
                        'transition': 'none',
                        'overflow': 'inherit',
                    }
                }
                if (table.color) {
                    style.background = "none";
                }
                if (table.height >= 150 && table.width >= 150) {
                    style['font-size'] = '32px';
                }
    
                return style;
            }
            get table_style_str_bottomright(){
                var style = this.table_style_bottomright();
                var str = "";
                var s;
                for (s in style) {
                    str += s + ":" + style[s] + "; ";
                }
                return str;
            }
            table_style_bottomleft(){
                var table = this.table;
                function unit(val){ return '' + val + 'px'; }
                var style = {
                    'width':        unit(((table.width)/2)),
                    'height':       unit(((table.height)/2)),
                    'line-height':  unit(table.height),
                    'margin-left':  unit((-table.width/2)*2),
                    'margin-top':   unit((-table.height/2)*-0.1),
                    'top':          unit(table.position_v + table.height/1.9),
                    'left':         unit(table.position_h + table.width/1.4),
                    'border-radius': table.shape === 'round' ? unit(Math.max(table.width,table.height)/2) : '3px',
                    'box-shadow': 'none',
                    'transition': 'none',
                    'overflow': 'inherit',
                };
                if(table.shape === 'round'){
                    style = {
                        'width':        unit(((table.width)/2)),
                        'height':       unit(((table.height)/2)),
                        'line-height':  unit(table.height),
                        'margin-left':  unit((-table.width/2)*1.8),
                        'margin-top':   unit((-table.height/2)*-0.1),
                        'top':          unit(table.position_v + table.height/2.8),
                        'left':         unit(table.position_h + table.width/1.4),
                        'border-radius': table.shape === 'round' ? unit(Math.max(table.width,table.height)/2) : '3px',
                        'box-shadow': 'none',
                        'transition': 'none',
                        'overflow': 'inherit',
                    }
                }
                if (table.color) {
                    style.background = "none";
                }
                if (table.height >= 150 && table.width >= 150) {
                    style['font-size'] = '32px';
                }
    
                return style;
            }
            get table_style_str_bottonleft(){
                var style = this.table_style_bottomleft();
                var str = "";
                var s;
                for (s in style) {
                    str += s + ":" + style[s] + "; ";
                }
                return str;
            }
        };

    Registries.Component.extend(FloorScreen, PosResFloorScreen);

    return FloorScreen;
});

