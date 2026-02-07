# -*- coding: utf-8 -*-
from odoo import models, fields, api
import hashlib

class EstateBiometric(models.Model):
    _name = 'estate.biometric'
    _description = '生物特徵管理 (隱私優先)'
    _inherit = ['mail.thread']

    name = fields.Char(string='識別名稱', required=True, default='Face ID')
    partner_id = fields.Many2one('res.partner', string='住戶', required=True, ondelete='cascade')
    
    # 安全核心：不存照片，只存特徵向量
    # 這裡模擬儲存加密後的特徵值 (實際應用會是 128/512 維度的浮點數陣列的加密 blob)
    embedding_data = fields.Text(string='特徵向量 (Encrypted)', required=True, help="加密的人臉特徵值，無法還原為照片")
    embedding_version = fields.Char(string='模型版本', default='v1.0')
    
    active = fields.Boolean(default=True)
    last_verified = fields.Datetime(string='最後驗證時間')
    
    # 授權設備
    allowed_device_ids = fields.Json(string='授權設備列表', default=list)

    @api.model
    def register_face(self, partner_id, vector_data):
        """
        註冊人臉 (由地端 Little J 呼叫)
        注意：這裡接收的 vector_data 已經是地端提取過的特徵，不是照片
        """
        # 再次雜湊處理，確保即使資料庫外洩也難以利用
        secure_hash = hashlib.sha256(vector_data.encode()).hexdigest()
        
        return self.create({
            'partner_id': partner_id,
            'embedding_data': secure_hash, # 模擬存儲
            'name': f"Face ID - {fields.Date.today()}"
        })

    def verify(self, input_vector):
        """
        驗證人臉 (比對特徵值)
        """
        self.ensure_one()
        # 實際會使用向量距離計算 (如 Cosine Similarity)
        # 這裡僅作示意
        input_hash = hashlib.sha256(input_vector.encode()).hexdigest()
        if input_hash == self.embedding_data:
            self.last_verified = fields.Datetime.now()
            return True
        return False

class EstateIntercomSession(models.Model):
    _name = 'estate.intercom.session'
    _description = '零信任對講機信令'
    
    # 一次性通話 ID
    session_id = fields.Char(string='Session ID', required=True, readonly=True)
    
    # 通話雙方
    caller_device_id = fields.Char(string='訪客設備/門口機')
    callee_partner_id = fields.Many2one('res.partner', string='住戶')
    
    # WebRTC 信令交換 (SDP)
    # 這些資料只用於建立連線，連線建立後即無用，應定期清除
    sdp_offer = fields.Text(string='SDP Offer (Guest)')
    sdp_answer = fields.Text(string='SDP Answer (Resident)')
    ice_candidates = fields.Text(string='ICE Candidates (JSON)')
    
    state = fields.Selection([
        ('offering', '呼叫中'),
        ('ringing', '響鈴中'),
        ('connected', '通話中'),
        ('ended', '已結束'),
        ('missed', '未接聽')
    ], default='offering', required=True)
    
    start_time = fields.Datetime(default=fields.Datetime.now)
    end_time = fields.Datetime()

    @api.model
    def create_offer(self, device_id, unit_number, sdp):
        """訪客發起呼叫"""
        # 根據戶號查找住戶
        partner = self.env['res.partner'].search([('unit_number', '=', unit_number)], limit=1)
        if not partner:
            return {'error': 'Unit not found'}
            
        session = self.create({
            'session_id': self.env['ir.sequence'].next_by_code('estate.intercom'),
            'caller_device_id': device_id,
            'callee_partner_id': partner.id,
            'sdp_offer': sdp,
            'state': 'ringing'
        })
        
        # TODO: 推播通知給住戶 App
        # self.env['bus.bus'].sendone(...)
        
        return {'session_id': session.session_id, 'status': 'ringing'}

    def submit_answer(self, sdp_answer):
        """住戶接聽"""
        self.ensure_one()
        self.sdp_answer = sdp_answer
        self.state = 'connected'
        return True

    def end_call(self):
        """結束通話"""
        self.ensure_one()
        self.state = 'ended'
        self.end_time = fields.Datetime.now()
        # 清除敏感的 SDP 資訊，只留通話紀錄
        self.sdp_offer = None
        self.sdp_answer = None
        self.ice_candidates = None
