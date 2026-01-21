#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
quick_setup_credentials.py

快速設定憑證檔案（支援拖放或路徑輸入）

使用方式：
  python quick_setup_credentials.py
  或
  python quick_setup_credentials.py "檔案路徑"
"""

import sys
import json
import shutil
import subprocess
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
CREDENTIALS_FILE = BASE_DIR / "google_credentials.json"
TOKEN_FILE = BASE_DIR / "google_token.json"
NEW_CLIENT_ID = "581281764864-2a3285kidmm2rj7jmrl9ve7cqfvid32d.apps.googleusercontent.com"


def setup_credentials_file(source_file: Path):
    """設定憑證檔案"""
    print(f"正在設定憑證檔案: {source_file.name}")
    
    try:
        # 驗證檔案
        test_data = json.loads(source_file.read_text(encoding="utf-8"))
        if "installed" not in test_data and "web" not in test_data:
            print("✗ 憑證檔案格式不正確")
            return False
        
        # 複製到目標位置
        shutil.copy2(source_file, CREDENTIALS_FILE)
        print(f"✓ 憑證檔案已設定: {CREDENTIALS_FILE}")
        
        # 顯示客戶端 ID
        if "installed" in test_data:
            client_id = test_data["installed"].get("client_id", "")
        elif "web" in test_data:
            client_id = test_data["web"].get("client_id", "")
        else:
            client_id = "未知"
        
        print(f"✓ 客戶端 ID: {client_id}")
        return True
        
    except Exception as e:
        print(f"✗ 設定憑證檔案時發生錯誤: {e}")
        return False


def execute_authorization():
    """執行授權流程"""
    print()
    print("開始執行 OAuth 授權流程...")
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, "complete_authorization_and_setup.py"],
            cwd=BASE_DIR,
            timeout=300
        )
        
        if TOKEN_FILE.exists():
            print()
            print("✓ OAuth token 已生成")
            return True
        else:
            print()
            print("⚠️  OAuth token 未生成")
            return False
            
    except Exception as e:
        print(f"✗ 執行授權流程時發生錯誤: {e}")
        return False


def main():
    """主函數"""
    print("=" * 70)
    print("快速設定憑證檔案")
    print("=" * 70)
    print()
    
    # 檢查是否提供了檔案路徑
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
    else:
        # 提示用戶輸入或拖放檔案
        print("請提供憑證檔案：")
        print("  方式 1: 將檔案拖放到此視窗，然後按 Enter")
        print("  方式 2: 輸入檔案完整路徑，然後按 Enter")
        print()
        try:
            user_input = input("檔案路徑: ").strip().strip('"').strip("'")
            if not user_input:
                print("已取消")
                return 1
            file_path = Path(user_input)
        except (EOFError, KeyboardInterrupt):
            print("已取消")
            return 1
    
    # 檢查檔案是否存在
    if not file_path.exists():
        print(f"✗ 檔案不存在: {file_path}")
        return 1
    
    if not file_path.is_file():
        print(f"✗ 不是檔案: {file_path}")
        return 1
    
    # 設定憑證檔案
    if not setup_credentials_file(file_path):
        return 1
    
    # 執行授權流程
    if execute_authorization():
        print()
        print("=" * 70)
        print("【完成】")
        print("=" * 70)
        print()
        print("✓ 憑證設定和授權已完成")
        print()
        print("現在可以使用：")
        print("  - python get_jules_task_direct.py <task_url>")
        print("  - python upload_diff_to_jules.py --auto-upload")
        print("  - python sync_from_google_task.py <task_url> <target_file>")
        print()
        return 0
    else:
        print()
        print("=" * 70)
        print("【部分完成】")
        print("=" * 70)
        print()
        print("✓ 憑證檔案已設定")
        print("⚠️  授權流程有問題")
        print()
        print("可以手動執行：")
        print("  python complete_authorization_and_setup.py")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
