#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
request_server_response.py

向伺服器提出回應要求

功能：
- 測試多種連接方式
- 發送 HTTP 請求
- 測試不同端口
- 生成回應報告
"""

import sys
import json
import socket
import requests
import time
from pathlib import Path
from typing import Dict, Any, List

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def test_port(host: str, port: int, timeout: float = 3.0) -> Dict[str, Any]:
    """測試端口連接"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        start_time = time.time()
        result = sock.connect_ex((host, port))
        elapsed = (time.time() - start_time) * 1000
        sock.close()
        
        return {
            "success": result == 0,
            "host": host,
            "port": port,
            "reachable": result == 0,
            "response_time_ms": round(elapsed, 2) if result == 0 else None,
            "error": None if result == 0 else f"連接失敗 (錯誤碼: {result})"
        }
    except socket.timeout:
        return {
            "success": False,
            "host": host,
            "port": port,
            "reachable": False,
            "error": "連接超時"
        }
    except Exception as e:
        return {
            "success": False,
            "host": host,
            "port": port,
            "reachable": False,
            "error": str(e)
        }


def send_http_request(url: str, method: str = "GET", timeout: float = 5.0) -> Dict[str, Any]:
    """發送 HTTP 請求"""
    try:
        start_time = time.time()
        
        if method.upper() == "GET":
            response = requests.get(url, timeout=timeout, allow_redirects=True)
        elif method.upper() == "POST":
            response = requests.post(url, timeout=timeout, allow_redirects=True)
        elif method.upper() == "HEAD":
            response = requests.head(url, timeout=timeout, allow_redirects=True)
        else:
            response = requests.request(method, url, timeout=timeout, allow_redirects=True)
        
        elapsed = (time.time() - start_time) * 1000
        
        return {
            "success": True,
            "url": url,
            "method": method,
            "status_code": response.status_code,
            "response_time_ms": round(elapsed, 2),
            "headers": dict(response.headers),
            "content_length": len(response.content),
            "content_preview": response.text[:200] if response.text else "",
            "reachable": True
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "url": url,
            "method": method,
            "reachable": False,
            "error": "連接錯誤（服務可能未運行）"
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "url": url,
            "method": method,
            "reachable": False,
            "error": "請求超時"
        }
    except requests.exceptions.SSLError as e:
        return {
            "success": False,
            "url": url,
            "method": method,
            "reachable": False,
            "error": f"SSL 錯誤: {str(e)[:100]}"
        }
    except Exception as e:
        return {
            "success": False,
            "url": url,
            "method": method,
            "reachable": False,
            "error": str(e)
        }


def scan_common_ports(host: str) -> List[Dict[str, Any]]:
    """掃描常見端口"""
    common_ports = [
        22,    # SSH
        80,    # HTTP
        443,   # HTTPS
        8788,  # 控制中心
        8799,  # Little J Hub
        8443,  # 路由器 HTTPS
        8888,  # OpenVPN / 其他服務
        3306,  # MySQL
        5432,  # PostgreSQL
        8080,  # HTTP 替代端口
    ]
    
    results = []
    print(f"正在掃描 {host} 的常見端口...")
    
    for port in common_ports:
        result = test_port(host, port, timeout=2.0)
        results.append(result)
        if result["success"]:
            print(f"  ✓ 端口 {port} 開放 (回應時間: {result.get('response_time_ms', 0)}ms)")
        else:
            print(f"  ✗ 端口 {port} 關閉")
    
    return results


