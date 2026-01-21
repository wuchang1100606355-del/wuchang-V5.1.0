#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_connection_status.py

檢查連線狀態

功能：
- 檢查 VPN 連接
- 測試伺服器連接
- 檢查環境變數
- 生成連線狀態報告
"""

import sys
import json
import socket
import requests
import os
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def check_vpn_connection() -> dict:
    """檢查 VPN 連接"""
    try:
        import subprocess
        import platform
        
        if platform.system() == "Windows":
            result = subprocess.run(
                ["ipconfig"],
                capture_output=True,
                text=True,
                timeout=5
            )
            output = result.stdout
            # 檢查是否有 10.8.0.x 的 IP
            if "10.8.0." in output:
                # 提取 IP
                import re
                ip_match = re.search(r'10\.8\.0\.\d+', output)
                if ip_match:
                    return {
                        "connected": True,
                        "local_ip": ip_match.group(0)
                    }
        return {"connected": False}
    except:
        return {"connected": False}


def test_server_connection(server_ip: str, port: int = 8788) -> dict:
    """測試伺服器連接"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((server_ip, port))
        sock.close()
        
        if result == 0:
            return {
                "reachable": True,
                "server_ip": server_ip,
                "port": port
            }
        else:
            return {
                "reachable": False,
                "server_ip": server_ip,
                "port": port,
                "error": "連接失敗"
            }
    except Exception as e:
        return {
            "reachable": False,
            "server_ip": server_ip,
            "port": port,
            "error": str(e)
        }


def test_http_connection(url: str) -> dict:
    """測試 HTTP 連接"""
    try:
        response = requests.get(url, timeout=5)
        return {
            "success": True,
            "url": url,
            "status_code": response.status_code,
            "reachable": True
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "url": url,
            "reachable": False,
            "error": "連接錯誤"
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "url": url,
            "reachable": False,
            "error": "連接超時"
        }
    except Exception as e:
        return {
            "success": False,
            "url": url,
            "reachable": False,
            "error": str(e)
        }


def check_environment_variables() -> dict:
    """檢查環境變數"""
    env_vars = {
        "WUCHANG_HEALTH_URL": os.getenv("WUCHANG_HEALTH_URL", ""),
        "WUCHANG_COPY_TO": os.getenv("WUCHANG_COPY_TO", ""),
        "WUCHANG_HUB_URL": os.getenv("WUCHANG_HUB_URL", ""),
        "WUCHANG_HUB_TOKEN": os.getenv("WUCHANG_HUB_TOKEN", ""),
    }
    
    return {
        "configured": {k: bool(v) for k, v in env_vars.items()},
        "values": {k: "***" if "TOKEN" in k else v for k, v in env_vars.items()}
    }


def main():
    """主函數"""
    print("=" * 70)
    print("連線狀態檢查")
    print("=" * 70)
    print()
    
    # 載入配置
    config_file = BASE_DIR / "network_interconnection_config.json"
    config = {}
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text(encoding="utf-8"))
        except:
            pass
    
    # 檢查 VPN 連接
    print("【VPN 連接狀態】")
    vpn_status = check_vpn_connection()
    if vpn_status.get("connected"):
        print(f"  ✓ VPN 已連接")
        print(f"  本機 IP: {vpn_status.get('local_ip', '未知')}")
    else:
        print("  ✗ VPN 未連接")
    print()
    
    # 測試伺服器連接
    server_ip = config.get("server_ip", "10.8.0.1")
    print(f"【伺服器連接測試】")
    print(f"  目標伺服器: {server_ip}")
    
    # TCP 連接測試
    tcp_test = test_server_connection(server_ip, 8788)
    if tcp_test.get("reachable"):
        print(f"  ✓ TCP 連接成功 ({server_ip}:8788)")
    else:
        print(f"  ✗ TCP 連接失敗: {tcp_test.get('error', '未知錯誤')}")
    
    # HTTP 連接測試
    health_url = config.get("health_url") or os.getenv("WUCHANG_HEALTH_URL", "")
    if not health_url:
        # 使用 VPN IP
        health_url = f"http://{server_ip}:8788/health"
    
    print(f"  健康檢查 URL: {health_url}")
    http_test = test_http_connection(health_url)
    if http_test.get("success"):
        print(f"  ✓ HTTP 連接成功 (狀態碼: {http_test.get('status_code')})")
    else:
        print(f"  ✗ HTTP 連接失敗: {http_test.get('error', '未知錯誤')}")
    print()
    
    # 環境變數檢查
    print("【環境變數配置】")
    env_status = check_environment_variables()
    for key, configured in env_status["configured"].items():
        status = "✓ 已設定" if configured else "✗ 未設定"
        value = env_status["values"][key]
        if configured:
            print(f"  {status} - {key}: {value}")
        else:
            print(f"  {status} - {key}")
    print()
    
    # 整體狀態
    print("【整體連線狀態】")
    vpn_ok = vpn_status.get("connected", False)
    tcp_ok = tcp_test.get("reachable", False)
    http_ok = http_test.get("success", False)
    
    if vpn_ok and tcp_ok and http_ok:
        print("  ✓ 連線暢通")
        print("  ✓ VPN 連接正常")
        print("  ✓ 伺服器連接正常")
        print("  ✓ HTTP 服務正常")
    elif vpn_ok and tcp_ok:
        print("  ⚠️  部分連線正常")
        print("  ✓ VPN 連接正常")
        print("  ✓ 伺服器連接正常")
        if not http_ok:
            print("  ✗ HTTP 服務不可用（可能正常，如果伺服器未運行 HTTP 服務）")
    elif vpn_ok:
        print("  ⚠️  VPN 已連接，但伺服器連接失敗")
        print("  ✓ VPN 連接正常")
        print("  ✗ 伺服器連接失敗")
    else:
        print("  ✗ 連線未暢通")
        print("  ✗ VPN 未連接")
        print("  ✗ 無法連接到伺服器")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
