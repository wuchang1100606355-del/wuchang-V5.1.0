# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Velocity Protocol Fields
    turnover_count = fields.Integer(string="Transaction Turnover", default=0, help="Total number of successful transactions.")
    velocity_level = fields.Selection([
        ('newbie', 'Newbie (<30)'),
        ('regular', 'Regular (30-100)'),
        ('veteran', 'Veteran (>100)')
    ], string="Velocity Level", compute='_compute_velocity_level', store=True)

    @api.depends('turnover_count')
    def _compute_velocity_level(self):
        for partner in self:
            if partner.turnover_count > 100:
                partner.velocity_level = 'veteran'
            elif partner.turnover_count >= 30:
                partner.velocity_level = 'regular'
            else:
                partner.velocity_level = 'newbie'

    def get_max_discount_allowed(self):
        """Returns the maximum discount percentage this partner can offer."""
        self.ensure_one()
        if self.velocity_level == 'veteran':
            return 100.0
        elif self.velocity_level == 'regular':
            return 50.0
        else:
            return 30.0

class BusinessAISecretary(models.AbstractModel):
    _name = 'wuchang.business.secretary'
    _description = 'AI Secretary for Business'

    @api.model
    def analyze_heatmap_and_suggest(self, heatmap_data):
        """
        Analyzes heatmap data to suggest issuing coupons.
        Mock logic: If traffic is low (< 10 people), suggest a coupon.
        """
        # heatmap_data could be a dict like {'hour': 14, 'traffic': 5}
        traffic = heatmap_data.get('traffic', 0)
        hour = heatmap_data.get('hour', 12)

        if traffic < 10:
            return f"下午 {hour} 點人流稀少（僅 {traffic} 人）。建議發送一張 100% 導客券把隔壁社區的人拉過來！"
        return "目前人流穩定，繼續保持。"
