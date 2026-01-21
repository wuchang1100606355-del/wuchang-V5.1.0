#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
little_j_setup_credentials_now.py

小J代理執行憑證設定（不依賴控制中心）

功能：
- 直接執行憑證搜尋和設定
- 執行 OAuth 授權
- 執行後續作業
- 生成完整報告
"""

import sys
import json
import subprocess
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
CLIENT_ID = "581281764864-4eg0icu55pkmbcirheflhp7fgt7gk499.apps.googleusercontent.com"
PROJECT_ID = "wuchang-sbir-project"


def execute_step(step_name: str, script_name: str, args: list = None):
    """執行步驟"""
    print(f"【{step_name}】")
    print()
    
    try:
        cmd = [sys.executable, script_name]
        if args:
            cmd.extend(args)
        
        result = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        print()
        return result.returncode == 0
    except Exception as e:
        print(f"✗ 執行失敗: {e}")
        print()
        return False


def main():
    """主函數"""
    print("=" * 70)
    print("小J代理執行憑證設定（完整流程）")
    print("=" * 70)
    print()
    print(f"客戶端 ID: {CLIENT_ID}")
    print(f"專案 ID: {PROJECT_ID}")
    print()
    
    steps_completed = []
    steps_failed = []
    
    # 步驟 1: 搜尋並設定憑證檔案
    if execute_step("步驟 1：搜尋並設定憑證檔案", "download_credentials_from_console.py"):
        steps_completed.append("憑證檔案設定")
        
        # 驗證憑證檔案
        credentials_file = BASE_DIR / "google_credentials.json"
        if credentials_file.exists():
            print("✓ 憑證檔案已確認存在")
            print()
        else:
            print("⚠️  憑證檔案未找到，可能需要手動下載")
            print()
            print("請執行以下操作：")
            print("  1. 前往: https://console.cloud.google.com/apis/credentials")
            print("  2. 下載憑證 JSON 檔案")
            print("  3. 複製到專案目錄並重新命名為 google_credentials.json")
            print()
            steps_failed.append("憑證檔案設定")
    else:
        steps_failed.append("憑證檔案設定")
    
    # 步驟 2: 執行授權和後續作業（如果憑證檔案存在）
    credentials_file = BASE_DIR / "google_credentials.json"
    if credentials_file.exists():
        if execute_step("步驟 2：執行 OAuth 授權和後續作業", "complete_authorization_and_setup.py"):
            steps_completed.append("OAuth 授權和後續作業")
        else:
            steps_failed.append("OAuth 授權和後續作業")
    else:
        print("【步驟 2：跳過（憑證檔案未設定）】")
        print()
        steps_failed.append("OAuth 授權（跳過）")
    
    # 總結
    print("=" * 70)
    print("【執行總結】")
    print("=" * 70)
    print()
    print(f"完成: {len(steps_completed)} 個步驟")
    for step in steps_completed:
        print(f"  ✓ {step}")
    
    if steps_failed:
        print(f"失敗/跳過: {len(steps_failed)} 個步驟")
        for step in steps_failed:
            print(f"  ✗ {step}")
    
    print()
    
    if len(steps_completed) == 2:
        print("=" * 70)
        print("【完成】")
        print("=" * 70)
        print()
        print("✓ 所有步驟已完成")
        print()
        print("現在可以使用：")
        print("  - python get_jules_task_direct.py <task_url>")
        print("  - python upload_diff_to_jules.py --auto-upload")
        print("  - python sync_from_google_task.py <task_url> <target_file>")
        print()
        return 0
    elif credentials_file.exists():
        print("=" * 70)
        print("【部分完成】")
        print("=" * 70)
        print()
        print("✓ 憑證檔案已設定")
        print("⚠️  授權或後續作業有問題")
        print()
        print("可以手動執行：")
        print("  python complete_authorization_and_setup.py")
        print()
        return 1
    else:
        print("=" * 70)
        print("【需要手動操作】")
        print("=" * 70)
        print()
        print("請先下載並設定憑證檔案")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
