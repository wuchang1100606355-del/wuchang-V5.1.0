from odoo import http


class WuchangOAuthController(http.Controller):
    @http.route('/web/login/oauth_providers', type='json', auth='public', website=True, csrf=False)
    def oauth_providers(self):
        env = http.request.env
        try:
            providers = env['auth.oauth.provider'].sudo().search([('enabled', '=', True)])
        except Exception:
            providers = env['auth.oauth.provider']
            try:
                providers = providers.browse([])
            except Exception:
                providers = []
        result = []
        for p in providers:
            result.append(
                {
                    'id': p.id,
                    'name': p.name,
                    'client_id': getattr(p, 'client_id', ''),
                }
            )
        return result
