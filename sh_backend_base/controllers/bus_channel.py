# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo.http import request

from odoo.addons.bus.controllers.main import BusController

class PushNotification(BusController):

    def _poll(self, dbname, channels, last, options): 
        """Add the relevant channels to the BusController polling."""
        if options.get('sh.user.push.notifications'):
            channels = list(channels)
            lock_channel = (
                request.db,
                'sh.user.push.notifications',
                options.get('sh.user.push.notifications')
            )
            channels.append(lock_channel)
        return super(PushNotification, self)._poll(dbname, channels, last, options)
    