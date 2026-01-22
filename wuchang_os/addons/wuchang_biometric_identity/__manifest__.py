# -*- coding: utf-8 -*-
{
    'name': '五常生物辨識身份管理',
    'version': '17.0.1.0.0',
    'category': 'Security',
    'summary': '個人身份管理、生物辨識資料記錄、階段三權限認證',
    'description': """
五常生物辨識身份管理模組
==================

功能：
- 個人身份管理（系統創辦人、可究責對象）
- 生物辨識資料記錄（人臉識別、指紋等）
- 生物辨識驗證歷史記錄
- 階段三權限認證整合
- MAC 地址驗證記錄

用途：
- 階段三權限認證（生物特徵辨認）
- 可究責對象身份驗證
- 個人身份綁定記錄
    """,
    'author': '五常社區發展協會',
    'website': 'https://wuchang.life',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/biometric_security.xml',
        'views/biometric_identity_views.xml',
        'views/biometric_verification_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
