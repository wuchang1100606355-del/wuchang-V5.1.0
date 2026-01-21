#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_database_password.py

更新資料庫密碼

功能：
- 更新 docker-compose 檔案中的資料庫密碼
- 提供更新指引
"""

import sys
import re
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


def update_password_in_file(file_path: Path, old_password: str, new_password: str):
    """更新檔案中的密碼"""
    if not file_path.exists():
        return False, "檔案不存在"
    
    try:
        content = file_path.read_text(encoding="utf-8")
        
        # 替換密碼
        pattern = f"POSTGRES_PASSWORD={old_password}"
        replacement = f"POSTGRES_PASSWORD={new_password}"
        
        if pattern in content:
            new_content = content.replace(pattern, replacement)
            file_path.write_text(new_content, encoding="utf-8")
            return True, "密碼已更新"
        else:
            return False, "未找到預設密碼"
    
    except Exception as e:
        return False, f"更新失敗: {str(e)}"


def main():
    """主函數"""
    print("=" * 70)
    print("更新資料庫密碼")
    print("=" * 70)
    print()
    
    # 從 .secrets.json 讀取建議的密碼，或使用輸入
    secrets_file = BASE_DIR / ".secrets.json"
    suggested_password = None
    
    if secrets_file.exists():
        import json
        try:
            secrets_data = json.loads(secrets_file.read_text(encoding="utf-8"))
            # 可以從 secrets 中讀取，但為了安全，還是讓用戶輸入
        except:
            pass
    
    # 讀取建議的密碼（從執行報告）
    print("請輸入新的資料庫密碼：")
    print("（建議使用之前產生的安全密碼）")
    print()
    
    new_password = input("新密碼: ").strip()
    
    if not new_password:
        log("未輸入密碼，取消操作", "WARN")
        return 1
    
    if len(new_password) < 8:
        log("密碼長度不足，建議至少 8 個字元", "WARN")
        response = input("是否繼續？(y/n): ").strip().lower()
        if response != 'y':
            return 1
    
    print()
    print("=" * 70)
    print("【更新 docker-compose 檔案】")
    print("=" * 70)
    print()
    
    compose_files = [
        BASE_DIR / "docker-compose.cloud.yml",
        BASE_DIR / "docker-compose.unified.yml",
        BASE_DIR / "docker-compose.safe.yml",
    ]
    
    updated_files = []
    failed_files = []
    
    for compose_file in compose_files:
        if compose_file.exists():
            log(f"更新: {compose_file.name}", "PROGRESS")
            success, message = update_password_in_file(
                compose_file, "odoo", new_password
            )
            
            if success:
                log(f"✓ {compose_file.name}: {message}", "OK")
                updated_files.append(compose_file)
            else:
                log(f"✗ {compose_file.name}: {message}", "WARN")
                failed_files.append((compose_file, message))
    
    print()
    print("=" * 70)
    print("【更新結果】")
    print("=" * 70)
    print()
    
    if updated_files:
        log(f"成功更新 {len(updated_files)} 個檔案", "OK")
        for f in updated_files:
            print(f"  ✓ {f.name}")
    
    if failed_files:
        log(f"{len(failed_files)} 個檔案更新失敗", "WARN")
        for f, msg in failed_files:
            print(f"  ✗ {f.name}: {msg}")
    
    print()
    print("=" * 70)
    print("【重要提醒】")
    print("=" * 70)
    print()
    print("⚠️  更新密碼後需要：")
    print()
    print("1. 停止資料庫容器")
    print("   docker stop wuchangv510-db-1")
    print()
    print("2. 備份現有資料庫（如果重要）")
    print("   docker exec wuchangv510-db-1 pg_dump -U odoo postgres > backup.sql")
    print()
    print("3. 更新資料庫密碼（在容器內）")
    print("   或重新建立資料庫容器（會清除資料）")
    print()
    print("4. 重新啟動容器")
    print("   docker-compose -f docker-compose.unified.yml up -d")
    print()
    print("⚠️  注意：更新密碼可能會導致資料庫連接中斷")
    print("   建議在維護時間窗口進行")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
