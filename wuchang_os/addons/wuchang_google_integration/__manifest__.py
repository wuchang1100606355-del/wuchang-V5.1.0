# -*- coding: utf-8 -*-
{
    'name': '五常 Google Workspace 整合 (Wuchang Google Integration)',
    'summary': 'Google Workspace 深度整合：Google Meet、Google 表單、Google Drive',
    'version': '5.1.0',
    'category': 'Productivity',
    'author': 'Wuchang OS Team',
    'website': 'https://wuchang.community',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
        'calendar',
        'wuchang_core',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/document_templates.xml',
        'views/google_meet_views.xml',
        'views/google_form_views.xml',
        'views/google_drive_views.xml',
        'views/document_template_views.xml',
        'views/google_integration_menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'description': """
五常 Google Workspace 深度整合
==============================

整合 Google 非營利組織提供的免費資源，讓「五常小J智慧五常社區雲系統」具備強大功能。

核心功能：
---------
1. Odoo 會議系統與 Google Meet 整合
   - 自動建立 Google Meet 連結
   - 會議排程同步到 Google Calendar
   - 會議錄影儲存到 Google Drive

2. AI 驅動的公文生成系統（基於 Google 表單）
   - 問答式公文設計
   - AI 自動生成正式公文
   - 多種公文類型支援

3. Google Drive 文件管理
   - 文件自動同步
   - 權限管理
   - 版本控制

資源規格（Google 非營利版）：
----------------------------
- Google Meet：100人/24小時，完全免費
- Google 表單：無限制表單和回應，完全免費
- Google 雲端硬碟：5TB/使用者，完全免費

合規聲明：
---------
✅ 所有功能均符合 Google 非營利組織使用條款
✅ 僅用於非營利目的和社區服務
✅ 完整的使用記錄和監控
    """,
}
