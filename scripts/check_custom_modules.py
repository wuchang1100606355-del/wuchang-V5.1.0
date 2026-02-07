#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_custom_modules.py

檢查自訂模組狀態

功能：
- 檢查自訂模組檔案是否存在
- 檢查模組是否在資料庫中註冊
- 提供安裝指引
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent

def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌",
        "PROGRESS": "🔄"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")

def check_custom_modules_in_filesystem():
    """檢查檔案系統中的自訂模組"""
    log("檢查檔案系統中的自訂模組...", "PROGRESS")
    
    addons_dir = BASE_DIR / "wuchang_os" / "addons"
    if not addons_dir.exists():
        log("自訂模組目錄不存在", "ERROR")
        return []
    
    modules = []
    for item in addons_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            manifest_file = item / "__manifest__.py"
            if manifest_file.exists():
                modules.append({
                    "name": item.name,
                    "path": str(item.relative_to(BASE_DIR)),
                    "manifest_exists": True
                })
                log(f"✓ 找到自訂模組: {item.name}", "OK")
    
    return modules

def check_custom_modules_in_database():
    """檢查資料庫中的自訂模組"""
    log("檢查資料庫中的自訂模組...", "PROGRESS")
    
    try:
        # 查找資料庫容器
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=db", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0 or not result.stdout.strip():
            log("未找到資料庫容器", "ERROR")
            return []
        
        db_container = result.stdout.strip().split('\n')[0]
        
        # 查詢自訂模組
        cmd = [
            "docker", "exec", db_container,
            "psql", "-U", "odoo", "-d", "admin",
            "-t", "-c",
            "SELECT name, state FROM ir_module_module WHERE name LIKE 'wuchang%' ORDER BY name;"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            lines = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
            modules = []
            for line in lines:
                parts = line.split('|')
                if len(parts) >= 2:
                    modules.append({
                        "name": parts[0].strip(),
                        "state": parts[1].strip()
                    })
            
            if modules:
                log(f"✓ 在資料庫中找到 {len(modules)} 個自訂模組", "OK")
            else:
                log("⚠️ 資料庫中未找到自訂模組", "WARN")
            
            return modules
        else:
            log(f"查詢失敗: {result.stderr}", "ERROR")
            return []
    
    except Exception as e:
        log(f"檢查資料庫時發生錯誤: {e}", "ERROR")
        return []

def main():
    """主函數"""
    print("=" * 70)
    print("自訂模組檢查")
    print("=" * 70)
    print()
    
    # 檢查檔案系統中的模組
    filesystem_modules = check_custom_modules_in_filesystem()
    
    # 檢查資料庫中的模組
    database_modules = check_custom_modules_in_database()
    
    # 比較
    print()
    log("模組狀態比較:", "INFO")
    print()
    
    filesystem_names = {m["name"] for m in filesystem_modules}
    database_names = {m["name"] for m in database_modules}
    
    print("檔案系統中的模組:")
    for module in filesystem_modules:
        status = "✅ 已註冊" if module["name"] in database_names else "⚠️ 未註冊"
        state = next((m["state"] for m in database_modules if m["name"] == module["name"]), "N/A")
        print(f"  {status} {module['name']} (資料庫狀態: {state})")
    
    print()
    print("資料庫中的自訂模組:")
    if database_modules:
        for module in database_modules:
            print(f"  - {module['name']}: {module['state']}")
    else:
        print("  無")
    
    # 提供建議
    print()
    missing_modules = filesystem_names - database_names
    if missing_modules:
        log("需要註冊的模組:", "WARN")
        for module_name in missing_modules:
            print(f"  - {module_name}")
        print()
        log("解決方法:", "INFO")
        print("  1. 訪問 http://localhost:8069")
        print("  2. 前往：應用程式")
        print("  3. 點擊：更新應用程式清單")
        print("  4. 等待 Odoo 掃描並註冊自訂模組")
        print("  5. 搜尋模組名稱並點擊「安裝」")
        print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
