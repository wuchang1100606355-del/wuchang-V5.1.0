from odoo import models, fields, api

class CommunityFundAccount(models.Model):
    """
    【Mod 7, 11, 12, 13】五常基金與 DeFi 核心帳本
    管理三大資金池：消費者遞延池、商家額度池、志工營運池、核心公積金
    """
    _name = 'community.fund.account'
    _description = '社區基金帳戶'

    name = fields.Char(string='帳戶名稱', required=True)
    account_type = fields.Selection([
        ('general', '一般資金池'),
        ('reserve', '遞延準備金 (100% Reserve)'),
        ('surplus', '永續公積金 (Retained Surplus)'),  # 那神聖的 $9 元
        ('welfare', '弱勢照顧專戶'),
        ('ops', '系統營運專戶')
    ], required=True)

    # Missing fields added here to resolve "Key Insertion" error
    merchant_donation_total = fields.Float(string='商家捐款總額', default=0.0)
    consumer_donation_total = fields.Float(string='消費者捐款總額', default=0.0)
    merchant_custody_total = fields.Float(string='商家保管總額', default=0.0)
    deferred_whc_quota = fields.Float(string='遞延幸福幣額度', default=0.0)
    google_maps_credit = fields.Float(string='Google Maps 抵免額', default=0.0)
    deferred_voucher_quota = fields.Float(string='遞延兌換券額度', default=0.0)

    balance = fields.Float(string='當前餘額', compute='_compute_balance', store=True)
    transaction_ids = fields.One2many('community.fund.transaction', 'account_id', string='交易明細')

    @api.depends('transaction_ids.amount')
    def _compute_balance(self):
        for account in self:
            account.balance = sum(account.transaction_ids.mapped('amount'))

class CommunityFundTransaction(models.Model):
    _name = 'community.fund.transaction'
    _description = '基金交易明細'

    account_id = fields.Many2one('community.fund.account', string='帳戶', required=True)
    amount = fields.Float(string='金額', required=True)
    reference = fields.Char(string='關聯單號')
    note = fields.Char(string='備註')
    date = fields.Datetime(string='交易時間', default=fields.Datetime.now)
