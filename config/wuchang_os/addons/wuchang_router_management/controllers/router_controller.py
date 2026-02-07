# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class RouterController(http.Controller):
    """路由器 API 控制器"""

    @http.route('/api/router/status', type='http', auth='user', methods=['GET'], csrf=False)
    def get_router_status(self):
        """取得路由器狀態"""
        try:
            router = request.env['router.router'].search([], limit=1)
            if router:
                router.action_check_status()
                return request.make_response(
                    json.dumps({
                        'status': router.status,
                        'connected_devices': router.connected_devices_count,
                        'last_check': router.last_check.isoformat() if router.last_check else None
                    }, ensure_ascii=False),
                    headers=[('Content-Type', 'application/json; charset=utf-8')]
                )
            else:
                return request.make_response(
                    json.dumps({'error': '未找到路由器記錄'}, ensure_ascii=False),
                    status=404,
                    headers=[('Content-Type', 'application/json; charset=utf-8')]
                )
        except Exception as e:
            _logger.error(f"取得路由器狀態失敗: {e}")
            return request.make_response(
                json.dumps({'error': str(e)}, ensure_ascii=False),
                status=500,
                headers=[('Content-Type', 'application/json; charset=utf-8')]
            )

    @http.route('/api/router/devices', type='http', auth='user', methods=['GET'], csrf=False)
    def get_devices(self):
        """取得連接設備列表"""
        try:
            devices = request.env['router.device'].search([])
            result = []
            for device in devices:
                result.append({
                    'name': device.name,
                    'ip': device.ip_address,
                    'mac': device.mac_address,
                    'type': device.device_type,
                    'is_server': device.is_server,
                    'server_identity': device.server_identity,
                    'status': device.status
                })
            
            return request.make_response(
                json.dumps({'devices': result}, ensure_ascii=False),
                headers=[('Content-Type', 'application/json; charset=utf-8')]
            )
        except Exception as e:
            _logger.error(f"取得設備列表失敗: {e}")
            return request.make_response(
                json.dumps({'error': str(e)}, ensure_ascii=False),
                status=500,
                headers=[('Content-Type', 'application/json; charset=utf-8')]
            )

    @http.route('/api/router/server_identities', type='http', auth='user', methods=['GET'], csrf=False)
    def get_server_identities(self):
        """取得伺服器身份列表"""
        try:
            identities = request.env['server.identity'].search([])
            result = []
            for identity in identities:
                result.append({
                    'name': identity.name,
                    'type': identity.identity_type,
                    'ip': identity.ip_address,
                    'mac': identity.mac_address,
                    'is_primary': identity.is_primary,
                    'services': identity.services
                })
            
            return request.make_response(
                json.dumps({'identities': result}, ensure_ascii=False),
                headers=[('Content-Type', 'application/json; charset=utf-8')]
            )
        except Exception as e:
            _logger.error(f"取得伺服器身份列表失敗: {e}")
            return request.make_response(
                json.dumps({'error': str(e)}, ensure_ascii=False),
                status=500,
                headers=[('Content-Type', 'application/json; charset=utf-8')]
            )
