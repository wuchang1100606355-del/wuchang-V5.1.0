#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""建立 POS 產品分類"""
import xmlrpc.client

ODOO_URL = 'http://localhost:8069'
ODOO_DB = 'admin'
ODOO_USERNAME = 'admin'
ODOO_PASSWORD = 'admin'

categories = [
    '義式咖啡',
    '無咖啡因',
    '茶',
    '聊國簡餐',
    '手沖咖啡'
]

try:
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})

    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    print("建立 POS 分類")
    print("=" * 60)

    for cat_name in categories:
        cat_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'pos.category', 'create',
            [{'name': cat_name}]
        )
        print(f"✓ {cat_name} (ID: {cat_id})")

    print("=" * 60)
    print(f"✓ 全部 {len(categories)} 個分類已建立")

except Exception as e:
    print(f"✗ 錯誤: {e}")
