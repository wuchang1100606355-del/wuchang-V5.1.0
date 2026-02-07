# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PersonalInvoice(models.Model):
    _name = 'wuchang.personal.invoice'
    _description = '個人發票與消費紀錄'
    _order = 'date desc, id desc'

    name = fields.Char('發票號碼', required=True, index=True)
    date = fields.Date('消費日期', default=fields.Date.context_today, required=True)
    amount = fields.Float('金額', required=True)
    seller_name = fields.Char('商家名稱')
    seller_ban = fields.Char('商家統編')
    
    # 手機條碼載具 (如: /AB1+234)
    carrier_id = fields.Char('手機條碼')
    
    # 關聯住戶
    user_id = fields.Many2one('res.users', string='住戶', default=lambda self: self.env.user, required=True)
    partner_id = fields.Many2one('res.partner', related='user_id.partner_id', string='合作夥伴', store=True)

    # 分類與明細
    category = fields.Selection([
        ('food', '餐飲'),
        ('transport', '交通'),
        ('life', '生活用品'),
        ('utility', '水電瓦斯'),
        ('ent', '娛樂'),
        ('other', '其他')
    ], string='消費分類', default='other')
    
    details = fields.Text('消費明細') # JSON or text list of items
    
    # 狀態
    lottery_result = fields.Selection([
        ('pending', '未對獎'),
        ('lost', '未中獎'),
        ('won', '中獎'),
        ('claimed', '已領獎')
    ], string='中獎狀態', default='pending')
    
    prize_amount = fields.Float('中獎金額')

    @api.model
    def create_from_scan(self, invoice_data):
        """
        從掃描或 API 匯入發票
        invoice_data: dict containing name, date, amount, seller_name, etc.
        """
        vals = {
            'name': invoice_data.get('invNum'),
            'date': invoice_data.get('invDate'), # Ensure format YYYY-MM-DD
            'amount': float(invoice_data.get('amount', 0)),
            'seller_name': invoice_data.get('sellerName'),
            'carrier_id': invoice_data.get('cardNo'),
            'details': invoice_data.get('details'),
        }
        return self.create(vals)

class PersonalExpenseBudget(models.Model):
    _name = 'wuchang.personal.budget'
    _description = '個人預算設定'
    
    user_id = fields.Many2one('res.users', string='住戶', default=lambda self: self.env.user)
    month = fields.Char('月份', help="Format: YYYY-MM")
    limit_amount = fields.Float('預算金額')
    current_amount = fields.Float('目前支出', compute='_compute_current_amount')
    
    @api.depends('user_id', 'month')
    def _compute_current_amount(self):
        for rec in self:
            # Simple computation logic placeholder
            rec.current_amount = 0.0
