# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import sys
from pathlib import Path
import logging

_logger = logging.getLogger(__name__)

# 嘗試載入路由器控制模組
try:
    project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    router_module_path = project_root / 'router_full_control.py'
    if router_module_path.exists():
        sys.path.insert(0, str(project_root))
        from router_full_control import RouterFullControl
        ROUTER_CONTROL_AVAILABLE = True
    else:
        ROUTER_CONTROL_AVAILABLE = False
except Exception:
    ROUTER_CONTROL_AVAILABLE = False


class RouterPortForwarding(models.Model):
    _name = 'router.port.forwarding'
    _description = '路由器端口轉發規則'
    _rec_name = 'name'

    name = fields.Char('規則名稱', required=True)
    router_id = fields.Many2one('router.router', '路由器', required=True, ondelete='cascade')
    external_port = fields.Integer('外部端口', required=True)
    internal_ip = fields.Char('內部 IP', required=True)
    internal_port = fields.Integer('內部端口', required=True)
    
    protocol = fields.Selection([
        ('TCP', 'TCP'),
        ('UDP', 'UDP'),
        ('BOTH', 'TCP/UDP')
    ], '協議', default='TCP', required=True)
    
    enabled = fields.Boolean('啟用', default=True)
    description = fields.Text('描述')
    
    # 關聯到伺服器身份
    server_identity_id = fields.Many2one(
        'server.identity',
        '伺服器身份',
        help='此規則關聯的伺服器身份'
    )

    def action_apply_to_router(self):
        """將規則應用到路由器"""
        if not ROUTER_CONTROL_AVAILABLE:
            raise UserError("路由器控制模組未載入，無法應用規則")
        
        for record in self:
            try:
                router_control = RouterFullControl(
                    hostname=record.router_id.internal_ip,
                    port=record.router_id.port,
                    username=record.router_id.username,
                    password=record.router_id.password
                )
                
                if router_control.login():
                    result = router_control.add_port_forwarding_rule(
                        external_port=record.external_port,
                        internal_ip=record.internal_ip,
                        internal_port=record.internal_port,
                        protocol=record.protocol,
                        description=record.description or record.name
                    )
                    
                    if result:
                        return {
                            'type': 'ir.actions.client',
                            'tag': 'display_notification',
                            'params': {
                                'title': '應用成功',
                                'message': f'端口轉發規則已應用到路由器',
                                'type': 'success',
                                'sticky': False,
                            }
                        }
                    else:
                        raise UserError("應用規則失敗")
                else:
                    raise UserError("無法登入路由器")
                    
            except Exception as e:
                _logger.error(f"應用端口轉發規則失敗: {e}")
                raise UserError(f"應用失敗: {str(e)}")
