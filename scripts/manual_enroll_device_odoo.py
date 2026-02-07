#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手動納管設備到 Odoo 資料庫
用途：當 Odoo API 無法訪問時，直接操作資料庫納管設備
"""

import sys
import os
import psycopg2
from datetime import datetime

# 資料庫連接設定（根據實際環境調整）
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'odoo',  # 根據實際資料庫名稱調整
    'user': 'odoo',      # 根據實際用戶名調整
    'password': 'odoo'   # 根據實際密碼調整
}

def manual_enroll_device():
    """手動納管設備到 Odoo"""
    
    device_info = {
        'name': 'v3_mix_edla_gl',
        'ip_address': '192.168.50.86',
        'mac_address': '',  # 可選
        'device_type': 'pos',
        'os_version': 'Android 13',
        'port': 41895,
        'developer_mode': True,
        'debug_options': {
            'usb': True,
            'gpu': True,
            'wifi': True
        }
    }
    
    print("=" * 60)
    print("  手動納管設備到 Odoo 資料庫")
    print("=" * 60)
    print()
    print("設備資訊:")
    print(f"  名稱: {device_info['name']}")
    print(f"  IP 地址: {device_info['ip_address']}")
    print(f"  通訊埠: {device_info['port']}")
    print(f"  設備類型: {device_info['device_type']}")
    print()
    
    try:
        # 連接資料庫
        print("正在連接資料庫...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 檢查設備是否已存在
        cur.execute("""
            SELECT id, name, ip_address, status 
            FROM wuchang_infrastructure_device 
            WHERE ip_address = %s OR name = %s
        """, (device_info['ip_address'], device_info['name']))
        
        existing = cur.fetchone()
        
        if existing:
            # 更新現有設備
            device_id = existing[0]
            cur.execute("""
                UPDATE wuchang_infrastructure_device 
                SET 
                    name = %s,
                    ip_address = %s,
                    mac_address = %s,
                    device_type = %s,
                    status = 'online',
                    last_seen = %s,
                    note = %s
                WHERE id = %s
            """, (
                device_info['name'],
                device_info['ip_address'],
                device_info.get('mac_address', ''),
                device_info['device_type'],
                datetime.now(),
                f"Android {device_info['os_version']} POS 設備，IP: {device_info['ip_address']}:{device_info['port']}，開發者模式: 已開啟，USB/GPU/WiFi 偵錯: 已開啟，手動納管時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                device_id
            ))
            action = 'updated'
            print(f"✓ 設備已更新 (ID: {device_id})")
        else:
            # 創建新設備
            cur.execute("""
                INSERT INTO wuchang_infrastructure_device 
                (name, ip_address, mac_address, device_type, status, last_seen, note, create_date, write_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                device_info['name'],
                device_info['ip_address'],
                device_info.get('mac_address', ''),
                device_info['device_type'],
                'online',
                datetime.now(),
                f"Android {device_info['os_version']} POS 設備，IP: {device_info['ip_address']}:{device_info['port']}，開發者模式: 已開啟，USB/GPU/WiFi 偵錯: 已開啟，手動納管時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                datetime.now(),
                datetime.now()
            ))
            device_id = cur.fetchone()[0]
            action = 'enrolled'
            print(f"✓ 設備已納管 (ID: {device_id})")
        
        # 提交變更
        conn.commit()
        cur.close()
        conn.close()
        
        print()
        print("=" * 60)
        print(f"  納管{'更新' if action == 'updated' else '完成'}")
        print("=" * 60)
        print()
        print("下一步：")
        print("  1. 啟動 Odoo 服務後，在 Odoo 中確認設備記錄")
        print("  2. 在 Google Workspace Admin Console 註冊設備")
        print("  3. 設定 Kiosk 模式和應用程式政策")
        print()
        
        return 0
        
    except psycopg2.OperationalError as e:
        print(f"❌ 資料庫連接失敗: {e}")
        print()
        print("請確認：")
        print("  1. PostgreSQL 服務正在運行")
        print("  2. 資料庫連接設定正確")
        print("  3. 用戶權限足夠")
        return 1
    except Exception as e:
        print(f"❌ 納管失敗: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(manual_enroll_device())
