# -*- coding: utf-8 -*-
from odoo import models, fields, api

# ==========================================
# 2. 住戶與商家模組
# ==========================================
class ResPartner(models.Model):
    _inherit = 'res.partner'

    whc_wallet_balance = fields.Float('幸福幣餘額', default=0.0, readonly=True)
    wish_credit_balance = fields.Float('非營利機構營運補助暨社區提案補助金', default=0.0, readonly=True)
    marketing_subsidy_quota = fields.Float('可用行銷補助額度', default=0.0, readonly=True)
    merchant_quota_balance = fields.Float('商家額度餘額', default=0.0)
    whc_ledger_ids = fields.One2many('wuchang.coin.ledger', 'partner_id', string='WHC Ledger')
    
    is_wuchang_resident = fields.Boolean('五常住戶', default=False)
    is_wuchang_merchant = fields.Boolean('五常公益商家', default=False)
    is_fund_pool_store = fields.Boolean('基金池直營店', default=False)
    is_honorary_merchant = fields.Boolean('榮譽商家', default=False)
    
    wuchang_shareholder_level = fields.Selection([('normal', '一般居民'), ('core', '核心股東')], compute='_compute_level', store=True)

    @api.depends('whc_wallet_balance')
    def _compute_level(self):
        for r in self:
            r.wuchang_shareholder_level = 'core' if r.whc_wallet_balance >= 1000 else 'normal'

    def add_marketing_quota(self, amount):
        self.sudo().write({'marketing_subsidy_quota': self.marketing_subsidy_quota + amount})
