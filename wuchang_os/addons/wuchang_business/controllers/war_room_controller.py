# -*- coding: utf-8 -*-
from odoo import http


class WarRoomController(http.Controller):
    @http.route('/wuchang/war_room', auth='user', website=True)
    def war_room(self, **kw):
        return "War Room Controller Placeholder"