def request_server_response(server_ip: str = None, server_ddns: str = None) -> Dict[str, Any]:
    """向伺服器提出回應要求"""
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "server_ip": server_ip,
        "server_ddns": server_ddns,
        "tests": {}
    }
    
    # 確定目標主機
    target_host = server_ip or server_ddns or "10.8.0.1"
    
    print("=" * 70)
    print("向伺服器提出回應要求")
    print("=" * 70)
    print(f"目標伺服器: {target_host}")
    print()
    
    # 1. 端口掃描
    print("【測試 1：端口掃描】")
    port_results = scan_common_ports(target_host)
    report["tests"]["port_scan"] = port_results
    
    open_ports = [r for r in port_results if r["success"]]
    if open_ports:
        print(f"\n✓ 發現 {len(open_ports)} 個開放端口")
    else:
        print("\n✗ 未發現開放端口")
    print()
    
    # 2. HTTP 請求測試
    print("【測試 2：HTTP 請求測試】")
    http_urls = [
        f"http://{target_host}:8788/",
        f"http://{target_host}:8788/health",
        f"http://{target_host}:8799/",
        f"http://{target_host}:8799/health",
        f"http://{target_host}:80/",
        f"https://{target_host}:8443/",
    ]
    
    if server_ddns:
        http_urls.extend([
            f"https://{server_ddns}:8443/",
            f"https://{server_ddns}:8443/health",
        ])
    
    http_results = []
    for url in http_urls:
        print(f"  測試: {url}")
        result = send_http_request(url, method="GET", timeout=3.0)
        http_results.append(result)
        
        if result["success"]:
            print(f"    ✓ 回應成功 (狀態碼: {result['status_code']}, 時間: {result['response_time_ms']}ms)")
            if result.get("content_preview"):
                print(f"    內容預覽: {result['content_preview'][:100]}...")
        else:
            print(f"    ✗ 回應失敗: {result.get('error', '未知錯誤')}")
    
    report["tests"]["http_requests"] = http_results
    print()
    
    # 3. 特定服務測試
    print("【測試 3：特定服務測試】")
    
    # 控制中心健康檢查
    if any(r["port"] == 8788 and r["success"] for r in port_results):
        health_url = f"http://{target_host}:8788/health"
        print(f"  控制中心健康檢查: {health_url}")
        health_result = send_http_request(health_url, timeout=3.0)
        report["tests"]["control_center_health"] = health_result
        
        if health_result["success"]:
            print(f"    ✓ 健康檢查成功 (狀態碼: {health_result['status_code']})")
            try:
                health_data = json.loads(health_result.get("content_preview", "{}"))
                print(f"    健康狀態: {json.dumps(health_data, ensure_ascii=False, indent=6)[:200]}")
            except:
                pass
        else:
            print(f"    ✗ 健康檢查失敗: {health_result.get('error')}")
    
    # Little J Hub 測試
    if any(r["port"] == 8799 and r["success"] for r in port_results):
        hub_url = f"http://{target_host}:8799/health"
        print(f"  Little J Hub 健康檢查: {hub_url}")
        hub_result = send_http_request(hub_url, timeout=3.0)
        report["tests"]["hub_health"] = hub_result
        
        if hub_result["success"]:
            print(f"    ✓ Hub 健康檢查成功 (狀態碼: {hub_result['status_code']})")
        else:
            print(f"    ✗ Hub 健康檢查失敗: {hub_result.get('error')}")
    
    print()
    
    # 4. 生成摘要
    print("【回應摘要】")
    successful_requests = [r for r in http_results if r["success"]]
    
    if successful_requests:
        print(f"  ✓ 成功回應: {len(successful_requests)}/{len(http_results)} 個請求")
        print("  可用的服務:")
        for req in successful_requests:
            print(f"    - {req['url']} (狀態碼: {req['status_code']})")
    else:
        print("  ✗ 所有 HTTP 請求均失敗")
        print("  可能原因:")
        print("    1. 伺服器端服務未運行")
        print("    2. 防火牆阻擋連接")
        print("    3. 服務配置錯誤")
    
    print()
    
    # 5. 建議
    print("【建議】")
    if open_ports:
        print(f"  ✓ 發現 {len(open_ports)} 個開放端口，網路連接正常")
    else:
        print("  ✗ 未發現開放端口，請檢查:")
        print("    1. VPN 連接是否正常")
        print("    2. 伺服器端服務是否運行")
        print("    3. 防火牆設定")
    
    if successful_requests:
        print("  ✓ 部分服務可正常回應")
    else:
        print("  ✗ 服務無回應，請檢查伺服器端配置")
    
    print()
    print("=" * 70)
    
    return report


def main():
    """主函數"""
    # 載入配置
    config_file = BASE_DIR / "network_interconnection_config.json"
    config = {}
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text(encoding="utf-8"))
        except:
            pass
    
    server_ip = config.get("server_ip", "10.8.0.1")
    server_ddns = config.get("server_ddns", "")
    
    # 執行回應請求
    report = request_server_response(server_ip=server_ip, server_ddns=server_ddns)
    
    # 儲存報告
    report_file = BASE_DIR / "server_response_report.json"
    report_file.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"詳細報告已儲存到: {report_file}")


if __name__ == "__main__":
    main()
