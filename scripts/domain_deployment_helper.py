#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
domain_deployment_helper.py

網域部署輔助工具

功能：
- 檢查 DNS 配置
- 驗證服務連接
- 生成配置檔案範本
- 測試域名解析
"""

import sys
import subprocess
import json
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


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    colors = {
        "INFO": "\033[36m",
        "SUCCESS": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "RESET": "\033[0m"
    }
    color = colors.get(level, colors["INFO"])
    reset = colors["RESET"]
    print(f"{color}[{level}]{reset} {message}")


def check_dns(domain: str) -> Tuple[bool, str]:
    """檢查 DNS 解析"""
    try:
        import socket
        ip = socket.gethostbyname(domain)
        return True, ip
    except socket.gaierror:
        return False, "無法解析"


def check_service(domain: str, port: int = 443, use_https: bool = True) -> Tuple[bool, str]:
    """檢查服務連接"""
    protocol = "https" if use_https else "http"
    url = f"{protocol}://{domain}:{port}" if port not in [80, 443] else f"{protocol}://{domain}"
    
    try:
        response = requests.get(url, timeout=5, verify=False)
        return True, f"HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, str(e)


def check_container(container_name: str) -> bool:
    """檢查容器狀態"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return container_name in result.stdout
    except:
        return False


def generate_caddyfile_template(domains: Dict[str, Dict]) -> str:
    """生成 Caddyfile 範本"""
    template = """# Caddyfile 配置範本
# 自動生成時間: {timestamp}

{{
    email your-email@example.com
    log {{
        output file /var/log/caddy/access.log
        format json
    }}
}}

"""
    
    for domain, config in domains.items():
        service = config.get("service", "localhost")
        port = config.get("port", 80)
        auth = config.get("auth", False)
        websocket = config.get("websocket", False)
        
        template += f"# {config.get('description', domain)}\n"
        template += f"{domain} {{\n"
        
        if auth:
            template += "    basicauth {\n"
            template += f"        {config.get('auth_user', 'admin')} $2a$14$請替換為實際密碼雜湊\n"
            template += "    }\n"
        
        template += f"    reverse_proxy {service}:{port} {{\n"
        template += "        header_up Host {host}\n"
        template += "        header_up X-Real-IP {remote}\n"
        template += "        header_up X-Forwarded-For {remote}\n"
        template += "        header_up X-Forwarded-Proto {scheme}\n"
        template += "    }\n"
        
        if websocket:
            template += "\n    @websocket {\n"
            template += "        header Connection *Upgrade*\n"
            template += "        header Upgrade websocket\n"
            template += "    }\n"
            template += f"    reverse_proxy @websocket {service}:{port}\n"
        
        template += "\n    header {\n"
        template += "        Strict-Transport-Security \"max-age=31536000; includeSubDomains\"\n"
        template += "        X-Content-Type-Options \"nosniff\"\n"
        template += "        X-Frame-Options \"SAMEORIGIN\"\n"
        template += "    }\n"
        template += "}\n\n"
    
    template += "# 預設處理\n"
    template += ":80, :443 {\n"
    template += "    respond \"404 Not Found\" 404\n"
    template += "}\n"
    
    from datetime import datetime
    return template.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def generate_cloudflared_config(domains: Dict[str, Dict]) -> str:
    """生成 Cloudflare Tunnel 配置範本"""
    template = """# Cloudflare Tunnel 配置範本
# 自動生成時間: {timestamp}
# 請替換 <tunnel-id> 為實際的 Tunnel ID

tunnel: <tunnel-id>
credentials-file: /etc/cloudflared/credentials.json

ingress:
"""
    
    for domain, config in domains.items():
        port = config.get("port", 80)
        template += f"  # {config.get('description', domain)}\n"
        template += f"  - hostname: {domain}\n"
        template += f"    service: http://localhost:{port}\n\n"
    
    template += "  # 預設規則\n"
    template += "  - service: http_status:404\n"
    
    from datetime import datetime
    return template.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def main():
    """主函數"""
    print("=" * 60)
    print("網域部署輔助工具")
    print("=" * 60)
    print()
    
    # 預設域名配置
    domains = {
        "app.wuchang.org.tw": {
            "description": "Odoo ERP 系統",
            "service": "wuchangv510-wuchang-web-1",
            "port": 8069,
            "auth": False,
            "websocket": False
        },
        "ai.wuchang.org.tw": {
            "description": "Open WebUI (AI 介面)",
            "service": "wuchangv510-open-webui-1",
            "port": 8080,
            "auth": False,
            "websocket": True
        },
        "admin.wuchang.org.tw": {
            "description": "Portainer (容器管理)",
            "service": "wuchangv510-portainer-1",
            "port": 9000,
            "auth": True,
            "auth_user": "admin",
            "websocket": False
        },
        "monitor.wuchang.org.tw": {
            "description": "Uptime Kuma (監控)",
            "service": "wuchangv510-uptime-kuma-1",
            "port": 3001,
            "auth": True,
            "auth_user": "monitor",
            "websocket": False
        },
        "caddy.wuchang.org.tw": {
            "description": "Caddy UI (管理介面)",
            "service": "wuchangv510-caddy-ui-1",
            "port": 80,
            "auth": True,
            "auth_user": "caddy",
            "websocket": False
        }
    }
    
    print("請選擇操作：")
    print("1. 檢查 DNS 解析")
    print("2. 檢查服務連接")
    print("3. 檢查容器狀態")
    print("4. 生成 Caddyfile 範本")
    print("5. 生成 Cloudflare Tunnel 配置範本")
    print("6. 完整檢查")
    print()
    
    choice = input("請選擇 (1-6): ").strip()
    
    if choice == "1":
        print()
        log("檢查 DNS 解析...", "INFO")
        print()
        for domain in domains.keys():
            success, result = check_dns(domain)
            if success:
                log(f"{domain} → {result}", "SUCCESS")
            else:
                log(f"{domain} → {result}", "ERROR")
    
    elif choice == "2":
        print()
        log("檢查服務連接...", "INFO")
        print()
        for domain, config in domains.items():
            port = config.get("port", 443)
            use_https = port == 443
            success, result = check_service(domain, port, use_https)
            if success:
                log(f"{domain} → {result}", "SUCCESS")
            else:
                log(f"{domain} → {result}", "ERROR")
    
    elif choice == "3":
        print()
        log("檢查容器狀態...", "INFO")
        print()
        containers = [
            "wuchangv510-caddy-1",
            "wuchangv510-wuchang-web-1",
            "wuchangv510-open-webui-1",
            "wuchangv510-portainer-1",
            "wuchangv510-uptime-kuma-1",
            "wuchangv510-cloudflared-1"
        ]
        for container in containers:
            if check_container(container):
                log(f"{container} → 運行中", "SUCCESS")
            else:
                log(f"{container} → 未運行", "ERROR")
    
    elif choice == "4":
        print()
        log("生成 Caddyfile 範本...", "INFO")
        caddyfile = generate_caddyfile_template(domains)
        output_file = Path("Caddyfile.template")
        output_file.write_text(caddyfile, encoding="utf-8")
        log(f"已生成: {output_file}", "SUCCESS")
        print()
        print(caddyfile)
    
    elif choice == "5":
        print()
        log("生成 Cloudflare Tunnel 配置範本...", "INFO")
        config = generate_cloudflared_config(domains)
        output_file = Path("cloudflared.config.template.yml")
        output_file.write_text(config, encoding="utf-8")
        log(f"已生成: {output_file}", "SUCCESS")
        print()
        print(config)
    
    elif choice == "6":
        print()
        log("執行完整檢查...", "INFO")
        print()
        
        # 檢查容器
        log("1. 檢查容器狀態", "INFO")
        containers = [
            "wuchangv510-caddy-1",
            "wuchangv510-wuchang-web-1",
            "wuchangv510-open-webui-1",
            "wuchangv510-portainer-1",
            "wuchangv510-uptime-kuma-1"
        ]
        for container in containers:
            if check_container(container):
                log(f"  ✓ {container}", "SUCCESS")
            else:
                log(f"  ✗ {container}", "ERROR")
        
        print()
        
        # 檢查 DNS
        log("2. 檢查 DNS 解析", "INFO")
        for domain in domains.keys():
            success, result = check_dns(domain)
            if success:
                log(f"  ✓ {domain} → {result}", "SUCCESS")
            else:
                log(f"  ✗ {domain} → {result}", "ERROR")
        
        print()
        
        # 檢查服務
        log("3. 檢查服務連接", "INFO")
        for domain, config in domains.items():
            port = config.get("port", 443)
            use_https = port == 443
            success, result = check_service(domain, port, use_https)
            if success:
                log(f"  ✓ {domain} → {result}", "SUCCESS")
            else:
                log(f"  ✗ {domain} → {result}", "WARNING")
    
    else:
        log("無效的選擇", "ERROR")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        log("操作已取消", "WARNING")
        sys.exit(0)
    except Exception as e:
        log(f"發生錯誤: {e}", "ERROR")
        sys.exit(1)
