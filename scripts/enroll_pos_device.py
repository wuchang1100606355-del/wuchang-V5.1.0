#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
納管 POS 設備 (192.168.50.88)
"""

import sys
import os

# 添加 Odoo 路徑
sys.path.insert(0, '/usr/lib/python3/dist-packages')

try:
    import odoo
    from odoo import api, SUPERUSER_ID
    import logging
    from datetime import datetime
    logging.getLogger('odoo').setLevel(logging.ERROR)
except ImportError:
    print("需要在 Odoo 容器內執行此腳本")
    sys.exit(1)

TARGET_IP = "192.168.50.88"
DEVICE_NAME = "POS-PC.wuchang.life"
MAC_ADDRESS = "C6-FD-8D-1A-63-D0"

def main():
    print("=" * 80)
    print(f"  納管設備 {TARGET_IP} (POS-PC)")
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
            
            # 1. 檢查設備是否已存在
            print(f"[1/3] 檢查設備是否已納管...")
            existing_devices = env['wuchang.infrastructure.device'].search([
                ('ip_address', '=', TARGET_IP)
            ])
            
            if existing_devices:
                device = existing_devices[0]
                print(f"  ✓ 設備已存在: {device.name} (ID: {device.id})")
                print(f"    當前狀態: {device.status}")
                print(f"    設備類型: {device.device_type}")
            else:
                # 2. 創建設備記錄
                print(f"[2/3] 創建設備記錄...")
                device = env['wuchang.infrastructure.device'].create({
                    'name': DEVICE_NAME,
                    'ip_address': TARGET_IP,
                    'mac_address': MAC_ADDRESS,
                    'device_type': 'pos',
                    'status': 'online',
                    'last_seen': datetime.now(),
                    'note': f'POS 系統電腦，納管時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
                })
                print(f"  ✓ 設備已創建: {device.name} (ID: {device.id})")
            print()
            
            # 3. 查找並應用適用的控制方案
            print(f"[3/3] 查找適用的控制方案...")
            
            # 查找適用的方案（POS 類型或 all）
            suitable_plans = env['wuchang.device.control.plan'].search([
                ('status', '=', 'active'),
                '|',
                ('device_type', '=', 'pos'),
                ('device_type', '=', 'all')
            ])
            
            if suitable_plans:
                print(f"  ✓ 找到 {len(suitable_plans)} 個適用方案:")
                for plan in suitable_plans:
                    print(f"\n    方案: {plan.name}")
                    print(f"    類型: {plan.plan_type}")
                    print(f"    優先級: {plan.priority}")
                    
                    # 檢查設備是否已在方案中
                    if device.id not in plan.device_ids.ids:
                        print(f"    → 將設備添加到方案中...")
                        plan.write({'device_ids': [(4, device.id)]})
                        print(f"    ✓ 設備已添加到方案")
                    else:
                        print(f"    ✓ 設備已在方案中")
            else:
                print(f"  ⚠ 未找到適用的控制方案")
                print(f"  建議: 創建 POS 設備專用的控制方案")
            
            print()
            
            # 4. 總結
            print("=" * 80)
            print("  納管結果")
            print("=" * 80)
            print()
            print(f"設備信息:")
            print(f"  • 名稱: {device.name}")
            print(f"  • IP: {device.ip_address}")
            print(f"  • 類型: {device.device_type}")
            print(f"  • 狀態: {device.status}")
            print(f"  • 最後連接: {device.last_seen}")
            print()
            print(f"關聯的控制方案: {len([p for p in suitable_plans if device.id in p.device_ids.ids])}")
            print()
            
            cr.commit()
            print("✓ 納管完成並已保存")
            
    except Exception as e:
        print(f"✗ 納管錯誤: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
