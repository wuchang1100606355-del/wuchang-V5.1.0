#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""檢查目前 Odoo POS 類別"""
import xmlrpc.client

ODOO_URL = 'http://localhost:8069'
ODOO_DB = 'admin'
ODOO_USERNAME = 'admin'
ODOO_PASSWORD = 'admin'

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

cats = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'pos.category', 'search_read',
    [[]],
    {'fields': ['name']}
)

print('目前 Odoo POS 類別：')
for c in sorted(cats, key=lambda x: x['name']):
    print(f'  - {c["name"]}')
print(f'\n共 {len(cats)} 個類別')
