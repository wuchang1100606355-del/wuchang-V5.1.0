from odoo import models, fields, api


class CommunityCampaign(models.Model):
    _name = 'wuchang.community.campaign'
    _description = 'Community Fundraising & Wish Campaign'
    _inherit = ['website.published.mixin']

    name = fields.Char('Campaign Name', required=True)
    description = fields.Text('Description')
    image = fields.Image('Banner Image')

    # Financials
    target_amount = fields.Float('Target Amount')
    current_amount = fields.Float('Current Amount')
    progress = fields.Float('Progress', compute='_compute_progress')

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Voting Active'),
        ('funded', 'Funded'),
        ('done', 'Completed')
    ], default='draft', string="Status")

    wish_ids = fields.One2many('wuchang.community.wish', 'campaign_id', string="Wishes")

    @api.depends('target_amount', 'current_amount')
    def _compute_progress(self):
        for record in self:
            if record.target_amount > 0:
                record.progress = (record.current_amount / record.target_amount) * 100
            else:
                record.progress = 0


class CommunityWish(models.Model):
    _name = 'wuchang.community.wish'
    _description = 'User Wishes & Votes'

    name = fields.Char('Wish Title', required=True)
    description = fields.Text('Why this matters?')
    user_id = fields.Many2one('res.users', string='Wisher', default=lambda self: self.env.user)
    campaign_id = fields.Many2one('wuchang.community.campaign', string='Campaign')

    vote_count = fields.Integer('Votes', default=0)

    # Visual Customization
    color_theme = fields.Selection([
        ('gold', 'Gold (Wealth/Value)'),
        ('green', 'Green (Eco/Life)'),
        ('blue', 'Blue (Tech/Logic)'),
        ('pink', 'Pink (Love/Care)'),
    ], default='green', string="Card Theme")

    def action_upvote(self):
        self.vote_count += 1
        return True

