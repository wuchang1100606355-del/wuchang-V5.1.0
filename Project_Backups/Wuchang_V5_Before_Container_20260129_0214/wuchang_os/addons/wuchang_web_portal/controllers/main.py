# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class WuchangPortal(http.Controller):
    @http.route('/', type='http', auth="public", website=True)
    def index(self, **kw):
        return request.render('website.homepage')
