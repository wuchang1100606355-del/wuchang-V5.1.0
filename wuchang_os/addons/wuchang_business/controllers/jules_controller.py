# -*- coding: utf-8 -*-
from odoo import http


class JulesController(http.Controller):
    @http.route('/wuchang/jules', auth='user', website=True)
    def jules(self, **kw):
        return "Jules Controller Placeholder"
