from odoo import models, fields, api, _

class CommunityProduct(models.Model):
    _name = 'community.product'
    _description = '社區商品'

    name = fields.Char('商品名稱', required=True)
    description = fields.Text('商品說明')
    price = fields.Float('價格 (NTD)', required=True)
    coin_reward = fields.Float('回饋幸福幣', default=0.0)
    image_url = fields.Char('圖片連結')
    category = fields.Selection([
        ('service', '生活服務'),
        ('food', '美食團購'),
        ('charity', '公益商品'),
        ('used', '二手市集')
    ], string='類別', required=True)
    
    partner_id = fields.Many2one('res.partner', string='供應商/賣家')
    active = fields.Boolean(default=True)

class CommunityOrder(models.Model):
    _name = 'community.order'
    _description = '社區訂單'

    name = fields.Char('訂單編號', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='買家', required=True)
    product_id = fields.Many2one('community.product', string='商品', required=True)
    amount = fields.Float('金額')
    status = fields.Selection([
        ('draft', '草稿'),
        ('paid', '已付款'),
        ('delivered', '已交付'),
        ('cancelled', '已取消')
    ], string='狀態', default='draft')
    date_order = fields.Datetime('訂購時間', default=fields.Datetime.now)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('community.order') or _('New')
        return super(CommunityOrder, self).create(vals)

    def action_pay(self):
        # 這裡未來可擴充金流串接
        self.write({'status': 'paid'})
        # 發放幸福幣回饋
        if self.product_id.coin_reward > 0:
            self.partner_id.sudo().write({
                'whc_wallet_balance': self.partner_id.whc_wallet_balance + self.product_id.coin_reward
            })
            self.env['wuchang.coin.transaction'].create({
                'dest_partner_id': self.partner_id.id,
                'amount': self.product_id.coin_reward,
                'transaction_type': 'reward',
                'description': f'購買回饋: {self.product_id.name}'
            })
class CommunityPartnerShop(models.Model):
    _name = 'community.partner.shop'
    _description = '合作商家'

    partner_id = fields.Many2one('res.partner', string='商家關聯', required=True)
    shop_name = fields.Char('店名', related='partner_id.name', readonly=False)
    revenue_share_percentage = fields.Float('營收提撥比例(%)', default=5.0)
    total_contribution = fields.Float('累計貢獻基金', readonly=True)

    def action_process_daily_sales(self, daily_revenue):
        # 計算提撥金
        contribution = daily_revenue * (self.revenue_share_percentage / 100.0)
        self.write({'total_contribution': self.total_contribution + contribution})
        
        # 轉入社區基金池
        pool = self.env['community.fund.pool'].search([], limit=1)
        if pool:
            pool.add_fund(contribution, 'partner')
        return contribution
    # 外送業務與補助金欄位
    delivery_revenue_share = fields.Float('外送營收提撥(%)', default=8.0)
    subsidy_received = fields.Float('累計獲得補助金', readonly=True)
    subsidy_status = fields.Selection([
        ('none', '未申請'),
        ('pending', '審核中'),
        ('approved', '已核准'),
        ('rejected', '已拒絕')
    ], string='補助申請狀態', default='none')
    subsidy_request_amount = fields.Float('申請補助金額')

    def action_request_subsidy(self, amount):
        if amount <= 0:
            raise UserError('申請金額必須大於 0')
        self.write({
            'subsidy_status': 'pending',
            'subsidy_request_amount': amount
        })
        return True

    def action_approve_subsidy(self):
        # 扣除基金池
        pool = self.env['community.fund.pool'].search([], limit=1)
        if not pool or pool.total_amount < self.subsidy_request_amount:
            raise UserError('基金池餘額不足！')
        
        pool.add_fund(-self.subsidy_request_amount, 'subsidy') # 支出
        
        self.write({
            'subsidy_status': 'approved',
            'subsidy_received': self.subsidy_received + self.subsidy_request_amount,
            'subsidy_request_amount': 0
        })
        return True

