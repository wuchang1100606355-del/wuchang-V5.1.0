# -*- coding: utf-8 -*-
{
    'name': 'Wuchang Credits Management',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'summary': '雙J協作機制 - Google Cloud 抵免額管理',
    'description': """
雙J協作機制 - 抵免額管理模組
============================

功能：
- 管理 Google Cloud 抵免額
- 雙J協作配置（小J + Jules）
- 自動化抵免額應用
- 使用量監控和報告
    """,
    'author': '五常非營利組織',
    'website': 'https://wuchang.life',
    'depends': [
        'base',
        'mail',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/credits_management_views.xml',
        'views/menu_items.xml',
        'data/double_j_collaboration_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
