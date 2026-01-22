#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diagnose_access_issues.py

診斷無法訪問的問題

全面檢查所有可能的原因
"""

import sys
import subprocess
import socket
import requests
from pathlib import Path
from typing import Dict, List, Tuple

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "cloudflared" / "config.yml"
CREDENTIALS_FILE = BASE_DIR / "cloudflared" / "credentials.json"


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌",
        "PROGRESS": "🔄"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")


def check_container_running(container_name: str) -> bool:
    """檢查容器是否運行"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5,
            encoding='utf-8',
            errors='replace'
        )
        return container_name in result.stdout
    except Exception:
        return False


def get_container_status(container_name: str) -> str:
    """取得容器狀態"""
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=5,
            encoding='utf-8',
            errors='replace'
        )
        return result.stdout.strip() if result.stdout.strip() else "未找到"
    except Exception:
        return "檢查失敗"


def get_container_logs(container_name: str, tail: int = 20) -> str:
    """取得容器日誌"""
    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", str(tail), container_name],
            capture_output=True,
            text=True,
            timeout=5,
            encoding='utf-8',
            errors='replace'
        )
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return f"無法取得日誌: {e}"


def check_dns_resolution(domain: str) -> Tuple[bool, str]:
    """檢查 DNS 解析"""
    try:
        ip = socket.gethostbyname(domain)
        return True, ip
    except socket.gaierror:
        return False, "無法解析"
    except Exception as e:
        return False, str(e)


def check_http_service(url: str, timeout: int = 5) -> Tuple[bool, str, int]:
    """檢查 HTTP 服務"""
    try:
        response = requests.get(url, timeout=timeout, verify=False, allow_redirects=True)
        return True, f"HTTP {response.status_code}", response.status_code
    except requests.exceptions.Timeout:
        return False, "連接超時", 0
    except requests.exceptions.ConnectionError:
        return False, "連接失敗", 0
    except requests.exceptions.SSLError:
        return True, "SSL 錯誤但可連接", 0
    except Exception as e:
        return False, str(e), 0


