#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
開啟Odoo POS餐廳功能
"""
import xmlrpc.client
import os

# Odoo連線設定
ODOO_URL = os.getenv('ODOO_URL', 'http://localhost:8069')
ODOO_DB = os.getenv('ODOO_DB', 'admin')
ODOO_USERNAME = os.getenv('ODOO_USERNAME', 'admin')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'admin')


def enable_restaurant_mode():
    """啟用POS餐廳模式"""
    print("=" * 80)
    print("開啟POS餐廳功能")
    print("=" * 80)

    try:
        # 連接Odoo
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})

        if not uid:
            print("✗ 登入失敗，請檢查帳號密碼")
            return False

        print(f"✓ 已登入 (User ID: {uid})")

        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

        # 搜尋POS配置
        pos_config_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'pos.config', 'search',
            [[]]
        )

        if not pos_config_ids:
            print("✗ 找不到POS配置")
            return False

        print(f"✓ 找到 {len(pos_config_ids)} 個POS配置")

        # 啟用所有POS的餐廳模式
        for config_id in pos_config_ids:
            # 讀取當前設定
            config = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'pos.config', 'read',
                [config_id], {'fields': ['name', 'module_pos_restaurant']}
            )[0]

            config_name = config['name']
            is_restaurant = config.get('module_pos_restaurant', False)

            if is_restaurant:
                print(f"  ✓ {config_name} - 餐廳模式已啟用")
            else:
                # 啟用餐廳模式
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'pos.config', 'write',
                    [[config_id], {'module_pos_restaurant': True}]
                )
                print(f"  ✓ {config_name} - 已開啟餐廳模式")

        print("\n" + "=" * 80)
        print("✓ POS餐廳功能已全部啟用！")
        print("=" * 80)
        return True

    except Exception as e:
        print(f"\n✗ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = enable_restaurant_mode()
    exit(0 if success else 1)
