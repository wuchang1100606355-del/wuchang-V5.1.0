{
    'name': 'Wuchang Core: 5-Constant Community OS',
    'version': '5.0.0',
    'category': 'Property Management',
    'summary': "The Noah's Ark of Community Resilience - Integrating Smart Life & Benevolent Finance",
    'description': """
五常智慧社區雲 (Wuchang OS)
===========================

🌟 核心價值
私利不凌駕眾利・貢獻即是股權
本系統由 江政隆 先生發起，五常物業規劃顧問股份有限公司 研發，無償授權 新北市 三重區五常社區發展協會 使用。

🏆 感謝與支持
本計畫感謝以下單位的指導與經費補助：
- Google 非營利組織 (Google for Nonprofits)：提供雲端基礎設施支援。
- 新北市政府文化局：一般型補助計畫。
- 信義房屋：社區一家社造徵件計畫。
- 上品聊國咖啡館 (重新總店)：提供百萬開發資金與技術支援。

🚀 功能模組
- 社區管理協力平台：管委會行政。
- 公益商家聯合銷售平台：POS 與外送，仁義店直營回饋。
- 發展基金運作暨公告：財務透明看板。
- 社區許願樹：居民提案，消費額度灌溉。
- 志工隊管理及派遣：專勤隊 A 隊，AI 督導。

⚖️ 治理宣告
- 最高權限負責人：江政隆 (總幹事)。
- 權責來源：奉會員大會決議，經理事會派任並由理事長公告。
- 法律責任：負責人已完成實名認證 (生物特徵/憑證)，並願負所有法律責任。若因刻 意命令造成損失，將負擔損害賠償。
- 爭議解決：以 新北地方法院合規電子公文 為最高命令。
- 緊急接管：收到公文後系統立即停機，並自動移交權限。
""",
    'author': 'Jiang Zhenglong (Jules)',
    'website': 'https://wuchang.community',
    'license': 'AGPL-3',
    'depends': ['base', 'web', 'mail', 'mail_bot', 'website', 'point_of_sale'],
    'data': [
        'security/security.xml',
        # 'security/ir.model.access.csv',

        'views/wuchang_menus.xml',
        'views/task_views.xml',
        'views/order_views.xml',
        'views/homepage_template.xml',
        'views/sister_control_views.xml',
        'views/settings_views.xml',
        'views/pos_expense_views.xml',
        'views/ai_prompt_views.xml',
        'views/ai_agent_views.xml',
        'views/finance_views.xml',
        'views/report_views.xml',
        'views/webauthn_login.xml',
        'views/knowledge_templates.xml',
        'views/infrastructure_views.xml',
        'views/device_control_views.xml',
        'views/system_tools_views.xml',
        'views/ai_memory_views.xml',
        'views/service_dashboard.xml',
        'views/property_views.xml',

        'data/breakfast_pos_menu.xml',
        'data/google_credentials.xml',
        'data/ai_memory_init.xml',
        'data/ai_cron.xml',
        'data/sustainability_data.xml',
        'views/client_actions.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'wuchang_core/static/src/js/pos_extension.js',
            'wuchang_core/static/src/js/community_super_app.jsx',
            'wuchang_core/static/src/js/community_super_app_mount.js',
            'wuchang_core/static/src/js/background_service.js',
            'wuchang_core/static/src/xml/delivery_interfaces.xml',
        ],
    },
    'installable': True,
    'application': True,
}

