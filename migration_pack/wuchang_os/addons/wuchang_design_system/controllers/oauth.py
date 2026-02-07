from odoo import http


class WuchangOAuthController(http.Controller):
    @http.route('/web/login/oauth_providers', type='json', auth='public', website=True, csrf=False)
    def oauth_providers(self):
        env = http.request.env
        providers = env['auth.oauth.provider'].sudo().search([('enabled', '=', True)])
        return [
            {
                'id': p.id,
                'name': p.name,
                'client_id': p.client_id,
            }
            for p in providers
        ]
