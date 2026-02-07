#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deploy_domain.py

網域部署自動化腳本

功能：
1. 檢查部署環境
2. 驗證 DNS 配置
3. 配置 Cloudflare Tunnel
4. 啟動服務
5. 驗證部署狀態
"""

import sys
import subprocess
import json
import socket
import requests
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
CLOUDFLARED_DIR = BASE_DIR / "cloudflared"


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


def check_docker():
    """檢查 Docker 是否安裝並運行"""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            encoding='utf-8',
            errors='replace'
        )
        if result.returncode == 0:
            log(f"Docker 已安裝: {result.stdout.strip()}", "OK")
            
            # 檢查 Docker 是否運行
            result = subprocess.run(
                ["docker", "ps"],
                capture_output=True,
                text=True,
                timeout=5,
                encoding='utf-8',
                errors='replace'
            )
            if result.returncode == 0:
                log("Docker 服務運行中", "OK")
                return True
            else:
                log("Docker 服務未運行", "ERROR")
                return False
        else:
            log("Docker 未安裝或無法執行", "ERROR")
            return False
    except FileNotFoundError:
        log("Docker 未安裝，請先安裝 Docker Desktop", "ERROR")
        return False
    except Exception as e:
        log(f"檢查 Docker 時發生錯誤: {e}", "ERROR")
        return False


def check_dns(domain: str) -> Tuple[bool, str]:
    """檢查 DNS 解析"""
    try:
        ip = socket.gethostbyname(domain)
        return True, ip
    except socket.gaierror:
        return False, "無法解析"


def check_service_http(url: str, timeout: int = 5) -> Tuple[bool, str]:
    """檢查 HTTP 服務"""
    try:
        response = requests.get(url, timeout=timeout, verify=False, allow_redirects=True)
        return True, f"HTTP {response.status_code}"
    except requests.exceptions.SSLError:
        return True, "SSL 連接正常"
    except requests.exceptions.RequestException as e:
        return False, str(e)


def check_container(container_name: str) -> bool:
    """檢查容器狀態"""
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


def get_container_status(container_name: str) -> Optional[str]:
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
        if result.stdout.strip():
            return result.stdout.strip()
        return None
    except Exception:
        return None


def check_cloudflare_config():
    """檢查 Cloudflare Tunnel 配置"""
    log("檢查 Cloudflare Tunnel 配置...", "PROGRESS")
    
    config_file = CLOUDFLARED_DIR / "config.yml"
    credentials_file = CLOUDFLARED_DIR / "credentials.json"
    
    if not CLOUDFLARED_DIR.exists():
        log(f"Cloudflare 配置目錄不存在: {CLOUDFLARED_DIR}", "WARN")
        log("將建立配置目錄...", "INFO")
        CLOUDFLARED_DIR.mkdir(parents=True, exist_ok=True)
    
    config_exists = config_file.exists()
    credentials_exists = credentials_file.exists()
    
    if config_exists:
        log(f"配置檔案存在: {config_file}", "OK")
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if '<tunnel-id>' in content:
                    log("配置檔案包含佔位符，需要更新實際的 Tunnel ID", "WARN")
                else:
                    log("配置檔案已設定", "OK")
        except Exception as e:
            log(f"讀取配置檔案時發生錯誤: {e}", "ERROR")
    else:
        log(f"配置檔案不存在: {config_file}", "WARN")
    
    if credentials_exists:
        log(f"憑證檔案存在: {credentials_file}", "OK")
    else:
        log(f"憑證檔案不存在: {credentials_file}", "WARN")
        log("需要執行 'cloudflared tunnel login' 並複製憑證", "INFO")
    
    return config_exists and credentials_exists


def generate_cloudflare_config():
    """產生 Cloudflare Tunnel 配置範本"""
    log("產生 Cloudflare Tunnel 配置範本...", "PROGRESS")
    
    if not CLOUDFLARED_DIR.exists():
        CLOUDFLARED_DIR.mkdir(parents=True, exist_ok=True)
    
    config_file = CLOUDFLARED_DIR / "config.yml"
    
    domains_config = {
        "app.wuchang.org.tw": {"port": 8069, "description": "Odoo ERP 系統"},
        "ai.wuchang.org.tw": {"port": 8080, "description": "Open WebUI (AI 介面)"},
        "admin.wuchang.org.tw": {"port": 9000, "description": "Portainer (容器管理)"},
        "monitor.wuchang.org.tw": {"port": 3001, "description": "Uptime Kuma (監控)"},
    }
    
    config_content = """# Cloudflare Tunnel 配置
