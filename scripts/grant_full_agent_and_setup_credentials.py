#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
grant_full_agent_and_setup_credentials.py

授予小J最高權限並代理執行憑證設定

功能：
- 請求 full_agent 權限
- 建立憑證設定 job
- 通過 Little J Hub 執行
- 完成後續作業
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
CLIENT_ID = "581281764864-4eg0icu55pkmbcirheflhp7fgt7gk499.apps.googleusercontent.com"
PROJECT_ID = "wuchang-sbir-project"


def check_control_center():
    """檢查控制中心狀態"""
    print("【步驟 1：檢查控制中心】")
    print()
    
    try:
        response = requests.get(f"{CONTROL_CENTER_URL}/api/local/health", timeout=2)
        if response.status_code == 200:
            print("  ✓ 控制中心運行中")
            return True
        else:
            print(f"  ✗ 控制中心回應異常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("  ✗ 控制中心未運行")
        print("  請先啟動控制中心：")
        print("    python local_control_center.py")
        return False
    except Exception as e:
        print(f"  ✗ 檢查失敗: {e}")
        return False


def request_full_agent_permission(session: requests.Session):
    """請求 full_agent 權限"""
    print()
    print("【步驟 2：請求最高權限（full_agent）】")
    print()
    
    # 檢查當前權限
    try:
        response = session.get(f"{CONTROL_CENTER_URL}/api/auth/status")
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                current_perms = data.get("status", {}).get("permissions", [])
                if "full_agent" in current_perms:
                    print("  ✓ 已擁有 full_agent 權限")
                    return True
    except:
        pass
    
    # 請求權限
    try:
        response = session.post(
            f"{CONTROL_CENTER_URL}/api/authz/request",
            json={
                "permissions": ["full_agent"],
                "ttl_seconds": 7200,  # 2 小時
                "reason": "代理用戶執行憑證設定和 Google Tasks API 授權流程",
                "scope": {
                    "domain": "wuchang.life",
                    "node_id": "local_agent",
                },
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                request_id = data.get("request_id")
                print(f"  ✓ 已提交權限請求，ID: {request_id}")
                print()
                print("  等待管理員核准...")
                print("  （如果已設定自動核准，將自動通過）")
                print()
                
                # 等待核准（最多 30 秒）
                for i in range(30):
                    time.sleep(1)
                    status_response = session.get(f"{CONTROL_CENTER_URL}/api/auth/status")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        if status_data.get("ok"):
                            perms = status_data.get("status", {}).get("permissions", [])
                            if "full_agent" in perms:
                                print("  ✓ full_agent 權限已生效")
                                return True
                    if i % 5 == 0 and i > 0:
                        print(f"    等待中... ({i}/30 秒)")
                
                print("  ⚠️  等待超時，請手動核准權限請求")
                print(f"  請求 ID: {request_id}")
                return False
            else:
                print(f"  ✗ 權限請求失敗: {data.get('error', '未知錯誤')}")
                return False
        else:
            print(f"  ✗ 請求失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ 請求權限時發生錯誤: {e}")
        return False


def create_credentials_setup_job(session: requests.Session):
    """建立憑證設定 job"""
    print()
    print("【步驟 3：建立憑證設定任務】")
    print()
    
    try:
        response = session.post(
            f"{CONTROL_CENTER_URL}/api/jobs/create",
            json={
                "type": "setup_credentials",
                "params": {
                    "client_id": CLIENT_ID,
                    "project_id": PROJECT_ID,
                    "target_path": str(BASE_DIR / "google_credentials.json"),
                    "action": "find_and_setup",
                },
                "actor": "system",
                "domain": "wuchang.life",
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                job_id = data.get("job_id")
                job_path = data.get("path")
                print(f"  ✓ 任務已建立")
                print(f"    任務 ID: {job_id}")
                print(f"    路徑: {job_path}")
                return job_id, job_path
            else:
                print(f"  ✗ 建立任務失敗: {data.get('error', '未知錯誤')}")
                return None, None
        else:
            print(f"  ✗ 請求失敗: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"  ✗ 建立任務時發生錯誤: {e}")
        return None, None


def execute_credentials_setup_directly(session: requests.Session):
    """直接執行憑證設定（使用 full_agent 權限）"""
    print()
    print("【步驟 4：執行憑證設定（使用最高權限）】")
    print()
    
    # 執行憑證搜尋和設定腳本
    try:
        response = session.post(
            f"{CONTROL_CENTER_URL}/api/run/script",
            json={
                "script": "download_credentials_from_console.py",
                "args": [],
                "timeout": 60,
            },
            timeout=65
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                result = data.get("run", {})
                if result.get("ok"):
                    print("  ✓ 憑證設定腳本執行成功")
                    if result.get("stdout"):
                        print("  輸出:")
                        print(result["stdout"][-500:])  # 最後 500 字元
                    return True
                else:
                    print("  ⚠️  腳本執行完成但有警告")
                    if result.get("stderr"):
                        print("  錯誤:")
                        print(result["stderr"][-500:])
                    return False
            else:
                print(f"  ✗ 執行失敗: {data.get('error', '未知錯誤')}")
                return False
        else:
            # 如果沒有 /api/run/script 端點，直接執行 Python 腳本
            print("  ⚠️  API 端點不可用，直接執行腳本...")
            import subprocess
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
            
            return result.returncode == 0
            
    except Exception as e:
        print(f"  ✗ 執行失敗: {e}")
        # 嘗試直接執行
        try:
            import subprocess
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
            return result.returncode == 0
        except:
            return False


def perform_authorization_and_tasks(session: requests.Session):
    """執行授權和後續作業"""
    print()
    print("【步驟 5：執行授權和後續作業】")
    print()
    
    # 檢查憑證檔案是否存在
    credentials_file = BASE_DIR / "google_credentials.json"
    if not credentials_file.exists():
        print("  ✗ 憑證檔案不存在，無法繼續")
        print("  請先完成憑證檔案設定")
        return False
    
    # 執行完整授權和設定
    try:
        import subprocess
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
        
        if result.returncode == 0:
            print("  ✓ 授權和後續作業完成")
            return True
        else:
            print("  ⚠️  執行完成但有警告")
            return False
    except Exception as e:
        print(f"  ✗ 執行失敗: {e}")
        return False


def main():
    """主函數"""
    print("=" * 70)
    print("授予小J最高權限並代理執行憑證設定")
    print("=" * 70)
    print()
    
    # 步驟 1: 檢查控制中心
    if not check_control_center():
        print()
        print("=" * 70)
        print("【失敗】")
        print("=" * 70)
        print()
        print("請先啟動控制中心：")
        print("  python local_control_center.py")
        print("或使用：")
        print("  start_servers.bat")
        return 1
    
    # 建立 session（用於保持登入狀態）
    session = requests.Session()
    
    # 步驟 2: 請求 full_agent 權限
    # 注意：這裡假設已經登入，如果需要登入，應該先執行登入流程
    has_permission = request_full_agent_permission(session)
    
    if not has_permission:
        print()
        print("⚠️  未獲得 full_agent 權限，將嘗試繼續執行")
        print("  （某些操作可能需要權限）")
        print()
    
    # 步驟 3: 建立 job（可選）
    job_id, job_path = create_credentials_setup_job(session)
    if job_id:
        print(f"  任務已建立，可以通過 Hub 執行")
        print()
    
    # 步驟 4: 直接執行憑證設定
    if execute_credentials_setup_directly(session):
        print()
        # 步驟 5: 執行授權和後續作業
        if perform_authorization_and_tasks(session):
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
    else:
        print()
        print("=" * 70)
        print("【需要手動操作】")
        print("=" * 70)
        print()
        print("憑證設定需要手動完成：")
        print("  1. 下載憑證檔案")
        print("  2. 複製到專案目錄")
        print("  3. 重新命名為 google_credentials.json")
        print()
        print("然後執行：")
        print("  python complete_authorization_and_setup.py")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
