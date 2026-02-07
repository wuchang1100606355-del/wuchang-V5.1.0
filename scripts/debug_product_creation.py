#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick check to create a product via XML-RPC and show the raw fault message."""
import xmlrpc.client

ODOO_URL = 'http://localhost:8069'
ODOO_DB = 'admin'
ODOO_USERNAME = 'admin'
ODOO_PASSWORD = 'admin'

try:
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    print(f"login uid={uid}")
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
    product_id = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_PASSWORD,
        'product.product',
        'create',
        [{
            'name': 'Test Product',
            'list_price': 100,
            'type': 'product',
        }],
    )
    print(f"created product id={product_id}")
except xmlrpc.client.Fault as fault:
    print("FAULT:")
    print(fault.faultString)
except Exception as exc:
    print("ERROR:")
    print(exc)
