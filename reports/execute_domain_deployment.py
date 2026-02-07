#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
execute_domain_deployment.py

執行網域部署

功能：
1. 檢查當前部署狀態
2. 驗證 DNS 配置
3. 檢查服務連接
4. 生成配置檔案
5. 執行部署
"""

import sys
import subprocess
import json
import socket
from pathlib import Path
from typing import Dict, List, Tuple, Optional

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


def check_container(container_name: str) -> Tuple[bool, str]:
    """檢查容器狀態"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}\t{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=5,
            encoding='utf-8',
            errors='replace'
        )
        if container_name in result.stdout:
            return True, result.stdout.strip()
        return False, "未運行"
    except Exception as e:
        return False, str(e)


def check_dns(domain: str) -> Tuple[bool, Optional[str]]:
    """檢查 DNS 解析"""
    try:
        ip = socket.gethostbyname(domain)
        return True, ip
    except socket.gaierror:
        return False, None


def check_port(host: str, port: int) -> bool:
    """檢查端口是否開放"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


def check_cloudflared_config() -> Tuple[bool, str]:
    """檢查 Cloudflare Tunnel 配置"""
    config_file = BASE_DIR / "cloudflared" / "config.yml"
    
    if not config_file.exists():
        return False, "配置文件不存在"
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if '<tunnel-id>' in content:
                return False, "需要替換 <tunnel-id> 為實際的隧道 ID"
            if 'credentials-file' not in content:
                return False, "缺少 credentials-file 配置"
        return True, "配置正常"
    except Exception as e:
        return False, str(e)


def check_credentials_file() -> Tuple[bool, str]:
    """檢查 Cloudflare 憑證檔案"""
    creds_file = BASE_DIR / "cloudflared" / "credentials.json"
    
    if not creds_file.exists():
        return False, "憑證檔案不存在"
    
    try:
        with open(creds_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'AccountTag' not in data or 'TunnelSecret' not in data:
                return False, "憑證檔案格式不正確"
        return True, "憑證檔案正常"
    except Exception as e:
        return False, str(e)


def check_caddy_config() -> Tuple[bool, str]:
    """檢查 Caddy 配置"""
    # 檢查 Caddyfile 是否存在（可能在多個位置）
    possible_locations = [
        BASE_DIR / "caddy" / "Caddyfile",
        BASE_DIR / "Caddyfile",
        Path("C:/caddy/Caddyfile")
    ]
    
    for caddyfile in possible_locations:
        if caddyfile.exists():
            return True, f"找到配置文件: {caddyfile}"
    
    return False, "未找到 Caddyfile，需要創建配置"


def generate_deployment_report():
    """產生部署報告"""
    print("=" * 70)
    print("網域部署狀態檢查")
    print("=" * 70)
    print()
    
    # 檢查容器
    log("檢查容器狀態...", "PROGRESS")
    print()
    
    containers = {
        "wuchangv510-caddy-1": "Caddy 反向代理",
        "wuchangv510-cloudflared-1": "Cloudflare Tunnel",
        "wuchangv510-wuchang-web-1": "Odoo ERP",
        "wuchangv510-db-1": "PostgreSQL 資料庫",
        "wuchangv510-portainer-1": "Portainer",
        "wuchangv510-uptime-kuma-1": "Uptime Kuma"
    }
    
    container_status = {}
    for container, description in containers.items():
        running, status = check_container(container)
        container_status[container] = {"running": running, "status": status, "description": description}
        
        if running:
            log(f"{description} ({container}): {status}", "OK")
        else:
            log(f"{description} ({container}): {status}", "ERROR")
    
    print()
    
    # 檢查 Cloudflare Tunnel 配置
    log("檢查 Cloudflare Tunnel 配置...", "PROGRESS")
    print()
    
    config_ok, config_msg = check_cloudflared_config()
    if config_ok:
        log(f"配置檔案: {config_msg}", "OK")
    else:
        log(f"配置檔案: {config_msg}", "ERROR")
    
    creds_ok, creds_msg = check_credentials_file()
    if creds_ok:
        log(f"憑證檔案: {creds_msg}", "OK")
    else:
        log(f"憑證檔案: {creds_msg}", "WARN")
    
    print()
    
    # 檢查 Caddy 配置
    log("檢查 Caddy 配置...", "PROGRESS")
    print()
    
    caddy_ok, caddy_msg = check_caddy_config()
    if caddy_ok:
        log(f"Caddy: {caddy_msg}", "OK")
    else:
        log(f"Caddy: {caddy_msg}", "WARN")
    
    print()
    
    # 檢查 DNS（可選）
    log("檢查 DNS 解析（可選）...", "PROGRESS")
    print()
    
    test_domains = [
        "app.wuchang.org.tw",
        "ai.wuchang.org.tw",
        "admin.wuchang.org.tw"
    ]
    
    for domain in test_domains:
        dns_ok, ip = check_dns(domain)
        if dns_ok:
            log(f"{domain} → {ip}", "OK")
        else:
            log(f"{domain} → 無法解析（可能尚未配置 DNS）", "WARN")
    
    print()
    
    # 產生總結
    print("=" * 70)
    print("【部署狀態總結】")
    print("=" * 70)
    print()
    
    running_count = sum(1 for c in container_status.values() if c["running"])
    total_count = len(container_status)
    
    log(f"容器狀態: {running_count}/{total_count} 運行中", "INFO")
    
    if config_ok and creds_ok:
        log("Cloudflare Tunnel 配置: 正常", "OK")
    else:
        log("Cloudflare Tunnel 配置: 需要完善", "WARN")
    
    if caddy_ok:
        log("Caddy 配置: 正常", "OK")
    else:
        log("Caddy 配置: 需要創建", "WARN")
    
    print()
    print("=" * 70)
    print("【下一步建議】")
    print("=" * 70)
    print()
    
    if not config_ok or not creds_ok:
        print("1. 完成 Cloudflare Tunnel 設定：")
        print("   - 建立 Cloudflare Tunnel")
        print("   - 下載 credentials.json")
        print("   - 更新 config.yml 中的 tunnel-id")
        print()
    
    if not caddy_ok:
        print("2. 創建 Caddyfile：")
        print("   - 使用 domain_deployment_helper.py 生成範本")
        print("   - 或參考 DOMAIN_DEPLOYMENT_PLAN.md")
        print()
    
    if running_count < total_count:
        print("3. 啟動未運行的容器：")
        for container, info in container_status.items():
            if not info["running"]:
                print(f"   - {container}")
        print()
    
    print("4. 配置 DNS：")
    print("   - 在 Cloudflare DNS 設定中添加 CNAME 記錄")
    print("   - 指向 Cloudflare Tunnel")
    print()
    
    print("5. 驗證部署：")
    print("   - 訪問 https://app.wuchang.org.tw")
    print("   - 檢查 SSL 證書")
    print("   - 測試服務連接")
    print()
    
    # 產生報告檔案
    report = {
        "timestamp": str(Path(__file__).stat().st_mtime),
        "containers": container_status,
        "cloudflared": {
            "config": config_ok,
            "credentials": creds_ok
        },
        "caddy": {
            "config": caddy_ok
        }
    }
    
    report_file = BASE_DIR / "domain_deployment_status.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    log(f"部署狀態報告已儲存: {report_file}", "OK")
    
    return 0


def main():
    """主函數"""
    return generate_deployment_report()


if __name__ == "__main__":
    sys.exit(main())
