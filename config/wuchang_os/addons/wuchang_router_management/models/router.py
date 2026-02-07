# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import sys
from pathlib import Path
import logging

_logger = logging.getLogger(__name__)

# 添加專案根目錄到路徑（如果路由器模組在專案根目錄）
try:
    project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    router_module_path = project_root / 'router_integration.py'
    if router_module_path.exists():
        sys.path.insert(0, str(project_root))
        from router_integration import RouterIntegration
        from router_full_control import RouterFullControl
        ROUTER_MODULES_AVAILABLE = True
    else:
        ROUTER_MODULES_AVAILABLE = False
        _logger.warning("路由器模組未找到，部分功能將無法使用")
except Exception as e:
    ROUTER_MODULES_AVAILABLE = False
    _logger.warning(f"無法載入路由器模組: {e}")


class Router(models.Model):
    _name = 'router.router'
    _description = '路由器管理'
    _rec_name = 'name'

    name = fields.Char('路由器名稱', required=True, default='ASUS RT-BE86U')
    model = fields.Char('型號', default='ASUS RT-BE86U')
    internal_ip = fields.Char('內部 IP', required=True, default='192.168.50.84')
    external_ip = fields.Char('外部 IP', default='220.135.21.74')
    ddns_hostname = fields.Char('DDNS 主機名稱', default='coffeeLofe.asuscomm.com')
    port = fields.Integer('管理端口', default=8443)
    username = fields.Char('用戶名')
    password = fields.Char('密碼', password=True)
    
    status = fields.Selection([
        ('online', '在線'),
        ('offline', '離線'),
        ('unknown', '未知')
    ], '狀態', default='unknown', readonly=True)
    
    last_check = fields.Datetime('最後檢查時間', readonly=True)
    connected_devices_count = fields.Integer('連接設備數', compute='_compute_devices_count', store=True)
    device_ids = fields.One2many('router.device', 'router_id', '連接設備')
    port_forwarding_ids = fields.One2many('router.port.forwarding', 'router_id', '端口轉發規則')
    
    # 系統資訊
    firmware_version = fields.Char('韌體版本', readonly=True)
    uptime = fields.Char('運行時間', readonly=True)
    cpu_usage = fields.Float('CPU 使用率 (%)', readonly=True)
    memory_usage = fields.Float('記憶體使用率 (%)', readonly=True)
    
    # 網路資訊
    wan_ip = fields.Char('WAN IP', readonly=True)
    wan_status = fields.Selection([
        ('connected', '已連接'),
        ('disconnected', '未連接'),
        ('unknown', '未知')
    ], 'WAN 狀態', readonly=True, default='unknown')
    
    notes = fields.Text('備註')

    @api.depends('device_ids')
    def _compute_devices_count(self):
        for record in self:
            record.connected_devices_count = len(record.device_ids)

    def action_sync_devices(self):
        """從路由器同步設備列表"""
        if not ROUTER_MODULES_AVAILABLE:
            raise UserError("路由器模組未載入，無法同步設備")
        
        for record in self:
            try:
                router_api = RouterIntegration(
                    hostname=record.internal_ip,
                    port=record.port,
                    username=record.username,
                    password=record.password
                )
                
                if router_api.login():
                    devices_info = router_api.get_connected_devices()
                    devices = devices_info.get('devices', [])
                    
                    # 清除舊設備
                    record.device_ids.unlink()
                    
                    # 建立新設備記錄
                    for device_data in devices:
                        self.env['router.device'].create({
                            'name': device_data.get('name', '未知設備'),
                            'router_id': record.id,
                            'ip_address': device_data.get('ip', ''),
                            'mac_address': device_data.get('mac', ''),
                            'device_type': 'wireless' if device_data.get('type') == 'wireless' else 'wired',
                            'status': 'online',
                        })
                    
                    record.status = 'online'
                    record.last_check = fields.Datetime.now()
                    
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': '同步成功',
                            'message': f'已同步 {len(devices)} 個設備',
                            'type': 'success',
                            'sticky': False,
                        }
                    }
                else:
                    record.status = 'offline'
                    raise UserError("無法登入路由器，請檢查認證資訊")
                    
            except Exception as e:
                _logger.error(f"同步設備失敗: {e}")
                raise UserError(f"同步設備失敗: {str(e)}")

    def action_check_status(self):
        """檢查路由器狀態"""
        if not ROUTER_MODULES_AVAILABLE:
            raise UserError("路由器模組未載入，無法檢查狀態")
        
        for record in self:
            try:
                router_api = RouterIntegration(
                    hostname=record.internal_ip,
                    port=record.port,
                    username=record.username,
                    password=record.password
                )
                
                if router_api.login():
                    status = router_api.get_router_status()
                    
                    record.status = 'online'
                    record.last_check = fields.Datetime.now()
                    
                    if status:
                        record.firmware_version = status.get('firmware_version', '')
                        record.uptime = status.get('uptime', '')
                        record.wan_ip = status.get('wan_ip', '')
                        record.wan_status = 'connected' if status.get('wan_connected') else 'disconnected'
                    
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': '狀態檢查完成',
                            'message': '路由器狀態正常',
                            'type': 'success',
                            'sticky': False,
                        }
                    }
                else:
                    record.status = 'offline'
                    raise UserError("無法連接到路由器")
                    
            except Exception as e:
                _logger.error(f"檢查狀態失敗: {e}")
                record.status = 'offline'
                raise UserError(f"檢查狀態失敗: {str(e)}")

    def action_sync_port_forwarding(self):
        """同步端口轉發規則"""
        if not ROUTER_MODULES_AVAILABLE:
            raise UserError("路由器模組未載入，無法同步端口轉發規則")
        
        for record in self:
            try:
                router_control = RouterFullControl(
                    hostname=record.internal_ip,
                    port=record.port,
                    username=record.username,
                    password=record.password
                )
                
                if router_control.login():
                    rules = router_control.get_port_forwarding_rules()
                    
                    # 清除舊規則
                    record.port_forwarding_ids.unlink()
                    
                    # 建立新規則
                    for rule_data in rules:
                        self.env['router.port.forwarding'].create({
                            'name': rule_data.get('description', '端口轉發規則'),
                            'router_id': record.id,
                            'external_port': rule_data.get('external_port', 0),
                            'internal_ip': rule_data.get('internal_ip', ''),
                            'internal_port': rule_data.get('internal_port', 0),
                            'protocol': rule_data.get('protocol', 'TCP'),
                            'enabled': rule_data.get('enabled', True),
                            'description': rule_data.get('description', ''),
                        })
                    
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': '同步成功',
                            'message': f'已同步 {len(rules)} 條端口轉發規則',
                            'type': 'success',
                            'sticky': False,
                        }
                    }
                else:
                    raise UserError("無法登入路由器")
                    
            except Exception as e:
                _logger.error(f"同步端口轉發規則失敗: {e}")
                raise UserError(f"同步失敗: {str(e)}")
