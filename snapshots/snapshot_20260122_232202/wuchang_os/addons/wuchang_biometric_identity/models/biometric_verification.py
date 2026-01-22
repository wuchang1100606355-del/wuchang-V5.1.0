# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class BiometricVerification(models.Model):
    _name = 'biometric.verification'
    _description = '生物辨識驗證記錄'
    _rec_name = 'verification_time'
    _order = 'verification_time desc'

    identity_id = fields.Many2one(
        'biometric.identity',
        '身份記錄',
        required=True,
        ondelete='cascade',
        help='對應的生物辨識身份記錄'
    )
    
    person_name = fields.Char('姓名', related='identity_id.person_name', store=True, readonly=True)
    
    verification_time = fields.Datetime('驗證時間', required=True, default=fields.Datetime.now, help='生物辨識驗證的時間')
    
    verification_result = fields.Selection([
        ('success', '驗證成功'),
        ('failed', '驗證失敗'),
        ('pending', '待驗證'),
        ('error', '驗證錯誤')
    ], '驗證結果', required=True, default='pending', help='生物辨識驗證的結果')
    
    verification_method = fields.Selection([
        ('face_recognition', '人臉識別'),
        ('fingerprint', '指紋'),
        ('iris', '虹膜'),
        ('voice', '聲紋'),
        ('other', '其他')
    ], '驗證方法', help='使用的生物辨識驗證方法')
    
    mac_address = fields.Char('MAC 地址', help='驗證時使用的設備 MAC 地址')
    device_info = fields.Text('設備資訊', help='驗證時使用的設備資訊（JSON 格式）')
    
    permission_stage = fields.Selection([
        ('1', '階段一：限縮權限'),
        ('2', '階段二：最高權限'),
        ('3', '階段三：權限解放')
    ], '權限階段', help='驗證後授予的權限階段')
    
    operation_type = fields.Char('操作類型', help='使用此驗證執行的操作類型')
    operation_details = fields.Text('操作詳情', help='操作的詳細資訊（JSON 格式）')
    
    error_message = fields.Text('錯誤訊息', help='如果驗證失敗，記錄錯誤訊息')
    
    notes = fields.Text('備註', help='備註資訊')
    
    # 自動設定
    @api.model
    def create(self, vals):
        """建立時自動設定驗證時間"""
        if 'verification_time' not in vals:
            vals['verification_time'] = fields.Datetime.now()
        return super(BiometricVerification, self).create(vals)
    
    def get_verification_summary(self):
        """取得驗證摘要"""
        return {
            'identity_id': self.identity_id.id,
            'person_name': self.person_name,
            'verification_time': self.verification_time.isoformat() if self.verification_time else None,
            'verification_result': self.verification_result,
            'permission_stage': self.permission_stage,
            'mac_address': self.mac_address
        }
