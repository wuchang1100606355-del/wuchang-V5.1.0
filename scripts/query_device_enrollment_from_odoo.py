#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 Odoo 查詢設備納管狀態和方案
"""

import sys
import os
import xmlrpc.client
from datetime import datetime

# Odoo 連接配置
ODOO_URL = "http://localhost:8069"
ODOO_DB = "admin"  # 根據實際數據庫名稱修改
ODOO_USERNAME = "admin"
ODOO_PASSWORD = "admin"  # 根據實際密碼修改

TARGET_IP = "192.168.50.88"

def connect_odoo():
    """連接到 Odoo"""
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        
        if not uid:
            print("✗ Odoo 認證失敗")
            return None, None
        
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        return uid, models
    except Exception as e:
        print(f"✗ 無法連接到 Odoo: {e}")
        return None, None

def query_device(uid, models, ip_address):
    """查詢設備"""
    try:
        # 查詢基礎設施設備
        device_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'wuchang.infrastructure.device', 'search_read',
            [[('ip_address', '=', ip_address)]],
            {'fields': ['id', 'name', 'ip_address', 'mac_address', 'device_type', 'status', 'last_seen', 'note']}
        )
        
        return device_ids
    except Exception as e:
        print(f"  ⚠ 查詢設備時出錯: {e}")
        return []

def query_control_plans(uid, models, device_type=None):
    """查詢長期控制方案"""
    try:
        domain = [('status', '=', 'active')]
        if device_type:
            domain.append(('device_type', 'in', [device_type, 'all']))
        
        plan_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'wuchang.device.control.plan', 'search_read',
            [domain],
            {'fields': ['id', 'name', 'plan_type', 'device_type', 'priority', 'control_strategy', 'enrollment_method', 'monitor_enabled', 'device_count']}
        )
        
        return plan_ids
    except Exception as e:
        print(f"  ⚠ 查詢控制方案時出錯: {e}")
        return []

def main():
    print("=" * 80)
    print(f"  從 Odoo 查詢設備 {TARGET_IP} 的納管狀態和方案")
    print("=" * 80)
    print()
    
    # 連接 Odoo
    print("連接 Odoo...")
    uid, models = connect_odoo()
    if not uid:
        print("無法連接到 Odoo，將使用本地偵測結果")
        return 1
    
    print(f"✓ 已連接到 Odoo (UID: {uid})")
    print()
    
    # 查詢設備
    print(f"[1/3] 查詢設備 {TARGET_IP}...")
    devices = query_device(uid, models, TARGET_IP)
    
    if devices:
        print(f"  ✓ 找到 {len(devices)} 個設備記錄:")
        for device in devices:
            print(f"\n    設備 ID: {device.get('id')}")
            print(f"    設備名稱: {device.get('name')}")
            print(f"    IP 地址: {device.get('ip_address')}")
            print(f"    MAC 地址: {device.get('mac_address')}")
            print(f"    設備類型: {device.get('device_type')}")
            print(f"    狀態: {device.get('status')}")
            print(f"    最後連接: {device.get('last_seen')}")
            device_type = device.get('device_type')
    else:
        print(f"  ⚠ 未找到設備記錄，設備可能尚未納管")
        device_type = None
    print()
    
    # 查詢適用的控制方案
    print(f"[2/3] 查詢適用的長期控制方案...")
    plans = query_control_plans(uid, models, device_type)
    
    if plans:
        print(f"  ✓ 找到 {len(plans)} 個適用方案:")
        for i, plan in enumerate(plans, 1):
            print(f"\n  方案 {i}: {plan.get('name')}")
            print(f"    方案 ID: {plan.get('id')}")
            print(f"    方案類型: {plan.get('plan_type')}")
            print(f"    設備類型: {plan.get('device_type')}")
            print(f"    優先級: {plan.get('priority')}")
            print(f"    控制策略: {plan.get('control_strategy')}")
            print(f"    納管方式: {plan.get('enrollment_method')}")
            print(f"    監控啟用: {plan.get('monitor_enabled')}")
            print(f"    關聯設備數: {plan.get('device_count')}")
    else:
        print(f"  ⚠ 未找到適用的長期控制方案")
    print()
    
    # 生成建議
    print("[3/3] 生成建議...")
    recommendations = []
    
    if not devices:
        recommendations.append({
            'action': 'enroll',
            'message': f'設備 {TARGET_IP} 尚未納管，建議執行納管操作',
            'method': 'POST /api/device/enroll/chrome_os' if device_type == 'chrome_os' else '創建設備記錄'
        })
    
    if device_type == 'chrome_os' and plans:
        chrome_plan = next((p for p in plans if p.get('device_type') == 'chrome_os'), None)
        if chrome_plan:
            recommendations.append({
                'action': 'apply_plan',
                'message': f'建議應用方案: {chrome_plan.get("name")}',
                'plan_id': chrome_plan.get('id'),
                'plan_name': chrome_plan.get('name')
            })
    
    if recommendations:
        print("  建議操作:")
        for rec in recommendations:
            print(f"    • {rec['message']}")
            if 'plan_id' in rec:
                print(f"      方案 ID: {rec['plan_id']}")
                print(f"      方案名稱: {rec['plan_name']}")
    
    print()
    print("=" * 80)
    print("  查詢完成")
    print("=" * 80)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
