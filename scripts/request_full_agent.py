#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
request_full_agent.py

請求最高權限（full_agent）的便捷腳本
"""

import sys
import json
import requests
from typing import Optional, Dict, Any

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_URL = "http://127.0.0.1:8788"


def check_server() -> bool:
    """檢查伺服器是否運行"""
    try:
        # 嘗試多個端點
        endpoints = [
            "/api/local/health",
            "/",
            "/api/deployment/status"
        ]
        for endpoint in endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=2)
                if response.status_code in [200, 404]:  # 404 也表示服務在運行
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


def request_full_agent(
    session: requests.Session,
    ttl_seconds: int = 86400,
    domain: str = "wuchang.life",
    reason: str = "系統管理需要"
) -> Optional[Dict[str, Any]]:
    """請求最高權限"""
    try:
        response = session.post(
            f"{BASE_URL}/api/authz/request",
            json={
                "permissions": ["full_agent"],
                "ttl_seconds": ttl_seconds,
                "scope": {"domain": domain},
                "reason": reason
            },
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                print("✓ 授權請求已提交")
                return data
        print(f"✗ 授權請求失敗：{response.text}")
        return None
    except Exception as e:
        print(f"✗ 授權請求錯誤：{e}")
        return None


def list_grants(session: requests.Session) -> None:
    """列出當前授權"""
    try:
        response = session.get(
            f"{BASE_URL}/api/authz/grants/list",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                grants = data.get("grants", [])
                print("\n【當前授權】")
                if grants:
                    for grant in grants:
                        perms = grant.get("permissions", [])
                        if "full_agent" in perms:
                            print(f"  ✓ full_agent: 已授權")
                        else:
                            print(f"  - {', '.join(perms)}")
                else:
                    print("  無授權記錄")
    except Exception as e:
        print(f"檢查授權失敗：{e}")


def main():
    """主函數"""
    print("=" * 70)
    print("本地小J最高權限授權工具")
    print("=" * 70)
    print()
    
    # 檢查伺服器
    print("檢查控制中心狀態...")
    if not check_server():
        print("✗ 控制中心未運行")
        print()
        print("請先啟動控制中心：")
        print("  python local_control_center.py")
        print()
        print("或使用：")
        print("  start_servers.bat")
        sys.exit(1)
    
    print("✓ 控制中心運行中")
    print()
    
    # 登入資訊
    print("【登入】")
    account_id = input("請輸入帳號 ID: ").strip()
    if not account_id:
        print("✗ 帳號 ID 不能為空")
        sys.exit(1)
    
    pin = input("請輸入 PIN: ").strip()
    if not pin:
        print("✗ PIN 不能為空")
        sys.exit(1)
    
    print()
    
    # 建立會話並登入
    session = requests.Session()
    if not login(session, account_id, pin):
        sys.exit(1)
    
    print()
    
    # 檢查現有授權
    list_grants(session)
    print()
    
    # 請求授權
    print("【請求最高權限】")
    ttl_input = input("授權有效期（小時，預設 24）: ").strip()
    ttl_hours = int(ttl_input) if ttl_input else 24
    ttl_seconds = ttl_hours * 3600
    
    reason = input("授權原因（選填）: ").strip() or "系統管理需要"
    
    print()
    result = request_full_agent(session, ttl_seconds=ttl_seconds, reason=reason)
    
    if result:
        request_id = result.get("request_id")
        print()
        print("【授權請求資訊】")
        print(f"  請求 ID: {request_id}")
        print(f"  狀態: 待核准")
        print(f"  有效期: {ttl_hours} 小時")
        print()
        print("【下一步】")
        print("授權請求已提交，需要管理員核准。")
        print("核准後即可使用最高權限。")
        print()
        print("查看請求狀態：")
        print(f"  GET {BASE_URL}/api/authz/requests/get?id={request_id}")
    else:
        print()
        print("【提示】")
        print("如果錯誤訊息提到需要填寫責任自然人，請先：")
        print("1. 在帳號設定中填寫 design_responsibility.natural_person")
        print("2. 在帳號設定中填寫 usage_responsibility.natural_person")
        print("3. 然後重新執行此腳本")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
