#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_pos_systems.py

檢查系統中的 POS（銷售點）系統數量

功能：
- 查詢所有 POS 配置
- 統計 POS 數量
- 顯示 POS 詳細資訊
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")


def query_pos_configs(database="admin"):
    """查詢 POS 配置"""
    print("=" * 70)
    print("檢查 POS（銷售點）系統")
    print("=" * 70)
    print()
    
    # 查詢 POS 數量
    try:
        result = subprocess.run(
            ["docker", "exec", "wuchangv510-db-1", "psql", "-U", "odoo", "-d", database,
             "-c", "SELECT COUNT(*) as pos_count FROM pos_config;"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            # 解析結果
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'pos_count' in line or line.strip().isdigit():
                    count = int(line.strip()) if line.strip().isdigit() else None
                    if count is not None:
                        log(f"POS 系統總數: {count}", "OK")
                        print()
                        break
        else:
            log("無法查詢 POS 數量", "ERROR")
            return None
    except Exception as e:
        log(f"查詢 POS 數量時發生錯誤: {e}", "ERROR")
        return None
    
    # 查詢詳細資訊
    print("【POS 系統詳細資訊】")
    print()
    
    try:
        result = subprocess.run(
            ["docker", "exec", "wuchangv510-db-1", "psql", "-U", "odoo", "-d", database,
             "-c", "SELECT id, name, active, company_id FROM pos_config ORDER BY id;"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(result.stdout)
            
            # 解析結果
            lines = result.stdout.strip().split('\n')
            pos_list = []
            
            # 跳過標題行
            data_started = False
            for line in lines:
                if '----' in line:
                    data_started = True
                    continue
                if data_started and line.strip():
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 3:
                        pos_list.append({
                            'id': parts[0],
                            'name': parts[1],
                            'active': parts[2] if len(parts) > 2 else 'N/A',
                            'company_id': parts[3] if len(parts) > 3 else 'N/A'
                        })
            
            return pos_list
        else:
            log("無法查詢 POS 詳細資訊", "ERROR")
            return None
    except Exception as e:
        log(f"查詢 POS 詳細資訊時發生錯誤: {e}", "ERROR")
        return None


def check_pos_sessions(database="admin"):
    """檢查 POS 會話"""
    print()
    print("=" * 70)
    print("【檢查 POS 會話】")
    print("=" * 70)
    print()
    
    try:
        result = subprocess.run(
            ["docker", "exec", "wuchangv510-db-1", "psql", "-U", "odoo", "-d", database,
             "-c", "SELECT COUNT(*) as session_count, COUNT(*) FILTER (WHERE state='opened') as open_sessions FROM pos_session;"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            log("無法查詢 POS 會話", "WARN")
    except Exception as e:
        log(f"查詢 POS 會話時發生錯誤: {e}", "WARN")


def check_pos_orders(database="admin"):
    """檢查 POS 訂單"""
    print()
    print("=" * 70)
    print("【檢查 POS 訂單統計】")
    print("=" * 70)
    print()
    
    try:
        result = subprocess.run(
            ["docker", "exec", "wuchangv510-db-1", "psql", "-U", "odoo", "-d", database,
             "-c", "SELECT COUNT(*) as total_orders, COUNT(DISTINCT pos_config_id) as pos_with_orders FROM pos_order;"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            log("無法查詢 POS 訂單", "WARN")
    except Exception as e:
        log(f"查詢 POS 訂單時發生錯誤: {e}", "WARN")


def generate_report(pos_list):
    """產生報告"""
    print()
    print("=" * 70)
    print("【POS 系統報告】")
    print("=" * 70)
    print()
    
    if pos_list:
        print(f"POS 系統總數: {len(pos_list)}")
        print()
        
        active_count = sum(1 for pos in pos_list if pos.get('active') == 't' or pos.get('active') == 'True')
        
        print(f"啟用的 POS: {active_count}")
        print(f"停用的 POS: {len(pos_list) - active_count}")
        print()
        
        print("【POS 系統列表】")
        for i, pos in enumerate(pos_list, 1):
            status = "✅" if (pos.get('active') == 't' or pos.get('active') == 'True') else "❌"
            print(f"{i}. {status} {pos.get('name', 'N/A')} (ID: {pos.get('id', 'N/A')})")
            print(f"   啟用狀態: {pos.get('active', 'N/A')}")
            print(f"   公司 ID: {pos.get('company_id', 'N/A')}")
            print()
    else:
        log("未找到 POS 系統", "WARN")
        print()
        print("可能原因：")
        print("  1. POS 模組尚未安裝")
        print("  2. 尚未建立 POS 配置")
        print("  3. 資料庫不同")
        print()
        print("建議：")
        print("  1. 檢查 Odoo 模組：應用程式 > 搜尋 'point_of_sale'")
        print("  2. 安裝 POS 模組")
        print("  3. 前往：銷售點 > 配置 > 銷售點")


def main():
    """主函數"""
    print("=" * 70)
    print("POS（銷售點）系統檢查")
    print("=" * 70)
    print()
    
    # 檢查多個資料庫
    databases = ["admin", "odoo"]
    
    all_pos = []
    
    for db in databases:
        print(f"【檢查資料庫: {db}】")
        print()
        
        pos_list = query_pos_configs(db)
        
        if pos_list:
            all_pos.extend(pos_list)
            check_pos_sessions(db)
            check_pos_orders(db)
        else:
            log(f"資料庫 {db} 中未找到 POS 配置或查詢失敗", "WARN")
        
        print()
    
    # 產生總報告
    if all_pos:
        print("=" * 70)
        print("【總報告】")
        print("=" * 70)
        generate_report(all_pos)
        
        # 儲存報告
        report_file = BASE_DIR / "pos_systems_report.json"
        try:
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "total_pos": len(all_pos),
                "pos_list": all_pos
            }
            report_file.write_text(
                json.dumps(report_data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            log(f"報告已儲存: {report_file}", "OK")
        except Exception as e:
            log(f"儲存報告失敗: {e}", "WARN")
    else:
        log("所有資料庫中都沒有找到 POS 系統", "WARN")
        print()
        print("建議：")
        print("  1. 確認 POS 模組已安裝")
        print("  2. 通過 Odoo 網頁介面建立 POS 配置")
        print("  3. 訪問: http://localhost:8069")
        print("  4. 前往: 銷售點 > 配置 > 銷售點")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
