# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class RouterDevice(models.Model):
    _name = 'router.device'
    _description = '路由器連接設備'
    _rec_name = 'name'

    name = fields.Char('設備名稱', required=True)
    router_id = fields.Many2one('router.router', '路由器', required=True, ondelete='cascade')
    ip_address = fields.Char('IP 地址', required=True)
    mac_address = fields.Char('MAC 地址')
    ipv6_address = fields.Char('IPv6 地址', help='設備的 IPv6 地址')
    
    device_type = fields.Selection([
        ('wired', '有線'),
        ('wireless', '無線'),
        ('unknown', '未知')
    ], '設備類型', default='unknown')
    
    is_server = fields.Boolean('是否為伺服器', default=False)
    
    server_identity = fields.Selection([
        ('identity_1', '身份 1 (server - 有線)'),
        ('identity_2', '身份 2 (server 2 - WiFi)'),
        ('none', '非伺服器')
    ], '伺服器身份', default='none')
    
    status = fields.Selection([
        ('online', '在線'),
        ('offline', '離線')
    ], '狀態', default='offline')
    
    last_seen = fields.Datetime('最後出現時間', default=fields.Datetime.now)
    signal_strength = fields.Integer('訊號強度 (dBm)', help='僅適用於無線設備')
    connected_time = fields.Integer('連接時間 (秒)', help='設備連接總時間')
    
    notes = fields.Text('備註')

    @api.onchange('name')
    def _onchange_name(self):
        """自動識別伺服器身份"""
        if self.name:
            name_lower = self.name.lower()
            # 識別 server 2 或 svrver 2 (WiFi) - 注意路由器可能顯示為 "svrver 2"
            if 'server 2' in name_lower or 'server2' in name_lower or 'svrver 2' in name_lower or 'svrver2' in name_lower:
                self.is_server = True
                self.server_identity = 'identity_2'
                self.device_type = 'wireless'
            # 識別 server (有線) - 排除包含 2 的情況
            elif name_lower == 'server' or (name_lower.startswith('server') and '2' not in name_lower and 'svrver' not in name_lower):
                self.is_server = True
                self.server_identity = 'identity_1'
                self.device_type = 'wired'
    
    @api.onchange('ip_address')
    def _onchange_ip_address(self):
        """根據 IP 自動識別伺服器身份"""
        if self.ip_address == '192.168.50.249':
            self.is_server = True
            self.server_identity = 'identity_1'
            self.device_type = 'wired'
        elif self.ip_address and self.ip_address.startswith('192.168.50.'):
            # 可能是身份 2，需要手動確認
            # 注意：身份 2 目前可能只有 IPv6，需要確認 IPv4
            pass
        elif self.ip_address and 'fe80::cdf9:2266:dc55:bcc6' in self.ip_address:
            # 身份 2 的 IPv6 地址
            self.is_server = True
            self.server_identity = 'identity_2'
            self.device_type = 'wireless'