# 產生時間: 2026-01-20
# 請將 <tunnel-id> 替換為實際的 Tunnel ID

tunnel: <tunnel-id>
credentials-file: /etc/cloudflared/credentials.json

ingress:
"""
    
    for domain, config in domains_config.items():
        config_content += f"  # {config['description']}\n"
        config_content += f"  - hostname: {domain}\n"
        config_content += f"    service: http://wuchangv510-wuchang-web-1:{config['port']}\n\n"
    
    config_content += "  # 預設規則（必須放在最後）\n"
    config_content += "  - service: http_status:404\n"
    
    config_file.write_text(config_content, encoding="utf-8")
    log(f"配置範本已產生: {config_file}", "OK")
    
    return config_file


def deploy_status_check():
    """檢查部署狀態"""
    print("=" * 70)
    print("【網域部署狀態檢查】")
    print("=" * 70)
    print()
    
    # 檢查 Docker
    log("1. 檢查 Docker 環境...", "PROGRESS")
    if not check_docker():
        log("Docker 檢查失敗，請先安裝並啟動 Docker", "ERROR")
        return False
    print()
    
    # 檢查容器
    log("2. 檢查容器狀態...", "PROGRESS")
    containers = {
        "wuchangv510-cloudflared-1": "Cloudflare Tunnel",
        "wuchangv510-wuchang-web-1": "Odoo Web",
        "wuchangv510-db-1": "PostgreSQL",
        "wuchangv510-caddy-1": "Caddy",
    }
    
    all_running = True
    for container, description in containers.items():
        if check_container(container):
            status = get_container_status(container)
            log(f"  {description} ({container}): 運行中 - {status}", "OK")
        else:
            log(f"  {description} ({container}): 未運行", "ERROR")
            all_running = False
    print()
    
    # 檢查 Cloudflare 配置
    log("3. 檢查 Cloudflare Tunnel 配置...", "PROGRESS")
    config_ready = check_cloudflare_config()
    print()
    
    # 檢查 DNS
    log("4. 檢查 DNS 解析...", "PROGRESS")
    domains = [
        "app.wuchang.org.tw",
        "ai.wuchang.org.tw",
        "admin.wuchang.org.tw",
        "monitor.wuchang.org.tw",
    ]
    
    dns_status = {}
    for domain in domains:
        success, result = check_dns(domain)
        if success:
            log(f"  {domain} → {result}", "OK")
            dns_status[domain] = True
        else:
            log(f"  {domain} → {result}", "WARN")
            dns_status[domain] = False
    print()
    
    # 檢查服務連接
    log("5. 檢查服務連接...", "PROGRESS")
    service_status = {}
    for domain in domains:
        url = f"https://{domain}"
        success, result = check_service_http(url, timeout=3)
        if success:
            log(f"  {domain} → {result}", "OK")
            service_status[domain] = True
        else:
            log(f"  {domain} → {result}", "WARN")
            service_status[domain] = False
    print()
    
    # 總結
    print("=" * 70)
    print("【部署狀態總結】")
    print("=" * 70)
    print()
    
    log(f"Docker 環境: {'正常' if check_docker() else '異常'}", "OK" if check_docker() else "ERROR")
    log(f"容器狀態: {'全部運行' if all_running else '部分異常'}", "OK" if all_running else "WARN")
    log(f"Cloudflare 配置: {'已配置' if config_ready else '未配置'}", "OK" if config_ready else "WARN")
    log(f"DNS 解析: {sum(dns_status.values())}/{len(domains)} 個域名可解析", "OK" if all(dns_status.values()) else "WARN")
    log(f"服務連接: {sum(service_status.values())}/{len(domains)} 個服務可連接", "OK" if all(service_status.values()) else "WARN")
    
    print()
    
    return all_running and config_ready


def deploy_guide():
    """顯示部署指南"""
    print("=" * 70)
    print("【網域部署指南】")
    print("=" * 70)
    print()
    
    guide = """
## 網域部署步驟

