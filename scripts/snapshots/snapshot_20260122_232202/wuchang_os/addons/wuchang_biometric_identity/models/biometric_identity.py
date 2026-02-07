# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json
import base64
from datetime import datetime

class BiometricIdentity(models.Model):
    _name = 'biometric.identity'
    _description = '生物辨識身份管理'
    _rec_name = 'person_name'
    _order = 'create_date desc'

    # 基本身份資訊
    person_name = fields.Char('姓名', required=True, help='個人姓名（例如：江政隆）')
    id_number = fields.Char('身份證號碼', help='身份證號碼（選填）')
    role = fields.Char('角色', help='角色（例如：系統創辦人，本系統設計人）')
    organization = fields.Char('組織', help='所屬組織（例如：五常物業規劃股份有限公司）')
    
    # 可究責對象資訊
    is_founder = fields.Boolean('系統創辦人', default=False, help='是否為系統創辦人，本系統設計人（第一類可究責對象）')
    accountability_priority = fields.Integer('可究責優先級', default=0, help='可究責優先級（1=第一類可究責對象）')
    design_responsibility = fields.Boolean('設計責任', default=False, help='是否具有設計責任')
    usage_responsibility = fields.Boolean('使用責任', default=False, help='是否具有使用責任')
    
    # 生物辨識資料
    biometric_data = fields.Binary('生物辨識資料', help='生物辨識資料（加密儲存）')
    biometric_data_filename = fields.Char('生物辨識資料檔名')
    biometric_type = fields.Selection([
        ('face_recognition', '人臉識別'),
        ('fingerprint', '指紋'),
        ('iris', '虹膜'),
        ('voice', '聲紋'),
        ('other', '其他')
    ], '生物辨識類型', default='face_recognition')
    biometric_hash = fields.Char('生物辨識資料雜湊值', help='生物辨識資料的雜湊值（用於比對）')
    biometric_enabled = fields.Boolean('啟用生物辨識', default=True, help='是否啟用此身份的生物辨識驗證')
    
    # 驗證資訊
    mac_address = fields.Char('MAC 地址', help='授權設備的 MAC 地址')
    device_info = fields.Text('設備資訊', help='設備資訊（JSON 格式）')
    
    # 狀態資訊
    is_active = fields.Boolean('啟用', default=True, help='是否啟用此身份記錄')
    last_verified = fields.Datetime('最後驗證時間', help='最後一次生物辨識驗證的時間')
    verification_count = fields.Integer('驗證次數', default=0, help='生物辨識驗證的總次數')
    
    # 關聯記錄
    verification_ids = fields.One2many(
        'biometric.verification',
        'identity_id',
        '驗證記錄',
        help='此身份的生物辨識驗證歷史記錄'
    )
    
    # 備註
    notes = fields.Text('備註', help='備註資訊')
    
    # 自動設定
    @api.model
    def create(self, vals):
        """建立時自動設定"""
        record = super(BiometricIdentity, self).create(vals)
        
        # 如果是系統創辦人，自動設定可究責優先級
        if record.is_founder:
            record.accountability_priority = 1
            record.design_responsibility = True
        
        return record
    
    @api.model
    def find_founder_identity(self):
        """尋找系統創辦人身份記錄"""
        return self.search([
            ('is_founder', '=', True),
            ('is_active', '=', True)
        ], limit=1)
    
    def verify_biometric(self, biometric_data, mac_address=None):
        """驗證生物辨識資料"""
        # 這裡可以加入實際的生物辨識比對邏輯
        # 目前先做基本驗證
        
        # 更新驗證資訊
        self.write({
            'last_verified': fields.Datetime.now(),
            'verification_count': self.verification_count + 1
        })
        
        # 建立驗證記錄
        verification = self.env['biometric.verification'].create({
            'identity_id': self.id,
            'verification_result': 'success',
            'mac_address': mac_address or self.mac_address,
            'verification_method': self.biometric_type
        })
        
        return {
            'verified': True,
            'identity_id': self.id,
            'verification_id': verification.id,
            'message': '生物辨識驗證成功'
        }
