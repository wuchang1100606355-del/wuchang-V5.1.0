#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
full_agent_setup_credentials_complete.py

完整流程：啟動服務 → 授予最高權限 → 執行憑證設定

功能：
- 自動啟動控制中心（如果未運行）
- 自動登入
- 請求並獲得 full_agent 權限
- 執行憑證設定
- 執行授權和後續作業
"""

import sys
import json
import os
import subprocess
import requests
import time
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
CONTROL_CENTER_URL = "http://127.0.0.1:8788"
AUTH_CONFIG_FILE = BASE_DIR / "auto_auth_config.json"
CLIENT_ID = "581281764864-4eg0icu55pkmbcirheflhp7fgt7gk499.apps.googleusercontent.com"


def check_and_start_control_center():
    """檢查並啟動控制中心"""
    print("【步驟 1：檢查並啟動控制中心】")
    print()
    
    try:
        response = requests.get(f"{CONTROL_CENTER_URL}/api/local/health", timeout=2)
        if response.status_code == 200:
            print("  ✓ 控制中心已運行")
            return True
    except:
        pass
    
    print("  ⚠️  控制中心未運行，正在啟動...")
    
    # 嘗試使用 start_servers.bat
    bat_file = BASE_DIR / "start_servers.bat"
    if bat_file.exists():
        try:
            subprocess.Popen(
                ["cmd", "/c", str(bat_file)],
                cwd=BASE_DIR,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            print("  ✓ 已啟動服務（背景執行）")
            print("  等待服務啟動...")
            
            # 等待服務啟動（最多 30 秒）
            for i in range(30):
                time.sleep(1)
                try:
                    response = requests.get(f"{CONTROL_CENTER_URL}/api/local/health", timeout=2)
                    if response.status_code == 200:
                        print(f"  ✓ 控制中心已啟動（等待 {i+1} 秒）")
                        return True
                except:
                    pass
                if i % 5 == 0 and i > 0:
                    print(f"    等待中... ({i}/30 秒)")
            
            print("  ⚠️  等待超時，請確認服務已啟動")
            return False
        except Exception as e:
            print(f"  ✗ 啟動失敗: {e}")
            return False
    else:
        print("  ✗ 找不到啟動腳本")
        print("  請手動啟動控制中心：")
        print("    python local_control_center.py")
        return False


def load_auth_config():
    """載入授權配置"""
    if AUTH_CONFIG_FILE.exists():
        try:
            return json.loads(AUTH_CONFIG_FILE.read_text(encoding="utf-8"))
        except:
            return {}
    return {}


def login_and_get_permissions(session: requests.Session, account_id: str, pin: str):
    """登入並獲取權限"""
    print()
    print("【步驟 2：登入並獲取權限】")
    print()
    
    # 登入
    try:
        response = session.post(
            f"{CONTROL_CENTER_URL}/api/auth/login",
            json={"account_id": account_id, "pin": pin},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                print(f"  ✓ 已登入: {account_id}")
            else:
                print(f"  ✗ 登入失敗: {data.get('error', '未知錯誤')}")
                return False
        else:
            print(f"  ✗ 登入失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ 登入時發生錯誤: {e}")
        return False
    
    # 檢查當前權限
    try:
        response = session.get(f"{CONTROL_CENTER_URL}/api/auth/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                perms = data.get("status", {}).get("permissions", [])
                print(f"  當前權限: {perms}")
                
                if "full_agent" in perms:
                    print("  ✓ 已擁有 full_agent 權限")
                    return True
                
                # 請求 full_agent 權限
                print("  請求 full_agent 權限...")
                response = session.post(
                    f"{CONTROL_CENTER_URL}/api/authz/request",
                    json={
                        "permissions": ["full_agent"],
                        "ttl_seconds": 7200,
                        "reason": "代理用戶執行憑證設定和 Google Tasks API 授權流程",
                        "scope": {"domain": "wuchang.life", "node_id": "local_agent"},
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        request_id = data.get("request_id")
                        print(f"  ✓ 已提交權限請求，ID: {request_id}")
                        
                        # 嘗試自動核准（如果配置允許）
                        config = load_auth_config()
                        if config.get("auto_approve", False):
                            print("  自動核准中...")
                            time.sleep(1)
                            approve_response = session.post(
                                f"{CONTROL_CENTER_URL}/api/authz/requests/approve",
                                json={"id": request_id},
                                timeout=5
                            )
                            if approve_response.status_code == 200:
                                approve_data = approve_response.json()
                                if approve_data.get("ok"):
                                    print("  ✓ 權限已自動核准")
                                    time.sleep(2)
                                    # 再次檢查權限
                                    status_response = session.get(f"{CONTROL_CENTER_URL}/api/auth/status", timeout=5)
                                    if status_response.status_code == 200:
                                        status_data = status_response.json()
                                        if status_data.get("ok"):
                                            new_perms = status_data.get("status", {}).get("permissions", [])
                                            if "full_agent" in new_perms:
                                                print("  ✓ full_agent 權限已生效")
                                                return True
                        else:
                            print("  請管理員手動核准權限請求")
                            print(f"  請求 ID: {request_id}")
                            return False
                else:
                    print(f"  ✗ 權限請求失敗: {response.status_code}")
                    return False
    except Exception as e:
        print(f"  ✗ 獲取權限時發生錯誤: {e}")
        return False
    
    return False


def execute_credentials_setup():
    """執行憑證設定"""
    print()
    print("【步驟 3：執行憑證設定】")
    print()
    
    # 執行憑證搜尋和設定
    try:
        result = subprocess.run(
            [sys.executable, "download_credentials_from_console.py"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        # 檢查憑證檔案是否存在
        credentials_file = BASE_DIR / "google_credentials.json"
        if credentials_file.exists():
            print()
            print("  ✓ 憑證檔案已設定")
            return True
        else:
            print()
            print("  ⚠️  憑證檔案未找到（可能需要手動下載）")
            return False
    except Exception as e:
        print(f"  ✗ 執行失敗: {e}")
        return False


def execute_authorization():
    """執行授權和後續作業"""
    print()
    print("【步驟 4：執行授權和後續作業】")
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, "complete_authorization_and_setup.py"],
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
        
        return result.returncode == 0
    except Exception as e:
        print(f"  ✗ 執行失敗: {e}")
        return False


def main():
    """主函數"""
    print("=" * 70)
    print("完整流程：授予小J最高權限並代理執行憑證設定")
    print("=" * 70)
    print()
    
    # 步驟 1: 檢查並啟動控制中心
    if not check_and_start_control_center():
        print()
        print("=" * 70)
        print("【失敗】")
        print("=" * 70)
        print()
        print("請手動啟動控制中心後重新執行")
        return 1
    
    # 載入配置
    config = load_auth_config()
    account_id = config.get("account_id")
    pin = config.get("pin")
    
    if not account_id or not pin:
        print()
        print("⚠️  未找到自動授權配置")
        print(f"  請建立 {AUTH_CONFIG_FILE} 並填入：")
        print(json.dumps({
            "account_id": "your_account_id",
            "pin": "your_pin",
            "auto_approve": True,
        }, ensure_ascii=False, indent=2))
        print()
        print("或手動輸入登入資訊：")
        try:
            account_id = input("帳號 ID: ").strip()
            pin = input("PIN: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("已取消")
            return 1
    else:
        print(f"✓ 已載入授權配置")
        print()
    
    # 建立 session
    session = requests.Session()
    
    # 步驟 2: 登入並獲取權限
    if not login_and_get_permissions(session, account_id, pin):
        print()
        print("=" * 70)
        print("【權限獲取失敗】")
        print("=" * 70)
        print()
        print("請手動核准權限請求後重新執行")
        return 1
    
    # 步驟 3: 執行憑證設定
    if not execute_credentials_setup():
        print()
        print("=" * 70)
        print("【需要手動操作】")
        print("=" * 70)
        print()
        print("請手動下載憑證檔案：")
        print("  1. 前往: https://console.cloud.google.com/apis/credentials")
        print("  2. 下載憑證 JSON 檔案")
        print("  3. 複製到專案目錄並重新命名為 google_credentials.json")
        print()
        print("然後重新執行此腳本")
        return 1
    
    # 步驟 4: 執行授權和後續作業
    if execute_authorization():
        print()
        print("=" * 70)
        print("【完成】")
        print("=" * 70)
        print()
        print("✓ 憑證設定已完成")
        print("✓ OAuth 授權已完成")
        print("✓ 後續作業已完成")
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
        print("✓ 憑證設定已完成")
        print("⚠️  授權或後續作業有問題")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
