from odoo import http
from odoo.http import request
import os

class WuchangPropertySiteController(http.Controller):
    @http.route('/hoa/site', type='http', auth='public', website=True)
    def hoa_site(self, **kw):
        hero = '/hoa/hero'
        return request.render('wuchang_property_toolkits.property_site', {
            'hero_url': hero,
        })

    @http.route('/hoa/hero', type='http', auth='public')
    def hoa_hero(self, **kw):
        base = os.path.join(os.getcwd(), 'memory_store/images/lao_coffee')
        preferred = []
        for n in ['hero.jpg', 'hero.png', 'banner.jpg', 'banner.png']:
            preferred.append(os.path.join(base, n))
        for fp in preferred:
            if os.path.isfile(fp):
                ext = os.path.splitext(fp)[1].lower()
                ctype = 'image/png' if ext == '.png' else 'image/jpeg'
                with open(fp, 'rb') as f:
                    return request.make_response(f.read(), headers=[('Content-Type', ctype)])
        try:
            candidates = []
            for name in os.listdir(base):
                if name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    fp = os.path.join(base, name)
                    if os.path.isfile(fp):
                        candidates.append((fp, os.path.getsize(fp)))
            if candidates:
                candidates.sort(key=lambda t: t[1], reverse=True)
                fp = candidates[0][0]
                ext = os.path.splitext(fp)[1].lower()
                ctype = 'image/webp' if ext == '.webp' else ('image/png' if ext == '.png' else 'image/jpeg')
                with open(fp, 'rb') as f:
                    return request.make_response(f.read(), headers=[('Content-Type', ctype)])
        except Exception:
            pass
        return request.not_found()
