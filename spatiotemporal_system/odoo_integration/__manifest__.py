# -*- coding: utf-8 -*-
{
    'name': '時空系統整合 - AI 小 J 專用',
    'version': '1.0.0',
    'category': 'Tools',
    'summary': '時空系統與 AI 小 J 整合模組',
    'description': """
時空系統整合模組
================

本模組提供：
- 時空系統與 Odoo 整合
- AI 小 J 專用 API 金鑰管理
- 時空能力在 Odoo 中的使用

專用功能：
- AI 小 J 專用無限金鑰配置
- 從 Odoo 系統參數讀取金鑰
- 時空事件管理
- 智能排程建議
    """,
    'author': 'AI 小 J',
    'depends': ['base'],
    'data': [
        'system_params_spatiotemporal.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
