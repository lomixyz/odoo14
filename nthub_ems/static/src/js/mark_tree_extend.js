///** @odoo-module */
//import { ListController } from "@web/views/list/list_controller";
//import { registry } from '@web/core/registry';
//import { listView } from '@web/views/list/list_view';
//
//export class MarkListController extends ListController {
//   setup() {
//       super.setup();
//   }
//   OnTestClick() {
//       this.actionService.doAction({
//          type: 'ir.actions.act_window',
//          res_model: 'multiple.marks',
//          name:'Generate Subject',
//          view_mode: 'form',
//          view_type: 'form',
//          views: [[false, 'form']],
//          target: 'new',
//          res_id: false,
//      });
//   }
//}
//registry.category("views").add("button_in_tree", {
//   ...listView,
//   Controller: MarkListController,
//   buttonTemplate: "button_mark.ListView.Buttons",
//});


/** @odoo-module */
var ListController = require("@web/views/list/list_controller").ListController;
var registry = require('@web/core/registry').registry;
var listView = require('@web/views/list/list_view').listView;

function MarkListController() {
    ListController.apply(this, arguments);
}

MarkListController.prototype = Object.create(ListController.prototype);
MarkListController.prototype.constructor = MarkListController;

MarkListController.prototype.setup = function () {
    ListController.prototype.setup.call(this);
};

MarkListController.prototype.OnTestClick = function () {
    this.actionService.doAction({
        type: 'ir.actions.act_window',
        res_model: 'multiple.marks',
        name: 'Generate Subject',
        view_mode: 'form',
        view_type: 'form',
        views: [[false, 'form']],
        target: 'new',
        res_id: false,
    });
};

registry.category("views").add("button_in_tree", {
    Controller: MarkListController,
    buttonTemplate: "button_mark.ListView.Buttons",
});






