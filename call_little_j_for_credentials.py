#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
call_little_j_for_credentials.py

調用小J（Little J Hub）執行憑證設定

功能：
- 通過 Little J Hub API 執行憑證設定
- 使用最高權限（full_agent）
- 自動完成整個流程
"""

import sys
import json
import requests
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def check_little_j_hub():
    """檢查 Little J Hub 狀態"""
    print("【步驟 1：檢查 Little J Hub 狀態】")
    print()
    
    hub_url = os.getenv("WUCHANG_HUB_URL", "http://127.0.0.1:8799")
    hub_token = os.getenv("WUCHANG_HUB_TOKEN", "")
    
    try:
        response = requests.get(
            f"{hub_url}/api/status",
            headers={"Authorization": f"Bearer {hub_token}"} if hub_token else {},
            timeout=2
        )
        
        if response.status_code == 200:
            print(f"  ✓ Little J Hub 運行中: {hub_url}")
            return True, hub_url, hub_token
        else:
            print(f"  ⚠️  Little J Hub 回應異常: {response.status_code}")
            return False, hub_url, hub_token
    except requests.exceptions.ConnectionError:
        print(f"  ✗ Little J Hub 未運行: {hub_url}")
        print("  請先啟動 Little J Hub")
        return False, hub_url, hub_token
    except Exception as e:
        print(f"  ✗ 檢查失敗: {e}")
        return False, hub_url, hub_token


def request_full_agent_permission(hub_url: str, hub_token: str):
    """請求 full_agent 權限"""
    print()
    print("【步驟 2：請求最高權限】")
    print()
    
    try:
        # 通過控制中心請求權限
        control_center_url = "http://127.0.0.1:8788"
        
        # 檢查控制中心
        try:
            response = requests.get(f"{control_center_url}/api/local/health", timeout=2)
            if response.status_code != 200:
                print("  ⚠️  控制中心未運行，跳過權限請求")
                return True  # 繼續執行
        except:
            print("  ⚠️  控制中心未運行，跳過權限請求")
            return True
        
        # 請求 full_agent 權限
        response = requests.post(
            f"{control_center_url}/api/authz/request",
            json={
                "permissions": ["full_agent"],
                "ttl_seconds": 3600,
                "reason": "執行憑證設定和授權流程",
                "scope": {"domain": "wuchang.life", "node_id": "local_agent"},
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                request_id = data.get("request_id")
                print(f"  ✓ 已提交權限請求，ID: {request_id}")
                print("  （需要管理員核准）")
                return True
            else:
                print(f"  ⚠️  權限請求失敗: {data.get('error', '未知錯誤')}")
                return True  # 繼續執行
        else:
            print(f"  ⚠️  權限請求失敗: {response.status_code}")
            return True  # 繼續執行
            
    except Exception as e:
        print(f"  ⚠️  權限請求時發生錯誤: {e}")
        print("  （將繼續執行，可能某些操作需要權限）")
        return True


def execute_via_little_j(task: str, params: dict = None):
    """通過 Little J Hub 執行任務"""
    print()
    print(f"【步驟 3：通過小J執行任務】")
    print(f"  任務: {task}")
    print()
    
    hub_url = os.getenv("WUCHANG_HUB_URL", "http://127.0.0.1:8799")
    hub_token = os.getenv("WUCHANG_HUB_TOKEN", "")
    
    try:
        # 建立任務請求
        payload = {
            "task": task,
            "params": params or {},
            "priority": "high",
            "require_full_agent": True,
        }
        
        headers = {
            "Content-Type": "application/json",
        }
        
        if hub_token:
            headers["Authorization"] = f"Bearer {hub_token}"
        
        response = requests.post(
            f"{hub_url}/api/tasks/execute",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                print(f"  ✓ 任務已提交")
                if data.get("task_id"):
                    print(f"    任務 ID: {data.get('task_id')}")
                return True, data
            else:
                print(f"  ✗ 任務執行失敗: {data.get('error', '未知錯誤')}")
                return False, data
        else:
            print(f"  ✗ 請求失敗: {response.status_code}")
            print(f"    回應: {response.text[:200]}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print(f"  ✗ 無法連接到 Little J Hub: {hub_url}")
        print("  請確認 Little J Hub 正在運行")
        return False, None
    except Exception as e:
        print(f"  ✗ 執行失敗: {e}")
        return False, None


def execute_credentials_setup_directly():
    """直接執行憑證設定（如果 Little J Hub 不可用）"""
    print()
    print("【步驟 4：直接執行憑證設定】")
    print()
    
    import subprocess
    
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
        
        if result.returncode == 0:
            print("  ✓ 憑證設定完成")
            return True
        else:
            print("  ⚠️  憑證設定未完成（可能需要手動操作）")
            return False
    except Exception as e:
        print(f"  ✗ 執行失敗: {e}")
        return False


def main():
    """主函數"""
    import os
    
    print("=" * 70)
    print("調用小J執行憑證設定")
    print("=" * 70)
    print()
    
    # 步驟 1: 檢查 Little J Hub
    hub_available, hub_url, hub_token = check_little_j_hub()
    
    # 步驟 2: 請求權限
    if hub_available:
        request_full_agent_permission(hub_url, hub_token)
    
    # 步驟 3: 通過 Little J Hub 執行（如果可用）
    if hub_available:
        success, result = execute_via_little_j(
            "setup_google_credentials",
            {
                "client_id": "581281764864-4eg0icu55pkmbcirheflhp7fgt7gk499.apps.googleusercontent.com",
                "project_id": "wuchang-sbir-project",
                "target_path": str(BASE_DIR / "google_credentials.json"),
            }
        )
        
        if success:
            print()
            print("=" * 70)
            print("【完成】")
            print("=" * 70)
            print()
            print("✓ 已通過小J提交憑證設定任務")
            print("  請等待任務完成")
            return 0
    
    # 步驟 4: 如果 Little J Hub 不可用，直接執行
    print()
    print("⚠️  Little J Hub 不可用，將直接執行憑證設定")
    print()
    
    if execute_credentials_setup_directly():
        print()
        print("=" * 70)
        print("【完成】")
        print("=" * 70)
        print()
        print("✓ 憑證設定已完成")
        print()
        print("現在可以執行完整授權：")
        print("  python complete_authorization_and_setup.py")
        return 0
    else:
        print()
        print("=" * 70)
        print("【需要手動操作】")
        print("=" * 70)
        print()
        print("請按照指引手動下載並設定憑證檔案")
        return 1


if __name__ == "__main__":
    sys.exit(main())
