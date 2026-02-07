#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Import menu items into Odoo POS using English names while keeping Chinese in description."""
import xmlrpc.client
import json
import os
from datetime import datetime

ODOO_URL = 'http://localhost:8069'
ODOO_DB = 'admin'
ODOO_USERNAME = 'admin'
ODOO_PASSWORD = 'admin'

MENU_DATA = {
    '義式咖啡': [
        {'name_zh': '濃縮咖啡', 'name_en': 'Espresso', 'price': 55, 'display': True},
        {'name_zh': '美式咖啡', 'name_en': 'Americano', 'price': 60, 'display': True},
        {'name_zh': '卡布奇諾', 'name_en': 'Cappuccino', 'price': 70, 'display': True},
        {'name_zh': '拿鐵', 'name_en': 'Latte', 'price': 70, 'display': True},
        {'name_zh': '瑪奇朵', 'name_en': 'Macchiato', 'price': 65, 'display': True},
        {'name_zh': '摩卡', 'name_en': 'Mocha', 'price': 75, 'display': True},
    ],
    '無咖啡因': [
        {'name_zh': '熱巧克力', 'name_en': 'Hot Chocolate', 'price': 60, 'display': True},
        {'name_zh': '濃湯', 'name_en': 'Soup', 'price': 50, 'display': True},
        {'name_zh': '熱可可', 'name_en': 'Cocoa', 'price': 55, 'display': True},
    ],
    '茶': [
        {'name_zh': '烏龍茶', 'name_en': 'Oolong Tea', 'price': 45, 'display': True},
        {'name_zh': '綠茶', 'name_en': 'Green Tea', 'price': 45, 'display': True},
        {'name_zh': '奶茶', 'name_en': 'Milk Tea', 'price': 50, 'display': True},
    ],
    '手沖咖啡': [
        {'name_zh': '手沖單品', 'name_en': 'Single Origin Pour Over',
            'price': 90, 'display': True},
        {'name_zh': '手沖混合', 'name_en': 'Blend Pour Over',
            'price': 85, 'display': True},
    ],
    '聊國簡餐': [
        {'name_zh': '吐司', 'name_en': 'Toast', 'price': 40, 'display': True},
        {'name_zh': '三明治', 'name_en': 'Sandwich', 'price': 65, 'display': True},
        {'name_zh': '貝果', 'name_en': 'Bagel', 'price': 55, 'display': True},
        {'name_zh': '馬芬蛋糕', 'name_en': 'Muffin', 'price': 50, 'display': True},
    ],
}

HIDDEN_ITEMS = {}


def import_menu_products():
    print("=" * 80)
    print("Importing menu (English names, Chinese stored in description)")
    print("=" * 80)
    try:
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        if not uid:
            print("✗ login failed")
            return False
        print(f"✓ login uid={uid}")
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

        log = {'ts': datetime.now().isoformat(), 'products': []}

        for cat_name, products in MENU_DATA.items():
            print(f"\n[{cat_name}]")
            cat_ids = models.execute_kw(
                ODOO_DB,
                uid,
                ODOO_PASSWORD,
                'pos.category',
                'search',
                [[['name', '=', cat_name]]],
            )
            if not cat_ids:
                print(f"  ✗ category not found: {cat_name}")
                continue
            cat_id = cat_ids[0]
            print(f"  ✓ category id={cat_id}")

            for p in products:
                if p['name_zh'] in HIDDEN_ITEMS:
                    print(f"  ⊘ skip hidden: {p['name_zh']}")
                    continue
                try:
                    # pos_categ_ids is the m2m field on product.template in Odoo 17
                    product_tmpl_id = models.execute_kw(
                        ODOO_DB,
                        uid,
                        ODOO_PASSWORD,
                        'product.template',
                        'create',
                        [{
                            'name': p['name_en'],
                            'list_price': p['price'],
                            'type': 'product',
                            'pos_categ_ids': [(6, 0, [cat_id])],
                            'available_in_pos': p['display'],
                            'uom_id': 1,
                            'uom_po_id': 1,
                            'description': f"[中文名] {p['name_zh']}",
                        }],
                    )
                    print(
                        f"  ✓ {p['name_en']} ({p['name_zh']}) ${p['price']} -> tmpl {product_tmpl_id}")
                    log['products'].append(
                        {**p, 'tmpl_id': product_tmpl_id, 'category': cat_name, 'category_id': cat_id})
                except xmlrpc.client.Fault as fault:
                    print(f"  ✗ Fault {p['name_en']}: {fault.faultString}")
                except Exception as exc:
                    print(f"  ✗ Error {p['name_en']}: {exc}")

        log_file = r"C:\wuchang V5.1.0\downloads\menu_import_log.json"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
        print("\n" + "=" * 80)
        print(f"Done. products created: {len(log['products'])}")
        print(f"Log: {log_file}")
        print("=" * 80)
        return True
    except Exception as exc:
        print(f"✗ Fatal error: {exc}")
        return False


if __name__ == '__main__':
    import_menu_products()
