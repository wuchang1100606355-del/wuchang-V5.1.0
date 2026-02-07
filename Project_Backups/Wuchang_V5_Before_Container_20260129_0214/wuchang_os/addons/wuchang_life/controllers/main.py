from odoo import http
from odoo.http import request


class WuchangLifeController(http.Controller):
    @http.route('/wuchang/life', type='http', auth='public', website=True)
    def life(self, **kwargs):
        return request.render('wuchang_life.life_page')

    @http.route('/wuchang/records', type='http', auth='public', website=True)
    def records(self, **kwargs):
        return request.render('wuchang_life.record_hall_page')

    @http.route('/wuchang/workspace', type='http', auth='public', website=True)
    def workspace(self, **kwargs):
        return request.render('wuchang_life.workspace_page')
