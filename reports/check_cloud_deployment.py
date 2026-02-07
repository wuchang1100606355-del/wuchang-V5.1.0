#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_cloud_deployment.py

雲端部署狀態檢查工具

功能：
- 檢查伺服器連接狀態
- 檢查部署檔案同步狀態
- 檢查 DNS 解析狀態
- 檢查雲端服務可用性
- 生成完整部署狀態報告
"""

from __future__ import annotations

import json
import os
import socket
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

BASE_DIR = Path(__file__).resolve().parent


def check_dns_resolution(hostname: str) -> Dict[str, Any]:
    """檢查 DNS 解析"""
    try:
        ip_addresses = socket.gethostbyname_ex(hostname)[2]
        return {
            "hostname": hostname,
            "resolved": True,
            "ip_addresses": ip_addresses,
        }
    except socket.gaierror as e:
        return {
            "hostname": hostname,
            "resolved": False,
            "error": str(e),
        }
    except Exception as e:
        return {
            "hostname": hostname,
            "resolved": False,
            "error": str(e),
        }


def check_http_endpoint(url: str, timeout: float = 5.0) -> Dict[str, Any]:
    """檢查 HTTP 端點"""
    try:
        req = Request(url)
        req.add_header("Accept", "application/json, text/plain")
        with urlopen(req, timeout=timeout) as resp:
            status = int(getattr(resp, "status", 200))
            return {
                "url": url,
                "reachable": 200 <= status < 300,
                "status_code": status,
                "ok": True,
            }
    except URLError as e:
        return {
            "url": url,
            "reachable": False,
            "error": str(e),
            "ok": False,
        }
    except Exception as e:
        return {
            "url": url,
            "reachable": False,
            "error": str(e),
            "ok": False,
        }


def check_file_sync_status(
    files: list[str],
    local_dir: Path,
    server_dir: Optional[Path],
) -> Dict[str, Any]:
    """檢查檔案同步狀態"""
    if not server_dir or not server_dir.exists():
        return {
            "configured": False,
            "server_dir": str(server_dir) if server_dir else None,
            "files": {},
        }
    
    status = {
        "configured": True,
        "server_dir": str(server_dir),
        "local_dir": str(local_dir),
        "files": {},
    }
    
    try:
        from file_compare_sync import compare_files
        results = compare_files(files, server_dir, local_dir)
        status["files"] = {
            f["filename"]: {
                "status": f["status"],
                "local_exists": f["local"] and f["local"].get("exists"),
                "server_exists": f["server"] and f["server"].get("exists"),
            }
            for f in results["files"]
        }
        status["summary"] = results["summary"]
    except Exception as e:
        status["error"] = str(e)
    
    return status


def get_deployment_status() -> Dict[str, Any]:
    """獲取完整部署狀態"""
    status = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "environment": {},
        "dns": {},
        "endpoints": {},
        "file_sync": {},
        "local_services": {},
    }
    
    # 環境變數
    env_vars = {
        "WUCHANG_HEALTH_URL": os.getenv("WUCHANG_HEALTH_URL", ""),
        "WUCHANG_COPY_TO": os.getenv("WUCHANG_COPY_TO", ""),
        "WUCHANG_HUB_URL": os.getenv("WUCHANG_HUB_URL", ""),
        "WUCHANG_HUB_TOKEN": "***" if os.getenv("WUCHANG_HUB_TOKEN") else "",
    }
    status["environment"] = {
        "configured": {k: bool(v) for k, v in env_vars.items()},
        "values": {k: v for k, v in env_vars.items()},
    }
    
    # DNS 解析檢查
    dns_hosts = [
        "wuchang.life",
        "www.wuchang.life",
        "app.wuchang.life",
    ]
    for hostname in dns_hosts:
        status["dns"][hostname] = check_dns_resolution(hostname)
    
    # 端點檢查
    health_url = env_vars.get("WUCHANG_HEALTH_URL", "")
    if health_url:
        status["endpoints"]["health"] = check_http_endpoint(health_url)
    
    hub_url = env_vars.get("WUCHANG_HUB_URL", "")
    if hub_url:
        hub_health = f"{hub_url.rstrip('/')}/health"
        status["endpoints"]["hub"] = check_http_endpoint(hub_health)
    
    # 本機服務檢查
    local_services = {
        "control_center": "http://127.0.0.1:8788/health",
        "little_j_hub": "http://127.0.0.1:8799/health",
    }
    for service_name, url in local_services.items():
        status["local_services"][service_name] = check_http_endpoint(url, timeout=2.0)
    
    # 檔案同步狀態
    server_dir_str = env_vars.get("WUCHANG_COPY_TO", "")
    if server_dir_str:
        try:
            from safe_sync_push import DEFAULT_FILES, RULE_FILES
            server_dir = Path(server_dir_str).expanduser().resolve()
            
            # KB files
            kb_status = check_file_sync_status(DEFAULT_FILES, BASE_DIR, server_dir)
            status["file_sync"]["kb"] = kb_status
            
            # Rules files
            rules_status = check_file_sync_status(RULE_FILES, BASE_DIR, server_dir)
            status["file_sync"]["rules"] = rules_status
        except Exception as e:
            status["file_sync"]["error"] = str(e)
    
    # 計算整體狀態
    dns_ok = all(d.get("resolved", False) for d in status["dns"].values())
    endpoints_ok = all(e.get("ok", False) for e in status["endpoints"].values())
    
    if endpoints_ok and dns_ok:
        status["overall_status"] = "healthy"
    elif endpoints_ok or dns_ok:
        status["overall_status"] = "partial"
    else:
        status["overall_status"] = "degraded"
    
    return status


def print_deployment_status(status: Dict[str, Any]) -> None:
    """列印部署狀態報告"""
    # 設定 UTF-8 編碼輸出
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except:
            pass
    
    print("=" * 70)
    print("雲端部署狀態檢查報告")
    print("=" * 70)
    print(f"檢查時間: {status['timestamp']}\n")
    
    # 環境變數狀態
    print("【環境變數配置】")
    env = status["environment"]
    for var_name, configured in env["configured"].items():
        status_icon = "[已設定]" if configured else "[未設定]"
        print(f"  {status_icon} {var_name}")
    print()
    
    # DNS 解析狀態
    print("【DNS 解析狀態】")
    for hostname, dns_info in status["dns"].items():
        if dns_info.get("resolved"):
            ips = ", ".join(dns_info.get("ip_addresses", []))
            print(f"  [OK] {hostname} -> {ips}")
        else:
            print(f"  [X] {hostname} -> 解析失敗")
            if dns_info.get("error"):
                print(f"    錯誤: {dns_info['error']}")
    print()
    
    # 端點狀態
    if status["endpoints"]:
        print("【雲端端點狀態】")
        for endpoint_name, endpoint_info in status["endpoints"].items():
            if endpoint_info.get("ok"):
                status_code = endpoint_info.get("status_code", 0)
                print(f"  [OK] {endpoint_name}: {endpoint_info['url']} (HTTP {status_code})")
            else:
                print(f"  [X] {endpoint_name}: {endpoint_info['url']}")
                if endpoint_info.get("error"):
                    print(f"    錯誤: {endpoint_info['error']}")
        print()
    
    # 本機服務狀態
    if status["local_services"]:
        print("【本機服務狀態】")
        for service_name, service_info in status["local_services"].items():
            if service_info.get("ok"):
                print(f"  [OK] {service_name}: 運行中")
            else:
                print(f"  [X] {service_name}: 未運行")
        print()
    
    # 檔案同步狀態
    if status["file_sync"]:
        print("【檔案同步狀態】")
        if "error" in status["file_sync"]:
            print(f"  [錯誤] {status['file_sync']['error']}")
        else:
            for profile_name, sync_info in status["file_sync"].items():
                if isinstance(sync_info, dict) and sync_info.get("configured"):
                    summary = sync_info.get("summary", {})
                    print(f"\n  Profile: {profile_name}")
                    print(f"    伺服器目錄: {sync_info.get('server_dir', 'N/A')}")
                    print(f"    總檔案數: {summary.get('total', 0)}")
                    print(f"    內容相同: {summary.get('same', 0)}")
                    print(f"    內容不同: {summary.get('different', 0)}")
                    print(f"    僅本機存在: {summary.get('only_local', 0)}")
                    print(f"    僅伺服器存在: {summary.get('only_server', 0)}")
                elif isinstance(sync_info, dict) and not sync_info.get("configured"):
                    print(f"  Profile: {profile_name} - [未配置]")
        print()
    
    # 整體狀態
    overall = status.get("overall_status", "unknown")
    print(f"【整體部署狀態】: {overall.upper()}")
    print("=" * 70)


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="檢查雲端部署狀態")
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式輸出",
    )
    
    args = parser.parse_args()
    
    status = get_deployment_status()
    
    if args.json:
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        print_deployment_status(status)


if __name__ == "__main__":
    main()
