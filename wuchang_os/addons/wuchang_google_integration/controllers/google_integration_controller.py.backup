# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class GoogleIntegrationController(http.Controller):

    @http.route('/google/integration/meet/create', type='json', auth='user')
    def create_google_meet(self, **kwargs):
        """建立 Google Meet 會議 API"""
        try:
            # 檢查權限
            if not request.env.user.has_group('wuchang_google_integration.group_google_integration_user'):
                return {'error': '權限不足'}
            
            # 取得參數
            name = kwargs.get('name')
            start_datetime = kwargs.get('start_datetime')
            end_datetime = kwargs.get('end_datetime')
            partner_ids = kwargs.get('partner_ids', [])
            
            # 建立 Google Meet 會議
            meet = request.env['wuchang.google.meet'].create({
                'name': name,
                'start_datetime': start_datetime,
                'end_datetime': end_datetime,
                'partner_ids': [(6, 0, partner_ids)],
            })
            
            meet.action_create_google_meet()
            
            return {
                'success': True,
                'meet_id': meet.id,
                'meet_link': meet.google_meet_link,
            }
            
        except Exception as e:
            _logger.error(f"建立 Google Meet 會議失敗: {str(e)}")
            return {'error': str(e)}
    
    @http.route('/google/integration/form/create', type='json', auth='user')
    def create_google_form(self, **kwargs):
        """建立 Google 表單 API"""
        try:
            # 檢查權限
            if not request.env.user.has_group('wuchang_google_integration.group_google_integration_user'):
                return {'error': '權限不足'}
            
            # 取得參數
            name = kwargs.get('name')
            form_type = kwargs.get('form_type', 'document')
            description = kwargs.get('description')
            
            # 建立 Google 表單
            form = request.env['wuchang.google.form'].create({
                'name': name,
                'form_type': form_type,
                'description': description,
            })
            
            form.action_create_google_form()
            
            return {
                'success': True,
                'form_id': form.id,
                'form_url': form.google_form_url,
            }
            
        except Exception as e:
            _logger.error(f"建立 Google 表單失敗: {str(e)}")
            return {'error': str(e)}