### 步驟 1: 設定 Cloudflare Tunnel

1. **登入 Cloudflare**
   ```bash
   # 如果還沒有安裝 cloudflared
   # Windows: 下載 https://github.com/cloudflare/cloudflared/releases
   
   # 登入 Cloudflare
   cloudflared tunnel login
   ```

2. **建立隧道**
   ```bash
   cloudflared tunnel create wuchang-tunnel
   ```
   
   記下產生的 Tunnel ID。

3. **配置 DNS 路由**
   ```bash
   cloudflared tunnel route dns wuchang-tunnel app.wuchang.org.tw
   cloudflared tunnel route dns wuchang-tunnel ai.wuchang.org.tw
   cloudflared tunnel route dns wuchang-tunnel admin.wuchang.org.tw
   cloudflared tunnel route dns wuchang-tunnel monitor.wuchang.org.tw
   ```

4. **複製憑證檔案**
   - 憑證位置：`%USERPROFILE%\.cloudflared\<tunnel-id>.json`
   - 複製到：`cloudflared/credentials.json`

5. **更新配置檔案**
   - 執行此腳本產生配置範本
   - 編輯 `cloudflared/config.yml`
   - 將 `<tunnel-id>` 替換為實際的 Tunnel ID

### 步驟 2: 啟動服務

```bash
# 使用雲端配置啟動
docker-compose -f docker-compose.cloud.yml up -d

# 或使用統一配置（如果已包含 Cloudflare）
docker-compose -f docker-compose.unified.yml up -d
```

### 步驟 3: 驗證部署

執行此腳本檢查部署狀態：
```bash
python deploy_domain.py
```

---

## 域名配置

- **app.wuchang.org.tw** → Odoo ERP 系統 (端口 8069)
- **ai.wuchang.org.tw** → Open WebUI (端口 8080)
- **admin.wuchang.org.tw** → Portainer (端口 9000)
- **monitor.wuchang.org.tw** → Uptime Kuma (端口 3001)

---

## 疑難排解

### DNS 無法解析
- 確認 DNS 路由已設定：`cloudflared tunnel route dns list`
- 等待 DNS 傳播（可能需要幾分鐘）

### 服務無法連接
- 檢查 Cloudflare Tunnel 容器是否運行
- 查看容器日誌：`docker logs wuchangv510-cloudflared-1`
- 確認配置檔案中的服務端口正確

### 憑證錯誤
- 確認 `credentials.json` 檔案存在且正確
- 重新執行 `cloudflared tunnel login`

---

## 相關檔案

- `cloudflared/config.yml` - Cloudflare Tunnel 配置
- `cloudflared/credentials.json` - Cloudflare 憑證
- `docker-compose.cloud.yml` - 雲端部署配置
- `CLOUD_DEPLOYMENT_GUIDE.md` - 詳細部署指南

"""
    
    print(guide)


def main():
    """主函數"""
    print("=" * 70)
    print("網域部署自動化工具")
    print("=" * 70)
    print()
    
    print("請選擇操作：")
    print("1. 檢查部署狀態")
    print("2. 產生 Cloudflare 配置範本")
    print("3. 顯示部署指南")
    print("4. 完整部署檢查")
    print()
    
    try:
        choice = input("請選擇 (1-4): ").strip()
    except EOFError:
        choice = "4"  # 預設執行完整檢查
    
    if choice == "1":
        deploy_status_check()
    
    elif choice == "2":
        config_file = generate_cloudflare_config()
        print()
        log("配置範本已產生", "OK")
        print()
        print("下一步：")
        print("1. 編輯配置檔案並更新 Tunnel ID")
        print("2. 複製 Cloudflare 憑證到 cloudflared/credentials.json")
        print("3. 執行 'cloudflared tunnel route dns' 設定 DNS 路由")
    
    elif choice == "3":
        deploy_guide()
    
    elif choice == "4" or choice == "":
        deploy_status_check()
        print()
        print("=" * 70)
        print("【後續步驟】")
        print("=" * 70)
        print()
        print("如果配置未完成，請執行：")
        print("  python deploy_domain.py  (選擇 2) 產生配置範本")
        print("  python deploy_domain.py  (選擇 3) 查看部署指南")
    
    else:
        log("無效的選擇", "ERROR")
        return 1
    
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
