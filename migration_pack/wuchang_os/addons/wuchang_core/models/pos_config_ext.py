# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    opening_time = fields.Char(
        string='Opening Time', help='HH:MM 24h, e.g., 06:00')
    closing_time = fields.Char(
        string='Closing Time', help='HH:MM 24h, e.g., 14:00')
    overnight = fields.Boolean(
        string='Overnight Hours', help='If closing time is on the next day')

    # --- 營運模式設定 ---
    wuchang_store_mode = fields.Selection([
        ('donor', '總店模式 (Donor Mode)：月結全捐，不即時入帳'),
        ('fund', '仁義店模式 (Fund Mode)：營收即基金，100% 注入')
    ], string='五常營運模式', default='donor')

    # --- 數位看板 (TV) 設定 ---
    signage_screen_id = fields.Many2one(
        'wuchang.digital.signage', string='綁定廣告電視牆')
    signage_url = fields.Char(string='電視牆播放網址', compute='_compute_signage_url')

    # --- 客顯螢幕 (Customer Display) ---
    enable_little_j_interaction = fields.Boolean(
        string='啟用小J 互動 (客顯)', default=True)
    customer_display_msg = fields.Char(
        string='待機迎賓語', default='歡迎光臨五常社區！您的消費就是做公益。')

    @api.depends('signage_screen_id')
    def _compute_signage_url(self):
        for config in self:
            if config.signage_screen_id:
                base_url = self.env['ir.config_parameter'].sudo(
                ).get_param('web.base.url')
                config.signage_url = f"{base_url}/wuchang/signage/{config.signage_screen_id.id}"
            else:
                config.signage_url = False


class WuchangDigitalSignage(models.Model):
    """
    【Mod 48】五常影音聯播網管理
    管理電視牆的播放清單、跑馬燈
    """
    _name = 'wuchang.digital.signage'
    _description = '數位看板播放清單'

    name = fields.Char(string='看板名稱 (e.g., 仁義店大電視)', required=True)

    # --- 內容控制 ---
    marquee_text = fields.Char(string='即時跑馬燈文字', default='今日拿鐵買一送一！五常專勤隊募集中！')
    is_live_interrupt = fields.Boolean(
        string='插播緊急廣播', default=False, help="若勾選，電視將暫停播放清單，強制顯示跑馬燈或緊急畫面")

    playlist_ids = fields.One2many(
        'wuchang.signage.content', 'signage_id', string='播放內容')


class WuchangSignageContent(models.Model):
    _name = 'wuchang.signage.content'
    _description = '看板內容項目'
    _order = 'sequence'

    sequence = fields.Integer(string='排序', default=10)
    signage_id = fields.Many2one('wuchang.digital.signage', string='所屬看板')

    content_type = fields.Selection([
        ('image', '圖片'),
        ('video', '影片 (URL)'),
        ('dashboard', '戰情室 (Iframe)')
    ], default='image')

    url = fields.Char(string='資源網址 (URL)', help="圖片連結、YouTube 連結或戰情室網址")
    duration = fields.Integer(string='播放秒數', default=10)


class WuchangPosOrder(models.Model):
    """
    訂單邏輯擴充：處理基金注入
    """
    _inherit = 'pos.order'

    def _process_saved_orders(self, draft, orders, user_id):
        """
        覆寫訂單處理邏輯，攔截並注入基金 (如果是仁義店模式)
        """
        res = super(WuchangPosOrder, self)._process_saved_orders(
            draft, orders, user_id)

        for order_id in res:
            order = self.browse(order_id)
            if order.config_id.wuchang_store_mode == 'fund':
                # 仁義店模式：直接注入基金池
                self._inject_to_fund(order)
        return res

    def _inject_to_fund(self, order):
        """
        將訂單金額注入 community.fund.account
        """
        # 尋找「一般資金池」
        fund = self.env['community.fund.account'].search(
            [('account_type', '=', 'general')], limit=1)
        if fund:
            # 建立交易紀錄
            self.env['wuchang.coin.transaction'].create({
                # 消費者 (如果有會員)
                'source_partner_id': order.partner_id.id if order.partner_id else False,
                'dest_partner_id': order.company_id.partner_id.id,  # 協會
                'amount': order.amount_total,  # 營收全額
                'transaction_type': 'mint',  # 視為鑄造/注入 (TWD -> Fund)
            })
            # 這裡簡單模擬：實際邏輯應該是 TWD 增加，而非 WHC 增加，需視 wuchang_finance 邏輯調整
            # 假設 balance_twd 是可寫的，或透過方法更新
            # fund.balance_twd += order.amount_total (需透過 write)
            pass
