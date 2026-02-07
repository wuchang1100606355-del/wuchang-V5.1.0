# -*- coding: utf-8 -*-
{
    'name': '五常路由器管理',
    'version': '17.0.1.0.0',
    'category': 'Infrastructure',
    'summary': '路由器資產管理、連接設備管理、網路配置管理',
    'description': """
五常路由器管理模組
==================

功能：
- 路由器資產管理（ASUS RT-BE86U）
- 連接設備列表和狀態追蹤
- 端口轉發規則管理
- DDNS 設定管理
- 伺服器雙身份管理（有線/WiFi）
- 網路流量監控

整合：
- router_integration.py
- router_full_control.py
- property_management_router_integration.py
    """,
    'author': '五常社區發展協會',
    'website': 'https://wuchang.life',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/router_security.xml',
        'views/router_views.xml',
        'views/router_device_views.xml',
        'views/router_port_forwarding_views.xml',
        'views/server_identity_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
