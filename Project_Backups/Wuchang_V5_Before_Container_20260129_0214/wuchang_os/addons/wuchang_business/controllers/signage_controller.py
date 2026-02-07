# -*- coding: utf-8 -*-
from odoo import http


class SignageController(http.Controller):
    @http.route('/wuchang/signage', auth='public', website=True)
    def signage(self, **kw):
        return "Signage Controller Placeholder"
