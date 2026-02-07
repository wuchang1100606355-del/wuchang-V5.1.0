# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import timedelta

class EstateParcel(models.Model):
    _name = 'estate.parcel'
    _description = '包裹管理'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='包裹編號', required=True, copy=False, readonly=True, default='New')
    carrier = fields.Selection([
        ('post', '郵局'),
        ('blackcat', '黑貓宅急便'),
        ('hct', '新竹物流'),
        ('kerry', '嘉里大榮'),
        ('lalamove', 'Lalamove'),
        ('foodpanda', 'Foodpanda'),
        ('uber', 'Uber Eats'),
        ('other', '其他')
    ], string='承運商', required=True, tracking=True)
    tracking_number = fields.Char(string='物流單號', tracking=True)
    
    # 收件人資訊
    partner_id = fields.Many2one('res.partner', string='收件住戶', required=True, tracking=True)
    unit_number = fields.Char(related='partner_id.unit_number', string='戶號', store=True)
    
    # 狀態管理
    state = fields.Selection([
        ('draft', '待收件'),
        ('arrived', '已到貨'),
        ('notified', '已通知'),
        ('picked', '已領取'),
        ('returned', '已退回')
    ], string='狀態', default='draft', tracking=True)
    
    # 時間戳記
    arrival_time = fields.Datetime(string='到貨時間', default=fields.Datetime.now)
    pickup_time = fields.Datetime(string='領取時間')
    
    # 智生活沒有的功能：生物辨識領取
    pickup_method = fields.Selection([
        ('qr', 'QR Code'),
        ('face', '人臉辨識'),
        ('nfc', '感應磁扣'),
        ('manual', '人工核銷')
    ], string='領取方式')
    
    pickup_proof = fields.Binary(string='領取存證照片', attachment=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('estate.parcel') or 'New'
        res = super(EstateParcel, self).create(vals)
        # 自動發送通知
        res._send_arrival_notification()
        return res

    def _send_arrival_notification(self):
        """發送推播通知給住戶"""
        for record in self:
            if record.state == 'draft':
                record.state = 'arrived'
            
            # 這裡介接 Line Bot 或 App 推播
            message = f"親愛的 {record.partner_id.name} 住戶，您的包裹 ({record.carrier}) 已送達管理室，請憑 QR Code 或刷臉領取。"
            record.message_post(body=message)
            record.state = 'notified'

    def action_confirm_pickup(self, method='manual'):
        """領取確認"""
        self.ensure_one()
        self.state = 'picked'
        self.pickup_time = fields.Datetime.now()
        self.pickup_method = method
        return True
