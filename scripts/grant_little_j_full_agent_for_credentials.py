#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
grant_little_j_full_agent_for_credentials.py

授予小J最高權限代理執行憑證設定

功能：
- 自動登入（如果需要）
- 請求 full_agent 權限
- 自動核准（如果配置允許）
- 執行憑證設定和授權流程
"""

import sys
import json
import os
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
PROJECT_ID = "wuchang-sbir-project"


def check_control_center():
    """檢查控制中心"""
    try:
        response = requests.get(f"{CONTROL_CENTER_URL}/api/local/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def load_auth_config():
    """載入授權配置"""
    if AUTH_CONFIG_FILE.exists():
        try:
            return json.loads(AUTH_CONFIG_FILE.read_text(encoding="utf-8"))
        except:
            return {}
    return {}


def login(session: requests.Session, account_id: str, pin: str):
    """登入"""
    try:
        response = session.post(
            f"{CONTROL_CENTER_URL}/api/auth/login",
            json={"account_id": account_id, "pin": pin},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("ok", False)
        return False
    except:
        return False


def get_current_permissions(session: requests.Session):
    """獲取當前權限"""
    try:
        response = session.get(f"{CONTROL_CENTER_URL}/api/auth/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                return data.get("status", {}).get("permissions", [])
        return []
    except:
        return []


def request_full_agent(session: requests.Session, reason: str = "代理執行憑證設定和授權流程"):
    """請求 full_agent 權限"""
    try:
        response = session.post(
            f"{CONTROL_CENTER_URL}/api/authz/request",
            json={
                "permissions": ["full_agent"],
                "ttl_seconds": 7200,
                "reason": reason,
                "scope": {"domain": "wuchang.life", "node_id": "local_agent"},
            },
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                return data.get("request_id")
        return None
    except:
        return None


def approve_request(session: requests.Session, request_id: str):
    """核准權限請求"""
    try:
        response = session.post(
            f"{CONTROL_CENTER_URL}/api/authz/requests/approve",
            json={"id": request_id},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("ok", False)
        return False
    except:
        return False


def execute_credentials_setup():
    """執行憑證設定"""
    import subprocess
    
    # 1. 搜尋並設定憑證檔案
    print("  執行憑證搜尋和設定...")
    result1 = subprocess.run(
        [sys.executable, "download_credentials_from_console.py"],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60
    )
    
    if result1.returncode != 0:
        print(f"    ⚠️  憑證設定未完成（可能需要手動下載）")
        print(f"    {result1.stdout[-200:]}")
        return False
    
    # 2. 檢查憑證檔案是否存在
    credentials_file = BASE_DIR / "google_credentials.json"
    if not credentials_file.exists():
        print("    ✗ 憑證檔案不存在")
        return False
    
    print("    ✓ 憑證檔案已設定")
    return True


def execute_authorization_and_tasks():
    """執行授權和後續作業"""
    import subprocess
    
    print("  執行完整授權和後續作業...")
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


def main():
    """主函數"""
    print("=" * 70)
    print("授予小J最高權限代理執行憑證設定")
    print("=" * 70)
    print()
    
    # 檢查控制中心
    if not check_control_center():
        print("✗ 控制中心未運行")
        print("請先啟動控制中心：")
        print("  python local_control_center.py")
        return 1
    
    print("✓ 控制中心運行中")
    print()
    
    # 載入配置
    config = load_auth_config()
    account_id = config.get("account_id")
    pin = config.get("pin")
    auto_approve = config.get("auto_approve", False)
    
    # 建立 session
    session = requests.Session()
    
    # 登入（如果需要）
    if account_id and pin:
        print("【登入】")
        if login(session, account_id, pin):
            print(f"✓ 已登入: {account_id}")
        else:
            print(f"✗ 登入失敗")
            return 1
        print()
    
    # 檢查當前權限
    print("【檢查權限】")
    current_perms = get_current_permissions(session)
    print(f"  當前權限: {current_perms}")
    print()
    
    # 請求 full_agent 權限
    if "full_agent" not in current_perms:
        print("【請求最高權限】")
        request_id = request_full_agent(session, "代理用戶執行憑證設定和 Google Tasks API 授權流程")
        
        if request_id:
            print(f"✓ 已提交權限請求，ID: {request_id}")
            
            # 自動核准（如果配置允許）
            if auto_approve:
                print("  自動核准中...")
                if approve_request(session, request_id):
                    print("✓ 權限已自動核准")
                    time.sleep(2)
                    current_perms = get_current_permissions(session)
                    if "full_agent" not in current_perms:
                        print("⚠️  權限尚未生效，請稍候")
                else:
                    print("✗ 自動核准失敗，請手動核准")
            else:
                print("  請管理員手動核准權限請求")
                print(f"  請求 ID: {request_id}")
        else:
            print("✗ 權限請求失敗")
        print()
    else:
        print("✓ 已擁有 full_agent 權限")
        print()
    
    # 執行憑證設定
    print("【執行憑證設定】")
    if execute_credentials_setup():
        print()
        # 執行授權和後續作業
        print("【執行授權和後續作業】")
        if execute_authorization_and_tasks():
            print()
            print("=" * 70)
            print("【完成】")
            print("=" * 70)
            print()
            print("✓ 憑證設定已完成")
            print("✓ OAuth 授權已完成")
            print("✓ 後續作業已完成")
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
    else:
        print()
        print("=" * 70)
        print("【需要手動操作】")
        print("=" * 70)
        print()
        print("請手動下載憑證檔案並設定")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
