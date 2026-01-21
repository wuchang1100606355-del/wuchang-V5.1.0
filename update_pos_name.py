#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_pos_name.py

更新 POS 名稱

功能：
- 查詢 POS 配置
- 更新 POS 名稱
- 驗證更新結果
"""

import sys
import subprocess
from pathlib import Path

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
    try:
        result = subprocess.run(
            ["docker", "exec", "wuchangv510-db-1", "psql", "-U", "odoo", "-d", database,
             "-c", "SELECT id, name, active, company_id FROM pos_config ORDER BY id;"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            log("無法查詢 POS 配置", "ERROR")
            return None
    except Exception as e:
        log(f"查詢時發生錯誤: {e}", "ERROR")
        return None


def update_pos_name(pos_id: int, new_name: str, database="admin"):
    """更新 POS 名稱"""
    try:
        # 使用 SQL 更新
        sql = f"UPDATE pos_config SET name = '{new_name}' WHERE id = {pos_id};"
        
        result = subprocess.run(
            ["docker", "exec", "wuchangv510-db-1", "psql", "-U", "odoo", "-d", database,
             "-c", sql],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            # 檢查更新結果
            if "UPDATE 1" in result.stdout or "UPDATE" in result.stdout:
                return True, "更新成功"
            else:
                return False, "未找到對應的 POS"
        else:
            return False, f"更新失敗: {result.stderr}"
    
    except Exception as e:
        return False, f"更新時發生錯誤: {e}"


def main():
    """主函數"""
    print("=" * 70)
    print("更新 POS 名稱")
    print("=" * 70)
    print()
    
    # 查詢現有 POS
    print("【現有 POS 系統】")
    print()
    pos_list = query_pos_configs()
    
    if pos_list:
        print(pos_list)
        print()
    
    # 識別需要更新的 POS
    print("=" * 70)
    print("【識別需要更新的 POS】")
    print("=" * 70)
    print()
    
    print("根據查詢結果，以下 POS 可能需要更新：")
    print("  - ID 3: 上品聊國咖啡館重新總店")
    print("  - ID 4: 上品聊國咖啡館重新總店")
    print()
    print("請確認要將哪一個 POS 改為「仁義分店」：")
    print()
    print("選項：")
    print("  1. ID 3 - 上品聊國咖啡館重新總店")
    print("  2. ID 4 - 上品聊國咖啡館重新總店")
    print("  3. 兩個都更新（分別改為不同名稱）")
    print()
    
    try:
        choice = input("請選擇 (1/2/3): ").strip()
        
        if choice == "1":
            pos_id = 3
            new_name = "仁義分店"
        elif choice == "2":
            pos_id = 4
            new_name = "仁義分店"
        elif choice == "3":
            print()
            print("請輸入兩個 POS 的新名稱：")
            name1 = input("ID 3 的新名稱: ").strip() or "仁義分店"
            name2 = input("ID 4 的新名稱: ").strip() or "仁義分店-2"
            
            # 更新兩個
            print()
            log(f"更新 ID 3 為: {name1}", "PROGRESS")
            success1, msg1 = update_pos_name(3, name1)
            if success1:
                log(f"✓ ID 3 更新成功", "OK")
            else:
                log(f"✗ ID 3 更新失敗: {msg1}", "ERROR")
            
            print()
            log(f"更新 ID 4 為: {name2}", "PROGRESS")
            success2, msg2 = update_pos_name(4, name2)
            if success2:
                log(f"✓ ID 4 更新成功", "OK")
            else:
                log(f"✗ ID 4 更新失敗: {msg2}", "ERROR")
            
            # 驗證
            print()
            print("=" * 70)
            print("【驗證更新結果】")
            print("=" * 70)
            print()
            query_pos_configs()
            
            return 0
        else:
            log("無效的選擇", "ERROR")
            return 1
        
        # 更新單一 POS
        print()
        print("=" * 70)
        print("【更新 POS 名稱】")
        print("=" * 70)
        print()
        
        log(f"更新 POS ID {pos_id} 為: {new_name}", "PROGRESS")
        success, message = update_pos_name(pos_id, new_name)
        
        if success:
            log(f"✓ 更新成功", "OK")
        else:
            log(f"✗ 更新失敗: {message}", "ERROR")
            return 1
        
        # 驗證
        print()
        print("=" * 70)
        print("【驗證更新結果】")
        print("=" * 70)
        print()
        query_pos_configs()
        
        return 0
    
    except KeyboardInterrupt:
        print()
        log("已取消", "INFO")
        return 1
    except Exception as e:
        log(f"執行時發生錯誤: {e}", "ERROR")
        return 1


if __name__ == "__main__":
    sys.exit(main())
