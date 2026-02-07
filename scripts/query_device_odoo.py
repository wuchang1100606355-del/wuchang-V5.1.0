#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 Odoo 查詢設備納管狀態
"""

import sys
import os

# 添加 Odoo 路徑（如果在容器內）
sys.path.insert(0, '/usr/lib/python3/dist-packages')

try:
    import odoo
    from odoo import api, SUPERUSER_ID
    import logging
    logging.getLogger('odoo').setLevel(logging.ERROR)
except ImportError:
    print("需要在 Odoo 容器內執行此腳本")
    sys.exit(1)

TARGET_IP = "192.168.50.88"

def main():
    print("=" * 80)
    print(f"  從 Odoo 查詢設備 {TARGET_IP} 的納管狀態和方案")
    print("=" * 80)
    print()
    
    try:
        # 初始化 Odoo
        odoo.tools.config.parse_config([])
        db_name = odoo.tools.config.get('db_name', 'admin')
        registry = odoo.registry(db_name)
        
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            
            print(f"已連接到數據庫: {db_name}")
            print()
            
            # 1. 查詢設備
            print(f"[1/3] 查詢設備 {TARGET_IP}...")
            devices = env['wuchang.infrastructure.device'].search([
                ('ip_address', '=', TARGET_IP)
            ])
            
            if devices:
                print(f"  ✓ 找到 {len(devices)} 個設備記錄:")
                for device in devices:
                    print(f"\n    設備 ID: {device.id}")
                    print(f"    設備名稱: {device.name}")
                    print(f"    IP 地址: {device.ip_address}")
                    print(f"    MAC 地址: {device.mac_address or 'N/A'}")
                    print(f"    設備類型: {device.device_type}")
                    print(f"    狀態: {device.status}")
                    print(f"    最後連接: {device.last_seen or 'N/A'}")
                    device_type = device.device_type
            else:
                print(f"  ⚠ 未找到設備記錄，設備尚未納管")
                device_type = 'pos'  # 根據偵測結果推斷
            print()
            
            # 2. 查詢適用的控制方案
            print(f"[2/3] 查詢適用的長期控制方案...")
            
            # 查詢所有啟用的方案
            all_plans = env['wuchang.device.control.plan'].search([
                ('status', '=', 'active')
            ])
            
            # 查找適用的方案
            suitable_plans = []
            for plan in all_plans:
                if plan.device_type == 'all' or plan.device_type == device_type:
                    suitable_plans.append(plan)
            
            if suitable_plans:
                print(f"  ✓ 找到 {len(suitable_plans)} 個適用方案:")
                for i, plan in enumerate(suitable_plans, 1):
                    print(f"\n  方案 {i}: {plan.name}")
                    print(f"    方案 ID: {plan.id}")
                    print(f"    方案類型: {plan.plan_type}")
                    print(f"    目標設備類型: {plan.device_type}")
                    print(f"    優先級: {plan.priority}")
                    print(f"    控制策略: {plan.control_strategy}")
                    print(f"    納管方式: {plan.enrollment_method}")
                    print(f"    監控啟用: {plan.monitor_enabled}")
                    print(f"    關聯設備數: {plan.device_count}")
            else:
                print(f"  ⚠ 未找到適用的長期控制方案")
            print()
            
            # 3. 檢查設備是否在方案中
            if devices:
                print(f"[3/3] 檢查設備是否在控制方案中...")
                device = devices[0]
                plans_with_device = env['wuchang.device.control.plan'].search([
                    ('device_ids', 'in', [device.id]),
                    ('status', '=', 'active')
                ])
                
                if plans_with_device:
                    print(f"  ✓ 設備已關聯到 {len(plans_with_device)} 個方案:")
                    for plan in plans_with_device:
                        print(f"    • {plan.name} (ID: {plan.id})")
                else:
                    print(f"  ⚠ 設備尚未關聯到任何控制方案")
            else:
                print(f"[3/3] 跳過（設備未納管）")
            print()
            
            # 生成建議
            print("=" * 80)
            print("  建議操作")
            print("=" * 80)
            print()
            
            if not devices:
                print("1. 納管設備:")
                print(f"   • 創建設備記錄: IP {TARGET_IP}, 類型: POS Terminal")
                print(f"   • 或使用 API: POST /api/device/enroll/chrome_os (如果是 Chrome OS)")
                print()
            
            if suitable_plans:
                print("2. 應用控制方案:")
                for plan in suitable_plans:
                    print(f"   • {plan.name} (優先級: {plan.priority})")
                    if not devices:
                        print(f"     - 需要先納管設備，然後將設備添加到方案中")
            print()
            
            cr.commit()
            
    except Exception as e:
        print(f"✗ 查詢錯誤: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
