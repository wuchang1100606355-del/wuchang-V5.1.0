from odoo import http
from odoo.http import request


class WuchangCommunityCampaign(http.Controller):
    @http.route('/campaign', type='http', auth='public', website=True)
    def campaign_home(self, **kwargs):
        return request.render('wuchang_community_campaign.campaign_home', {})


class CommunityCampaignController(http.Controller):
    @http.route(['/community/wish-tree'], type='http', auth="public", website=True)
    def wish_tree_home(self, **kwargs):
        campaigns = request.env['wuchang.community.campaign'].sudo().search([('state', 'in', ['active', 'funded'])])
        return request.render('wuchang_community_campaign.wish_tree_page', {
            'campaigns': campaigns,
        })

    @http.route(['/community/wish/vote'], type='json', auth="user")
    def wish_vote(self, wish_id):
        wish = request.env['wuchang.community.wish'].sudo().browse(int(wish_id))
        if wish.exists():
            wish.action_upvote()
            return {'new_count': wish.vote_count}
        return {'error': 'Wish not found'}

    @http.route(['/community/wish/submit'], type='http', auth="user", website=True, methods=['POST'])
    def wish_submit(self, **post):
        title = (post.get('title') or '').strip()
        cid = post.get('campaign_id')
        if title and cid:
            request.env['wuchang.community.wish'].sudo().create({
                'name': title,
                'description': post.get('description') or '',
                'campaign_id': int(cid),
                'color_theme': post.get('color_theme', 'green'),
            })
        return request.redirect('/community/wish-tree')


class LittleJHubController(http.Controller):
    @http.route(['/little-j/hub'], type='http', auth="public", website=True)
    def little_j_hub(self, **kwargs):
        return request.render('wuchang_community_campaign.little_j_service_hub', {})