def check_local_service(host: str, port: int, timeout: int = 3) -> Tuple[bool, str]:
    """檢查本地服務"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0, "可連接" if result == 0 else "無法連接"
    except Exception as e:
        return False, str(e)


def main():
    """主函數"""
    print("=" * 70)
    print("訪問問題診斷")
    print("=" * 70)
    print()
    
    log("診斷所有域名無法訪問的問題", "INFO")
    print()
    
    # 要檢查的域名
    domains = {
        "www.wuchang.life": {"priority": "最高", "required": True},
        "app.wuchang.org.tw": {"priority": "一般", "required": False},
        "ai.wuchang.org.tw": {"priority": "一般", "required": False},
        "admin.wuchang.org.tw": {"priority": "一般", "required": False},
        "monitor.wuchang.org.tw": {"priority": "一般", "required": False}
    }
    
    # 1. 檢查 Cloudflare Tunnel 容器
    print("=" * 70)
    print("【1. Cloudflare Tunnel 容器狀態】")
    print("=" * 70)
    print()
    
    container_name = "wuchangv510-cloudflared-1"
    is_running = check_container_running(container_name)
    status = get_container_status(container_name)
    
    if is_running:
        log(f"容器運行中: {status}", "OK")
    else:
        log(f"容器未運行: {status}", "ERROR")
        log("需要啟動容器: docker start wuchangv510-cloudflared-1", "INFO")
        print()
    
    # 檢查日誌
    log("查看容器日誌...", "PROGRESS")
    logs = get_container_logs(container_name, tail=20)
    
    if "Cannot determine default configuration path" in logs:
        log("配置檔案路徑錯誤", "ERROR")
        log("解決方案: 確認 cloudflared/config.yml 存在", "INFO")
    elif "Cannot determine default origin certificate path" in logs:
        log("憑證檔案路徑錯誤", "ERROR")
        log("解決方案: 確認 cloudflared/credentials.json 存在", "INFO")
    elif "Registered tunnel connection" in logs:
        log("隧道連接已註冊", "OK")
    elif "Thank you for trying Cloudflare Tunnel" in logs:
        log("使用臨時隧道（未設定正式隧道）", "WARN")
        log("需要設定正式的命名隧道和 DNS 路由", "INFO")
    else:
        # 顯示最近日誌
        print("最近日誌:")
        for line in logs.split('\n')[-10:]:
            if line.strip():
                print(f"  {line}")
    print()
    
    # 2. 檢查配置檔案
    print("=" * 70)
    print("【2. 配置檔案檢查】")
    print("=" * 70)
    print()
    
    if CONFIG_FILE.exists():
        log(f"配置檔案存在: {CONFIG_FILE}", "OK")
        
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if '<tunnel-id>' in content:
                    log("Tunnel ID 未設定（仍是佔位符）", "ERROR")
                    log("需要更新為實際的 Tunnel ID", "INFO")
                else:
                    log("Tunnel ID 已設定", "OK")
                
                if 'www.wuchang.life' in content:
                    log("www.wuchang.life 已配置", "OK")
                else:
                    log("www.wuchang.life 未配置", "ERROR")
                
        except Exception as e:
            log(f"讀取配置檔案失敗: {e}", "ERROR")
    else:
        log("配置檔案不存在", "ERROR")
        log("需要建立 cloudflared/config.yml", "INFO")
    
    if CREDENTIALS_FILE.exists():
        log(f"憑證檔案存在: {CREDENTIALS_FILE}", "OK")
    else:
        log("憑證檔案不存在", "ERROR")
        log("需要執行: cloudflared tunnel login 並複製憑證", "INFO")
    print()
    
    # 3. 檢查 DNS 解析
    print("=" * 70)
    print("【3. DNS 解析檢查】")
    print("=" * 70)
    print()
    
    dns_results = {}
    for domain, info in domains.items():
        log(f"檢查 {domain} ({info['priority']}優先級)...", "PROGRESS")
        resolved, result = check_dns_resolution(domain)
        
        if resolved:
            log(f"  DNS 解析成功: {result}", "OK")
            dns_results[domain] = {"resolved": True, "ip": result}
        else:
            log(f"  DNS 解析失敗: {result}", "ERROR")
            dns_results[domain] = {"resolved": False, "error": result}
            
            if info["required"]:
                log(f"  這是必須能訪問的域名！", "ERROR")
        print()
    
    # 4. 檢查本地服務
    print("=" * 70)
    print("【4. 本地服務檢查】")
    print("=" * 70)
    print()
    
    local_services = {
        "wuchangv510-caddy-1": {"port": 80, "description": "Caddy (首頁)"},
        "wuchangv510-wuchang-web-1": {"port": 8069, "description": "Odoo ERP"},
        "wuchangv510-open-webui-1": {"port": 8080, "description": "Open WebUI"},
        "wuchangv510-portainer-1": {"port": 9000, "description": "Portainer"},
        "wuchangv510-uptime-kuma-1": {"port": 3001, "description": "Uptime Kuma"}
    }
    
    local_results = {}
    for service_name, info in local_services.items():
        is_running = check_container_running(service_name)
        accessible, result = check_local_service("localhost", info["port"], timeout=2)
        
        if is_running:
            if accessible:
                log(f"{service_name}: 運行中，本地端口 {info['port']} 可訪問", "OK")
                local_results[service_name] = {"running": True, "accessible": True}
            else:
                log(f"{service_name}: 運行中，但本地端口 {info['port']} 無法訪問", "WARN")
                local_results[service_name] = {"running": True, "accessible": False}
        else:
            log(f"{service_name}: 未運行", "ERROR")
            local_results[service_name] = {"running": False, "accessible": False}
    print()
    
    # 5. 檢查外網訪問
    print("=" * 70)
    print("【5. 外網訪問檢查】")
    print("=" * 70)
    print()
    
    service_results = {}
    for domain, info in domains.items():
        log(f"檢查 http://{domain}...", "PROGRESS")
        accessible, result, status_code = check_http_service(f"http://{domain}", timeout=3)
        
        if accessible:
            log(f"  服務可訪問: {result}", "OK")
            service_results[domain] = {"accessible": True, "status": status_code}
        else:
            log(f"  服務無法訪問: {result}", "ERROR")
            service_results[domain] = {"accessible": False, "error": result}
            
            if info["required"]:
                log(f"  這是必須能訪問的域名！", "ERROR")
        print()
    
    # 6. 問題診斷和解決方案
    print("=" * 70)
    print("【問題診斷和解決方案】")
    print("=" * 70)
    print()
    
    issues = []
    solutions = []
    
    # 檢查容器
    if not check_container_running(container_name):
        issues.append("Cloudflare Tunnel 容器未運行")
        solutions.append("執行: docker start wuchangv510-cloudflared-1")
    
    # 檢查配置檔案
    if not CONFIG_FILE.exists():
        issues.append("配置檔案不存在")
        solutions.append("建立 cloudflared/config.yml")
    
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            if '<tunnel-id>' in content:
                issues.append("Tunnel ID 未設定")
                solutions.append("更新 cloudflared/config.yml 中的 <tunnel-id> 為實際 ID")
    
    # 檢查憑證
    if not CREDENTIALS_FILE.exists():
        issues.append("憑證檔案不存在")
        solutions.append("執行: cloudflared tunnel login 並複製憑證到 cloudflared/credentials.json")
    
    # 檢查 DNS
    required_domain = "www.wuchang.life"
    if required_domain in dns_results and not dns_results[required_domain].get("resolved", False):
        issues.append(f"{required_domain} DNS 解析失敗")
        solutions.append(f"設定 DNS 路由: cloudflared tunnel route dns wuchang-tunnel {required_domain}")
    
    # 檢查本地服務
    caddy_running = local_results.get("wuchangv510-caddy-1", {}).get("running", False)
    if not caddy_running:
        issues.append("Caddy 容器未運行（首頁服務不可用）")
        solutions.append("執行: docker start wuchangv510-caddy-1")
    
    # 顯示問題和解決方案
    if issues:
        log("發現以下問題：", "ERROR")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
        print()
        
        log("解決方案：", "INFO")
        for i, solution in enumerate(solutions, 1):
            print(f"{i}. {solution}")
        print()
    else:
        log("未發現明顯問題", "OK")
        log("可能需要等待 DNS 傳播或檢查其他網路設定", "INFO")
        print()
    
    # 7. 優先修復步驟
    print("=" * 70)
    print("【優先修復步驟（確保 www.wuchang.life 可訪問）】")
    print("=" * 70)
    print()
    
    print("按照以下順序執行（必須）：")
    print()
    print("1. 確認容器運行：")
    print("   docker ps")
    print("   確認 wuchangv510-cloudflared-1 和 wuchangv510-caddy-1 都在運行")
    print()
    print("2. 檢查配置檔案：")
    print("   確認 cloudflared/config.yml 存在且 Tunnel ID 已設定")
    print("   確認 cloudflared/credentials.json 存在")
    print()
    print("3. 設定 DNS 路由（使用 Docker）：")
    print("   docker run --rm \\")
    print("     -v \"${env:USERPROFILE}\\.cloudflared:/home/nonroot/.cloudflared\" \\")
    print("     cloudflare/cloudflared:latest tunnel route dns wuchang-tunnel www.wuchang.life")
    print()
    print("4. 重啟容器：")
    print("   docker restart wuchangv510-cloudflared-1")
    print()
    print("5. 等待幾分鐘（DNS 傳播）")
    print()
    print("6. 驗證：")
    print("   nslookup www.wuchang.life")
    print("   curl http://www.wuchang.life")
    print()
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        log("操作已取消", "WARN")
        sys.exit(0)
    except Exception as e:
        log(f"發生錯誤: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)
