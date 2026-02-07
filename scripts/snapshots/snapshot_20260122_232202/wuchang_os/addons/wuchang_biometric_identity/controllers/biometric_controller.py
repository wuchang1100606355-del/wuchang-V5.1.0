# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class BiometricController(http.Controller):
    
    @http.route('/api/biometric/verify', type='json', auth='user', methods=['POST'], csrf=False)
    def verify_biometric(self, **kwargs):
        """生物辨識驗證 API"""
        try:
            data = request.jsonrequest
            person_name = data.get('person_name', '').strip()
            biometric_data = data.get('biometric_data')
            mac_address = data.get('mac_address', '').strip()
            
            if not person_name:
                return {
                    'ok': False,
                    'error': 'missing_person_name',
                    'message': '缺少姓名參數'
                }
            
            # 尋找身份記錄
            identity = request.env['biometric.identity'].search([
                ('person_name', '=', person_name),
                ('is_active', '=', True)
            ], limit=1)
            
            if not identity:
                return {
                    'ok': False,
                    'error': 'identity_not_found',
                    'message': f'找不到 {person_name} 的身份記錄'
                }
            
            # 執行生物辨識驗證
            result = identity.verify_biometric(biometric_data, mac_address)
            
            # 如果是系統創辦人，授予階段三權限
            permission_stage = '3' if identity.is_founder and identity.accountability_priority == 1 else '1'
            
            # 更新驗證記錄的權限階段
            if result.get('verification_id'):
                verification = request.env['biometric.verification'].browse(result['verification_id'])
                verification.write({
                    'permission_stage': permission_stage,
                    'verification_result': 'success'
                })
            
            return {
                'ok': True,
                'verified': True,
                'identity_id': identity.id,
                'person_name': identity.person_name,
                'is_founder': identity.is_founder,
                'permission_stage': permission_stage,
                'verification_id': result.get('verification_id'),
                'message': '生物辨識驗證成功'
            }
            
        except Exception as e:
            _logger.error(f"生物辨識驗證錯誤: {str(e)}")
            return {
                'ok': False,
                'error': 'verification_error',
                'message': str(e)
            }
    
    @http.route('/api/biometric/founder/check', type='json', auth='user', methods=['POST'], csrf=False)
    def check_founder_biometric(self, **kwargs):
        """檢查系統創辦人生物辨識狀態"""
        try:
            founder = request.env['biometric.identity'].find_founder_identity()
            
            if not founder:
                return {
                    'ok': False,
                    'error': 'founder_not_found',
                    'message': '找不到系統創辦人身份記錄'
                }
            
            return {
                'ok': True,
                'founder_exists': True,
                'person_name': founder.person_name,
                'has_biometric_data': bool(founder.biometric_data),
                'last_verified': founder.last_verified.isoformat() if founder.last_verified else None,
                'verification_count': founder.verification_count
            }
            
        except Exception as e:
            _logger.error(f"檢查系統創辦人生物辨識狀態錯誤: {str(e)}")
            return {
                'ok': False,
                'error': 'check_error',
                'message': str(e)
            }
