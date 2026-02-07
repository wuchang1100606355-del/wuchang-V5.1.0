# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class WuchangPortal(http.Controller):
    @http.route('/', type='http', auth="public", website=True)
    def index(self, **kw):
        # 這裡未來可以注入即時戰情數據
        return request.render('website.homepage')
