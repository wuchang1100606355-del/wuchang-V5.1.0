#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_homepage_config.py

檢查首頁配置

檢查首頁的 DNS 設定、服務配置和訪問狀態
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


def check_dns_resolution(domain: str):
    """檢查 DNS 解析"""
    try:
        ip = socket.gethostbyname(domain)
        return True, ip
    except socket.gaierror:
        return False, None
    except Exception as e:
        return False, str(e)


def check_http_service(url: str, timeout: int = 5):
    """檢查 HTTP 服務"""
    try:
        response = requests.get(url, timeout=timeout, verify=False, allow_redirects=True)
        return True, response.status_code, response.url
    except requests.exceptions.SSLError:
        return True, "SSL 連接", url
    except requests.exceptions.Timeout:
        return False, "超時", None
    except requests.exceptions.ConnectionError:
        return False, "連接失敗", None
    except Exception as e:
        return False, str(e), None


def check_cloudflare_config():
    """檢查 Cloudflare 配置"""
    config_file = BASE_DIR / "cloudflared" / "config.yml"
    
    homepage_domains = []
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 查找所有域名配置
                for line in content.split('\n'):
                    if 'hostname:' in line:
                        domain = line.split('hostname:')[-1].strip()
                        if domain and not domain.startswith('#'):
                            homepage_domains.append(domain)
        except Exception as e:
            log(f"讀取配置檔案時發生錯誤: {e}", "ERROR")
    
    return homepage_domains


def check_homepage_file():
    """檢查首頁檔案"""
    index_file = BASE_DIR / "index.html"
    
    if index_file.exists():
        return True, index_file
    else:
        return False, None


def check_docker_service_for_homepage():
    """檢查是否有服務提供首頁"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}|{{.Ports}}"],
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8',
            errors='replace'
        )
        
        # 檢查是否有 Web 伺服器容器（Nginx, Apache, Caddy 等）
        web_servers = []
        for line in result.stdout.strip().split('\n'):
            if 'caddy' in line.lower() or 'nginx' in line.lower() or 'apache' in line.lower() or 'httpd' in line.lower():
                parts = line.split('|', 1)
                if len(parts) == 2:
                    web_servers.append({
                        "name": parts[0],
                        "ports": parts[1]
                    })
        
        return web_servers
    except Exception as e:
        log(f"檢查容器時發生錯誤: {e}", "ERROR")
        return []


def main():
    """主函數"""
    print("=" * 70)
    print("首頁配置檢查")
    print("=" * 70)
    print()
    
    # 可能的首頁域名（首頁必須是 www.wuchang.life）
    homepage_domains = [
        "www.wuchang.life",  # 首頁主域名（必須）
        "wuchang.life",      # 無 www 的域名（可選）
    ]
    
    # 1. 檢查首頁檔案
    print("=" * 70)
    print("【1. 首頁檔案】")
    print("=" * 70)
    print()
    
    homepage_exists, homepage_file = check_homepage_file()
    
    if homepage_exists:
        log(f"首頁檔案存在: {homepage_file}", "OK")
        log(f"檔案大小: {homepage_file.stat().st_size / 1024:.2f} KB", "INFO")
    else:
        log("首頁檔案不存在: index.html", "WARN")
    print()
    
    # 2. 檢查 Cloudflare 配置
    print("=" * 70)
    print("【2. Cloudflare 配置】")
    print("=" * 70)
    print()
    
    configured_domains = check_cloudflare_config()
    
    if configured_domains:
        log(f"配置的域名: {len(configured_domains)} 個", "OK")
        for domain in configured_domains:
            print(f"  - {domain}")
    else:
        log("未找到配置的域名", "WARN")
    
    # 檢查是否有首頁域名
    homepage_in_config = [d for d in configured_domains if 'app' not in d and 'ai' not in d and 'admin' not in d and 'monitor' not in d]
    
    if homepage_in_config:
        log(f"找到首頁相關域名: {len(homepage_in_config)} 個", "OK")
        for domain in homepage_in_config:
            print(f"  - {domain}")
    else:
        log("未找到首頁域名配置", "WARN")
        log("建議新增首頁域名到 Cloudflare 配置", "INFO")
    print()
    
    # 3. 檢查 Web 伺服器
    print("=" * 70)
    print("【3. Web 伺服器容器】")
    print("=" * 70)
    print()
    
    web_servers = check_docker_service_for_homepage()
    
    if web_servers:
        log(f"找到 Web 伺服器容器: {len(web_servers)} 個", "OK")
        for server in web_servers:
            print(f"  - {server['name']}")
            print(f"    端口: {server['ports']}")
    else:
        log("未找到 Web 伺服器容器（Caddy、Nginx 等）", "WARN")
    print()
    
    # 4. 檢查 DNS 解析
    print("=" * 70)
    print("【4. DNS 解析檢查】")
    print("=" * 70)
    print()
    
    dns_results = {}
    
    # 檢查已配置的域名
    all_domains_to_check = list(set(homepage_domains + configured_domains))
    
    for domain in all_domains_to_check:
        log(f"檢查 {domain}...", "PROGRESS")
        resolved, result = check_dns_resolution(domain)
        
        if resolved:
            log(f"  DNS 解析成功: {result}", "OK")
            dns_results[domain] = {"resolved": True, "ip": result}
        else:
            log(f"  DNS 解析失敗: {result}", "ERROR")
            dns_results[domain] = {"resolved": False, "error": result}
        print()
    
    # 5. 檢查服務訪問
    print("=" * 70)
    print("【5. 服務訪問檢查】")
    print("=" * 70)
    print()
    
    service_results = {}
    
    for domain in all_domains_to_check:
        log(f"檢查 https://{domain}...", "PROGRESS")
        accessible, result, final_url = check_http_service(f"https://{domain}", timeout=3)
        
        if accessible:
            log(f"  服務可訪問: {result}", "OK")
            if final_url:
                log(f"  最終 URL: {final_url}", "INFO")
            service_results[domain] = {"accessible": True, "status": result, "url": final_url}
        else:
            log(f"  服務無法訪問: {result}", "WARN")
            service_results[domain] = {"accessible": False, "error": result}
        print()
    
    # 6. 總結和建議
    print("=" * 70)
    print("【總結和建議】")
    print("=" * 70)
    print()
    
    # 統計
    total_domains = len(all_domains_to_check)
    resolved_count = sum(1 for r in dns_results.values() if r.get("resolved", False))
    accessible_count = sum(1 for r in service_results.values() if r.get("accessible", False))
    
    log(f"DNS 解析: {resolved_count}/{total_domains} 個域名可解析", 
        "OK" if resolved_count == total_domains else "WARN")
    
    log(f"服務訪問: {accessible_count}/{total_domains} 個服務可訪問",
        "OK" if accessible_count == total_domains else "WARN")
    
    print()
    
    # 建議
    print("建議：")
    print()
    
    if not homepage_in_config:
        print("1. 新增首頁域名到 Cloudflare Tunnel 配置")
        print("   例如：")
        print("   - hostname: wuchang.org.tw")
        print("     service: http://wuchangv510-caddy-1:80")
        print()
    
    if not web_servers:
        print("2. 確認 Web 伺服器容器運行中（例如 Caddy）")
        print("   並確認首頁檔案已掛載到容器中")
        print()
    
    if resolved_count < total_domains:
        print("3. 配置 DNS 路由：")
        for domain in all_domains_to_check:
            if not dns_results.get(domain, {}).get("resolved", False):
                print(f"   cloudflared tunnel route dns wuchang-tunnel {domain}")
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
