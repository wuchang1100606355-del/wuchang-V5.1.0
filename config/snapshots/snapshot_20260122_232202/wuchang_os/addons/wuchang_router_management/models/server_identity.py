# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ServerIdentity(models.Model):
    _name = 'server.identity'
    _description = '伺服器身份管理'
    _rec_name = 'name'

    name = fields.Char('身份名稱', required=True)
    
    identity_type = fields.Selection([
        ('wired', '有線網卡'),
        ('wifi', 'WiFi 網卡')
    ], '身份類型', required=True)
    
    ip_address = fields.Char('IP 地址', required=True)
    mac_address = fields.Char('MAC 地址')
    
    device_id = fields.Many2one(
        'router.device',
        '對應設備',
        help='對應的路由器連接設備記錄'
    )
    
    is_primary = fields.Boolean('主要身份', default=False, help='主要身份用於主要服務')
    
    services = fields.Text(
        '服務列表',
        help='此身份提供的服務列表（JSON 格式或文字描述）'
    )
    
    cloudflare_tunnel_config = fields.Text(
        'Cloudflare Tunnel 配置',
        help='此身份在 Cloudflare Tunnel config.yml 中的配置'
    )
    
    notes = fields.Text('備註')
    
    # 預設身份
    @api.model
    def create_default_identities(self):
        """建立預設的兩個伺服器身份"""
        # 身份 1 (server - 有線)
        identity_1 = self.search([('name', '=', 'server')], limit=1)
        if not identity_1:
            identity_1 = self.create({
                'name': 'server',
                'identity_type': 'wired',
                'ip_address': '192.168.50.249',
                'is_primary': True,
                'services': '主要服務：Caddy (80), Odoo (8069), Open WebUI (8080), Portainer (9000), Uptime Kuma (3001)',
            })
        
        # 身份 2 (server 2 - WiFi)
        identity_2 = self.search([('name', '=', 'server 2')], limit=1)
        if not identity_2:
            identity_2 = self.create({
                'name': 'server 2',
                'identity_type': 'wifi',
                'ip_address': '',  # 待確認
                'is_primary': False,
                'services': 'WiFi 網卡服務（待配置）',
            })
        
        return identity_1, identity_2
