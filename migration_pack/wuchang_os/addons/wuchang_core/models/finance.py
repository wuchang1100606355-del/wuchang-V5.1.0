# -*- coding: utf-8 -*-
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

    # Unified fields
    balance_twd = fields.Float(string='新台幣餘額 (TWD)', readonly=True)
    balance_whc = fields.Float(string='幸福幣餘額 (WHC)', readonly=True)

    # Alias fields for compatibility if needed, or we just update references
    total_twd_assets = fields.Float(
        string='基金總資產 (TWD)', related='balance_twd', readonly=True)
    total_whc_circulation = fields.Float(
        string='幸福幣流通總量', related='balance_whc', readonly=True)


class TransparencyLog(models.Model):
    """
    透明誠信軌跡 (玻璃口袋)
    """
    _name = 'transparency.log'
    _description = '透明誠信軌跡'

    name = fields.Char(string='交易摘要')
    timestamp = fields.Datetime(string='時間戳記', default=fields.Datetime.now)
    amount = fields.Float(string='金額')
    flow_type = fields.Selection([
        ('inflow', '流入'),
        ('outflow', '流出')
    ], string='資金流向')


class WuchangCoinTransaction(models.Model):
    """
    幸福幣交易紀錄 (Blockchain-like Ledger)
    """
    _name = 'wuchang.coin.transaction'
    _description = '幸福幣交易紀錄'

    source_partner_id = fields.Many2one('res.partner', string='轉出方')
    dest_partner_id = fields.Many2one('res.partner', string='轉入方')
    amount = fields.Float(string='金額 (WHC)', required=True)
    transaction_type = fields.Selection([
        ('mint', '鑄造 (捐款換幣)'),
        ('transfer', '轉帳 (消費)'),
        ('reward', '獎勵 (志工發放)'),
        ('burn', '銷毀 (商家核銷)')
    ], required=True)
    timestamp = fields.Datetime(default=fields.Datetime.now)

    # 數位玻璃口袋 (Mod 17)
    hash_signature = fields.Char(string='不可篡改雜湊值', readonly=True)
