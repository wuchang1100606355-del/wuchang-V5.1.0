#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_server_connection.py

伺服器連接檢查工具

功能：
- 檢查本機服務狀態
- 測試遠端伺服器連接（如果設定）
- 檢查 Hub 連接狀態
- 生成連接報告
"""

from __future__ import annotations

import json
import os
import sys
import time
from typing import Dict, Any, Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)


def check_local_services() -> Dict[str, Any]:
    """檢查本機服務狀態"""
    services = {
        "control_center": {
            "name": "本機中控台",
            "url": "http://127.0.0.1:8788/",
            "health_url": "http://127.0.0.1:8788/health",
        },
        "little_j_hub": {
            "name": "Little J Hub",
            "url": "http://127.0.0.1:8799/",
            "health_url": "http://127.0.0.1:8799/health",
        },
    }
    
    results = {}
    for service_id, config in services.items():
        try:
            req = Request(config["health_url"])
            req.add_header("Accept", "application/json, text/plain")
            with urlopen(req, timeout=2.0) as resp:
                status = int(getattr(resp, "status", 200))
                results[service_id] = {
                    "name": config["name"],
                    "url": config["url"],
                    "health_url": config["health_url"],
                    "status": "running" if 200 <= status < 300 else "error",
                    "http_status": status,
                    "reachable": True,
                }
        except URLError as e:
            results[service_id] = {
                "name": config["name"],
                "url": config["url"],
                "health_url": config["health_url"],
                "status": "not_running",
                "reachable": False,
                "error": str(e),
            }
        except Exception as e:
            results[service_id] = {
                "name": config["name"],
                "url": config["url"],
                "health_url": config["health_url"],
                "status": "unknown",
                "reachable": False,
                "error": str(e),
            }
    
    return results


def check_remote_server(health_url: Optional[str] = None) -> Dict[str, Any]:
    """檢查遠端伺服器連接"""
    if not health_url:
        health_url = os.getenv("WUCHANG_HEALTH_URL", "").strip()
    
    if not health_url:
        return {
            "configured": False,
            "hint": "請設定 WUCHANG_HEALTH_URL 環境變數或提供 health_url 參數",
        }
    
    try:
        from risk_gate import check_server_health
        
        result = check_server_health(health_url, timeout_seconds=5.0, retries=2)
        return {
            "configured": True,
            "health_url": health_url,
            "ok": result.ok,
            "status": result.status,
            "content_type": result.content_type,
            "body_preview": result.body_preview[:200] if result.body_preview else "",
            "reachable": result.ok,
        }
    except Exception as e:
        return {
            "configured": True,
            "health_url": health_url,
            "ok": False,
            "reachable": False,
            "error": str(e),
        }


def check_hub_connection() -> Dict[str, Any]:
    """檢查 Hub 連接狀態"""
    hub_url = os.getenv("WUCHANG_HUB_URL", "").strip().rstrip("/")
    hub_token = os.getenv("WUCHANG_HUB_TOKEN", "").strip()
    
    if not hub_url:
        return {
            "configured": False,
            "hint": "請設定 WUCHANG_HUB_URL 和 WUCHANG_HUB_TOKEN 環境變數",
        }
    
    if not hub_token:
        return {
            "configured": True,
            "hub_url": hub_url,
            "error": "WUCHANG_HUB_TOKEN 未設定",
        }
    
    try:
        # 檢查 Hub 健康狀態
        health_url = f"{hub_url}/health"
        req = Request(health_url, method="GET")
        req.add_header("Accept", "application/json")
        if hub_token:
            req.add_header("Authorization", f"Bearer {hub_token}")
        
        with urlopen(req, timeout=5.0) as resp:
            status = int(getattr(resp, "status", 200))
            raw = resp.read(4096).decode("utf-8", errors="ignore")
            
            try:
                health_data = json.loads(raw)
            except:
                health_data = {"raw": raw[:200]}
            
            return {
                "configured": True,
                "hub_url": hub_url,
                "health_url": health_url,
                "ok": 200 <= status < 300,
                "http_status": status,
                "health": health_data,
                "reachable": True,
            }
    except URLError as e:
        return {
            "configured": True,
            "hub_url": hub_url,
            "health_url": f"{hub_url}/health",
            "ok": False,
            "reachable": False,
            "error": str(e),
        }
    except Exception as e:
        return {
            "configured": True,
            "hub_url": hub_url,
            "ok": False,
            "reachable": False,
            "error": str(e),
        }


def get_connection_status() -> Dict[str, Any]:
    """獲取完整的連接狀態"""
    status = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "local_services": check_local_services(),
        "remote_server": check_remote_server(),
        "hub": check_hub_connection(),
        "environment": {
            "WUCHANG_HEALTH_URL": os.getenv("WUCHANG_HEALTH_URL", ""),
            "WUCHANG_HUB_URL": os.getenv("WUCHANG_HUB_URL", ""),
            "WUCHANG_HUB_TOKEN": "***" if os.getenv("WUCHANG_HUB_TOKEN") else "",
            "WUCHANG_COPY_TO": os.getenv("WUCHANG_COPY_TO", ""),
        },
    }
    
    # 計算整體連接狀態
    local_ok = any(
        s.get("status") == "running"
        for s in status["local_services"].values()
    )
    remote_ok = status["remote_server"].get("ok", False) if status["remote_server"].get("configured") else None
    hub_ok = status["hub"].get("ok", False) if status["hub"].get("configured") else None
    
    if local_ok:
        status["overall_status"] = "local_available"
    elif remote_ok:
        status["overall_status"] = "remote_available"
    elif hub_ok:
        status["overall_status"] = "hub_available"
    else:
        status["overall_status"] = "limited"
    
    return status


def print_status(status: Dict[str, Any]) -> None:
    """列印狀態報告"""
    # 設定 UTF-8 編碼輸出
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except:
            pass
    
    print("=" * 60)
    print("伺服器連接狀態檢查報告")
    print("=" * 60)
    print(f"檢查時間: {status['timestamp']}\n")
    
    # 本機服務
    print("【本機服務】")
    for service_id, service in status["local_services"].items():
        status_icon = "[OK]" if service.get("reachable") else "[X]"
        print(f"  {status_icon} {service['name']}: {service['url']}")
        if service.get("reachable"):
            print(f"    狀態: {service.get('status', 'unknown')} (HTTP {service.get('http_status', 0)})")
        else:
            print(f"    狀態: {service.get('status', 'unknown')}")
            if service.get("error"):
                print(f"    錯誤: {service['error']}")
    print()
    
    # 遠端伺服器
    print("【遠端伺服器】")
    remote = status["remote_server"]
    if remote.get("configured"):
        status_icon = "[OK]" if remote.get("ok") else "[X]"
        print(f"  {status_icon} 健康檢查 URL: {remote.get('health_url', 'N/A')}")
        if remote.get("reachable"):
            print(f"    狀態: OK (HTTP {remote.get('status', 0)})")
        else:
            print(f"    狀態: 不可達")
            if remote.get("error"):
                print(f"    錯誤: {remote['error']}")
    else:
        print(f"  [提示] {remote.get('hint', '未設定')}")
    print()
    
    # Hub 連接
    print("【Hub 連接】")
    hub = status["hub"]
    if hub.get("configured"):
        status_icon = "[OK]" if hub.get("ok") else "[X]"
        print(f"  {status_icon} Hub URL: {hub.get('hub_url', 'N/A')}")
        if hub.get("reachable"):
            print(f"    狀態: OK (HTTP {hub.get('http_status', 0)})")
            if hub.get("health"):
                health = hub["health"]
                if isinstance(health, dict):
                    print(f"    健康狀態: {json.dumps(health, ensure_ascii=False, indent=6)[:200]}")
        else:
            print(f"    狀態: 不可達")
            if hub.get("error"):
                print(f"    錯誤: {hub['error']}")
    else:
        print(f"  [提示] {hub.get('hint', '未設定')}")
    print()
    
    # 環境變數摘要
    print("【環境變數摘要】")
    env = status["environment"]
    print(f"  WUCHANG_HEALTH_URL: {'[已設定]' if env.get('WUCHANG_HEALTH_URL') else '[未設定]'}")
    print(f"  WUCHANG_HUB_URL: {'[已設定]' if env.get('WUCHANG_HUB_URL') else '[未設定]'}")
    print(f"  WUCHANG_HUB_TOKEN: {'[已設定]' if env.get('WUCHANG_HUB_TOKEN') else '[未設定]'}")
    print(f"  WUCHANG_COPY_TO: {'[已設定]' if env.get('WUCHANG_COPY_TO') else '[未設定]'}")
    print()
    
    # 整體狀態
    overall = status.get("overall_status", "unknown")
    print(f"【整體狀態】: {overall}")
    print("=" * 60)


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="檢查伺服器連接狀態")
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式輸出",
    )
    parser.add_argument(
        "--health-url",
        type=str,
        help="指定遠端伺服器健康檢查 URL（覆蓋環境變數）",
    )
    
    args = parser.parse_args()
    
    status = get_connection_status()
    
    # 如果指定了 health_url，覆蓋環境變數
    if args.health_url:
        status["remote_server"] = check_remote_server(args.health_url)
    
    if args.json:
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        print_status(status)


if __name__ == "__main__":
    main()
