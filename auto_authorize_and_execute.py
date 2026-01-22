#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_authorize_and_execute.py

自動獲取權限並執行操作

功能：
- 自動檢查當前權限狀態
- 自動請求必要權限
- 執行授權後的操作
"""

import sys
import json
import requests
from pathlib import Path
from typing import Optional, Dict, Any

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_URL = "http://127.0.0.1:8788"
BASE_DIR = Path(__file__).resolve().parent

# 授權配置檔案（如果存在，會自動讀取）
AUTH_CONFIG_FILE = BASE_DIR / "auto_auth_config.json"


def load_auth_config() -> Optional[Dict[str, Any]]:
    """載入授權配置"""
    if AUTH_CONFIG_FILE.exists():
        try:
            return json.loads(AUTH_CONFIG_FILE.read_text(encoding="utf-8"))
        except:
            return None
    return None


def check_server() -> bool:
    """檢查伺服器是否運行"""
    try:
        endpoints = ["/api/local/health", "/", "/api/deployment/status"]
        for endpoint in endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=2)
                if response.status_code in [200, 404]:
                    return True
            except:
                continue
        return False
    except:
        return False


def login(session: requests.Session, account_id: str, pin: str) -> bool:
    """登入"""
    try:
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"account_id": account_id, "pin": pin},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                print(f"✓ 登入成功：{account_id}")
                return True
        print(f"✗ 登入失敗：{response.text}")
        return False
    except Exception as e:
        print(f"✗ 登入錯誤：{e}")
        return False


def check_current_permissions(session: requests.Session) -> Dict[str, Any]:
    """檢查當前權限"""
    try:
        response = session.get(f"{BASE_URL}/api/auth/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                return data
        return {"ok": False}
    except Exception as e:
        print(f"檢查權限失敗：{e}")
        return {"ok": False}


def list_grants(session: requests.Session) -> list:
    """列出當前授權"""
    try:
        response = session.get(f"{BASE_URL}/api/authz/grants/list", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                return data.get("grants", [])
        return []
    except:
        return []


def has_permission(grants: list, permission: str) -> bool:
    """檢查是否有特定權限"""
    for grant in grants:
        perms = grant.get("permissions", [])
        if permission in perms or "full_agent" in perms or "admin_all" in perms:
            # 檢查是否過期
            items = grant.get("items", [])
            if items:
                import time
                now = int(time.time())
                for item in items:
                    if item.get("permission") == permission or permission in ["full_agent", "admin_all"]:
                        exp = item.get("expires_at_epoch")
                        if exp and int(exp) > now:
                            return True
            else:
                # 舊格式
                exp = grant.get("expires_at_epoch")
                if exp:
                    import time
                    if int(exp) > int(time.time()):
                        return True
                else:
                    return True  # 沒有過期時間，視為永久
    return False


def request_permission(
    session: requests.Session,
    permission: str = "full_agent",
    ttl_seconds: int = 86400,
    domain: str = "wuchang.life",
    reason: str = "自動執行需要"
) -> Optional[Dict[str, Any]]:
    """請求權限"""
    try:
        response = session.post(
            f"{BASE_URL}/api/authz/request",
            json={
                "permissions": [permission],
                "ttl_seconds": ttl_seconds,
                "scope": {"domain": domain},
                "reason": reason
            },
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                print(f"✓ 權限請求已提交：{permission}")
                return data
        print(f"✗ 權限請求失敗：{response.text}")
        return None
    except Exception as e:
        print(f"✗ 權限請求錯誤：{e}")
        return None


def auto_approve_request(session: requests.Session, request_id: str) -> bool:
    """自動核准授權請求（需要管理員權限）"""
    try:
        response = session.post(
            f"{BASE_URL}/api/authz/requests/approve",
            json={
                "id": request_id,
                "ttl_seconds": 86400,
                "scope": {"domain": "wuchang.life"}
            },
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                print(f"✓ 授權請求已核准：{request_id}")
                return True
        print(f"✗ 核准失敗：{response.text}")
        return False
    except Exception as e:
        print(f"✗ 核准錯誤：{e}")
        return False


def execute_with_permission(session: requests.Session, operation: str, **kwargs):
    """在權限下執行操作"""
    print(f"\n【執行操作】{operation}")
    
    if operation == "check_status":
        response = session.get(f"{BASE_URL}/api/deployment/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return data
    
    elif operation == "sync_files":
        # 執行檔案同步
        print("執行檔案同步...")
        # 這裡可以添加實際的同步邏輯
        return {"ok": True, "message": "同步完成"}
    
    elif operation == "get_google_task":
        task_url = kwargs.get("task_url")
        if task_url:
            response = session.post(
                f"{BASE_URL}/api/google-tasks/tasks/from-url",
                json={"url": task_url},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                print(json.dumps(data, ensure_ascii=False, indent=2))
                return data
    
    return {"ok": False, "error": "未知操作"}


def main():
    """主函數"""
    print("=" * 70)
    print("自動權限授權與執行")
    print("=" * 70)
    print()
    
    # 檢查伺服器
    print("檢查控制中心狀態...")
    if not check_server():
        print("✗ 控制中心未運行")
        print("請先啟動：python local_control_center.py")
        sys.exit(1)
    print("✓ 控制中心運行中")
    print()
    
    # 載入配置
    config = load_auth_config()
    if not config:
        print("【配置檔案】")
        print("未找到自動授權配置檔案")
        print(f"請建立 {AUTH_CONFIG_FILE} 並填入：")
        print(json.dumps({
            "account_id": "your_account_id",
            "pin": "your_pin",
            "auto_approve": False,  # 是否自動核准（需要管理員權限）
            "default_permission": "full_agent",
            "default_ttl_hours": 24
        }, ensure_ascii=False, indent=2))
        print()
        print("或手動輸入登入資訊：")
        account_id = input("帳號 ID: ").strip()
        pin = input("PIN: ").strip()
        auto_approve = False
        default_permission = "full_agent"
        default_ttl_hours = 24
    else:
        account_id = config.get("account_id", "")
        pin = config.get("pin", "")
        auto_approve = config.get("auto_approve", False)
        default_permission = config.get("default_permission", "full_agent")
        default_ttl_hours = config.get("default_ttl_hours", 24)
    
    if not account_id or not pin:
        print("✗ 缺少登入資訊")
        sys.exit(1)
    
    print()
    
    # 登入
    session = requests.Session()
    if not login(session, account_id, pin):
        sys.exit(1)
    
    print()
    
    # 檢查當前權限
    print("【檢查當前權限】")
    grants = list_grants(session)
    has_full_agent = has_permission(grants, "full_agent")
    has_admin = has_permission(grants, "admin_all")
    
    if has_full_agent:
        print("✓ 已有 full_agent 權限")
    elif has_admin:
        print("✓ 已有 admin_all 權限")
    else:
        print("✗ 沒有最高權限，正在請求...")
        
        # 請求權限
        result = request_permission(
            session,
            permission=default_permission,
            ttl_seconds=default_ttl_hours * 3600,
            reason="自動執行需要"
        )
        
        if result:
            request_id = result.get("request_id")
            print(f"  請求 ID: {request_id}")
            
            # 如果配置允許且當前帳號有管理員權限，嘗試自動核准
            if auto_approve and has_admin:
                print("  嘗試自動核准...")
                if auto_approve_request(session, request_id):
                    print("✓ 權限已自動核准")
                    # 重新檢查權限
                    grants = list_grants(session)
                    has_full_agent = has_permission(grants, "full_agent")
                else:
                    print("⚠️  自動核准失敗，需要管理員手動核准")
            else:
                print("⚠️  需要管理員核准授權請求")
                print(f"  請求 ID: {request_id}")
    
    print()
    
    # 執行操作
    if has_full_agent or has_admin:
        print("【執行操作】")
        print("✓ 已獲得必要權限，可以執行操作")
        print()
        
        # 這裡可以添加需要執行的操作
        # 例如：檢查系統狀態、同步檔案等
        
        # 範例：檢查部署狀態
        status = execute_with_permission(session, "check_status")
        
        print()
        print("【操作完成】")
        print("所有操作已執行完成")
    else:
        print("【等待授權】")
        print("請等待管理員核准授權請求後再執行操作")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
