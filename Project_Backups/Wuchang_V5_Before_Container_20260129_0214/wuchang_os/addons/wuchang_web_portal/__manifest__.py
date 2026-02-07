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
