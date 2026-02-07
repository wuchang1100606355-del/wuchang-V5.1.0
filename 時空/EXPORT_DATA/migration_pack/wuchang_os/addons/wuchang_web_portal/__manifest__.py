# -*- coding: utf-8 -*-
{
    'name': "五常社區入口網 (Wuchang Web Portal)",
    'summary': "基於 Odoo Website 的現代化入口首頁",
    'version': '1.0.0',
    'category': 'Website',
    'author': "江政隆",
    'depends': [
        'base', 'website', 'wuchang_core'
    ],
    'data': [
        'views/portal_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'wuchang_web_portal/static/src/css/portal.css',
            'wuchang_web_portal/static/src/js/portal.js',
        ],
    },
    'application': True,
}


---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:23:50
---
