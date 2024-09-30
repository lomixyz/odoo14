/*  Copyright 2016-2017 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
    License MIT (https://opensource.org/licenses/MIT). */
// odoo.define("web_debranding.bot", function(require) {
//     "use strict";

//     require("web_debranding.dialog");
//     var Message = require("mail.model.Message");
//     var session = require("web.session");
//     var MailBotService = require("mail_bot.MailBotService");
//     var core = require("web.core");
//     var _t = core._t;

//     Message.include({
//         _getAuthorName: function() {
//             if (this._isOdoobotAuthor()) {
//                 return "Bot";
//             }
//             return this._super.apply(this, arguments);
//         },
//         getAvatarSource: function() {
//             if (this._isOdoobotAuthor()) {
//                 return "/web/binary/company_logo?company_id=" + session.company_id;
//             }
//             return this._super.apply(this, arguments);
//         },
//     });

//     MailBotService.include({
//         getPreviews: function(filter) {
//             var previews = this._super.apply(this, arguments);
//             previews.map(function(preview) {
//                 if (preview.title === _t("OdooBot has a request")) {
//                     preview.title = _t("Bot has a request");
//                 }
//                 if (preview.imageSRC === "/mail/static/src/img/odoobot.png") {
//                     preview.imageSRC =
//                         "/web/binary/company_logo?company_id=" + session.company_id;
//                 }
//                 return preview;
//             });
//             return previews;
//         },
//     });
// });
odoo.define('web_debranding.bot', function(require) {
    "use strict";
console.log("abuzar")
    const Registry = require('web.Registry');
    const Message = require('mail/static/src/components/message/message.js');
    const ExtendedMessage = (Message) =>
        class extends Message {
            get avatar()  {
                console.log("message%%%%%%%%%")
                if (this.message.author && this.message.author === this.env.messaging.partnerRoot) {
                return "/web/binary/company_logo?company_id=" + session.company_id;
            } else if (this.message.author) {
                // TODO FIXME for public user this might not be accessible. task-2223236
                // we should probably use the correspondig attachment id + access token
                // or create a dedicated route to get message image, checking the access right of the message
                return this.message.author.avatarUrl;
            } else if (this.message.message_type === 'email') {
                return '/mail/static/src/img/email_icon.png';
            }
            return '/mail/static/src/img/smiley/avatar.jpg'; 
                // super.sleep(...arguments); 
            }
        }
    // Registry.Component.extend(Message, ExtendedMessage);
    return ExtendedMessage;

});

// /*  Copyright 2016-2017 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
//     License MIT (https://opensource.org/licenses/MIT). */
// odoo.define("web_debranding.bot", function(require) {
//     "use strict";

//     require("web_debranding.dialog");
//     // var Message = require("mail.model.Message");
//     var session = require("web.session");
//     var MailBotService = require("mail_bot.MailBotService");
//     var core = require("web.core");
//     var _t = core._t;
//     console.log("Bot")
//     const {registerInstancePatchModel,} = require('mail/static/src/model/model_core.js');


// registerInstancePatchModel('mail.message', 'web_debranding/static/src/js/bot.js', {
// // /home/abuzar/Project/odoo/Abuzar/web_debranding/static/src/js/bot.js
//     //--------------------------------------------------------------------------
//     // Public
//     //--------------------------------------------------------------------------

//     /**
//      * @override
//      */
//         _getAuthorName(){
//             if (this._isOdoobotAuthor()) {
//                 return "Bot";
//             }
//             return this._super.apply(this, arguments);
//         },
//         getAvatarSource(){
//             if (this._isOdoobotAuthor()) {
//                 return "/web/binary/company_logo?company_id=" + session.company_id;
//             }
//             return this._super.apply(this, arguments);
//         },
// });

//     // Message.include({
//     //     _getAuthorName: function() {
//     //         if (this._isOdoobotAuthor()) {
//     //             return "Bot";
//     //         }
//     //         return this._super.apply(this, arguments);
//     //     },
//     //     getAvatarSource: function() {
//     //         if (this._isOdoobotAuthor()) {
//     //             return "/web/binary/company_logo?company_id=" + session.company_id;
//     //         }
//     //         return this._super.apply(this, arguments);
//     //     },
//     // });

//     // MailBotService.include({
//     //     getPreviews: function(filter) {
//     //         var previews = this._super.apply(this, arguments);
//     //         previews.map(function(preview) {
//     //             if (preview.title === _t("OdooBot has a request")) {
//     //                 preview.title = _t("Bot has a request");
//     //             }
//     //             if (preview.imageSRC === "/mail/static/src/img/odoobot.png") {
//     //                 preview.imageSRC =
//     //                     "/web/binary/company_logo?company_id=" + session.company_id;
//     //             }
//     //             return preview;
//     //         });
//     //         return previews;
//     //     },
//     // });
// });



// // const {
// //     registerInstancePatchModel,
// // } = require('mail/static/src/model/model_core.js');

// // registerInstancePatchModel('mail.message', 'sms/static/src/models/message/message.js', {