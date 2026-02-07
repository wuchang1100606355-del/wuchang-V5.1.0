#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cloud_deployment.py

雲端部署自動化腳本

功能：
- 檢查部署環境
- 建立 Cloudflare Tunnel 配置
- 啟動容器服務
- 驗證部署狀態
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
CLOUDFLARED_DIR = BASE_DIR / "cloudflared"
GDRIVE_PATH = Path("J:/共用雲端硬碟/五常雲端空間")


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")


def check_docker():
    """檢查 Docker 是否安裝"""
    print("【檢查 Docker 環境】")
    print()
    
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            log(f"Docker 已安裝: {result.stdout.strip()}", "OK")
            return True
        else:
            log("Docker 未安裝或無法執行", "ERROR")
            return False
    except FileNotFoundError:
        log("Docker 未安裝，請先安裝 Docker Desktop", "ERROR")
        return False
    except Exception as e:
        log(f"檢查 Docker 時發生錯誤: {e}", "ERROR")
        return False


def check_docker_compose():
    """檢查 Docker Compose 是否可用"""
    try:
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            log(f"Docker Compose 可用: {result.stdout.strip()}", "OK")
            return True
        else:
            log("Docker Compose 不可用", "WARN")
            return False
    except Exception as e:
        log(f"檢查 Docker Compose 時發生錯誤: {e}", "WARN")
        return False


def check_gdrive_path():
    """檢查 Google Drive 路徑"""
    print("【檢查 Google Drive 路徑】")
    print()
    
    if GDRIVE_PATH.exists():
        log(f"Google Drive 路徑存在: {GDRIVE_PATH}", "OK")
        
        # 檢查必要的資料夾
        required_dirs = [
            "containers/data/odoo",
            "containers/uploads",
            "containers/logs",
            "containers/config",
            "backups/database",
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            full_path = GDRIVE_PATH / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            log(f"缺少資料夾: {', '.join(missing_dirs)}", "WARN")
            log("執行 python unified_storage_setup.py 建立資料夾結構", "INFO")
            return False
        else:
            log("所有必要的資料夾都存在", "OK")
            return True
    else:
        log(f"Google Drive 路徑不存在: {GDRIVE_PATH}", "ERROR")
        log("請確認 Google Drive 已安裝並同步", "INFO")
        return False


def setup_cloudflared_config():
    """建立 Cloudflare Tunnel 配置"""
    print("【建立 Cloudflare Tunnel 配置】")
    print()
    
    CLOUDFLARED_DIR.mkdir(exist_ok=True)
    
    # 檢查是否已有配置
    config_file = CLOUDFLARED_DIR / "config.yml"
    credentials_file = CLOUDFLARED_DIR / "credentials.json"
    
    if config_file.exists() and credentials_file.exists():
        log("Cloudflare Tunnel 配置已存在", "OK")
        return True
    
    # 建立範例配置
    example_config = """# Cloudflare Tunnel 配置範本
# 請先執行以下步驟：
# 1. 登入 Cloudflare: cloudflared tunnel login
# 2. 建立隧道: cloudflared tunnel create wuchang-tunnel
# 3. 配置 DNS: cloudflared tunnel route dns wuchang-tunnel app.wuchang.org.tw
# 4. 複製 credentials.json 到此目錄

tunnel: <tunnel-id>
credentials-file: /etc/cloudflared/credentials.json

ingress:
  # Odoo ERP 系統
  - hostname: app.wuchang.org.tw
    service: http://wuchang-web:8069
  
  # 預設規則（必須放在最後）
  - service: http_status:404
"""
    
    config_file.write_text(example_config, encoding="utf-8")
    log(f"已建立範例配置: {config_file}", "OK")
    
    # 建立說明檔案
    readme = CLOUDFLARED_DIR / "README.md"
    readme_content = """# Cloudflare Tunnel 設定說明

## 步驟 1：安裝 cloudflared

### Windows
下載並安裝：https://github.com/cloudflare/cloudflared/releases

### 或使用 Docker
```bash
docker pull cloudflare/cloudflared:latest
```

## 步驟 2：登入 Cloudflare

```bash
cloudflared tunnel login
```

這會開啟瀏覽器，讓您登入 Cloudflare 並授權。

## 步驟 3：建立隧道

```bash
cloudflared tunnel create wuchang-tunnel
```

## 步驟 4：配置 DNS

```bash
cloudflared tunnel route dns wuchang-tunnel app.wuchang.org.tw
```

## 步驟 5：複製憑證

憑證檔案位置：
- Windows: `%USERPROFILE%\\.cloudflared\\<tunnel-id>.json`
- Linux/Mac: `~/.cloudflared/<tunnel-id>.json`

複製到：`cloudflared/credentials.json`

## 步驟 6：更新配置

編輯 `config.yml`，將 `<tunnel-id>` 替換為實際的隧道 ID。

## 步驟 7：啟動服務

```bash
docker-compose -f docker-compose.cloud.yml up -d
```
"""
    
    readme.write_text(readme_content, encoding="utf-8")
    log(f"已建立說明檔案: {readme}", "OK")
    
    log("請按照 README.md 的說明完成 Cloudflare Tunnel 設定", "WARN")
    return False


def check_containers():
    """檢查容器狀態"""
    print("【檢查容器狀態】")
    print()
    
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        container = json.loads(line)
                        containers.append(container)
                    except:
                        pass
            
            wuchang_containers = [
                c for c in containers
                if 'wuchang' in c.get('Names', '').lower()
            ]
            
            if wuchang_containers:
                log(f"找到 {len(wuchang_containers)} 個五常容器", "OK")
                for container in wuchang_containers:
                    status = container.get('Status', '')
                    name = container.get('Names', '')
                    log(f"  - {name}: {status}", "INFO")
            else:
                log("沒有找到五常容器", "INFO")
            
            return True
        else:
            log("無法檢查容器狀態", "WARN")
            return False
    except Exception as e:
        log(f"檢查容器時發生錯誤: {e}", "WARN")
        return False


def deploy_containers():
    """部署容器"""
    print("【部署容器】")
    print()
    
    compose_file = BASE_DIR / "docker-compose.cloud.yml"
    
    if not compose_file.exists():
        log(f"Docker Compose 檔案不存在: {compose_file}", "ERROR")
        return False
    
    try:
        log("正在啟動容器...", "INFO")
        result = subprocess.run(
            ["docker", "compose", "-f", str(compose_file), "up", "-d"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            log("容器啟動成功", "OK")
            print(result.stdout)
            return True
        else:
            log("容器啟動失敗", "ERROR")
            print(result.stderr)
            return False
    except Exception as e:
        log(f"部署容器時發生錯誤: {e}", "ERROR")
        return False


def verify_deployment():
    """驗證部署狀態"""
    print("【驗證部署狀態】")
    print()
    
    services = {
        "wuchang-web": 8069,
        "wuchang-db": 5432,
        "wuchang-cloudflared": None,
    }
    
    all_ok = True
    for service, port in services.items():
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={service}", "--format", "{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                status = result.stdout.strip()
                if "Up" in status:
                    log(f"{service}: 運行中 ({status})", "OK")
                else:
                    log(f"{service}: {status}", "WARN")
                    all_ok = False
            else:
                log(f"{service}: 未運行", "WARN")
                all_ok = False
        except Exception as e:
            log(f"檢查 {service} 時發生錯誤: {e}", "WARN")
            all_ok = False
    
    return all_ok


def main():
    """主函數"""
    print("=" * 70)
    print("雲端部署自動化")
    print("=" * 70)
    print()
    
    # 檢查環境
    if not check_docker():
        return 1
    
    if not check_docker_compose():
        log("將嘗試使用 docker-compose 命令", "INFO")
    
    if not check_gdrive_path():
        log("請先執行 python unified_storage_setup.py", "WARN")
        return 1
    
    # 檢查 Cloudflare Tunnel 配置
    cloudflared_ready = setup_cloudflared_config()
    
    # 檢查現有容器
    check_containers()
    
    print()
    print("=" * 70)
    print("【部署選項】")
    print("=" * 70)
    print()
    
    if cloudflared_ready:
        print("1. 完整部署（包含 Cloudflare Tunnel）")
        print("   docker-compose -f docker-compose.cloud.yml up -d")
        print()
        print("2. 本地部署（不含 Cloudflare Tunnel）")
        print("   docker-compose -f docker-compose.unified.yml up -d")
    else:
        print("1. 本地部署（不含 Cloudflare Tunnel）")
        print("   docker-compose -f docker-compose.unified.yml up -d")
        print()
        print("2. 完成 Cloudflare Tunnel 設定後，使用完整部署")
        print("   docker-compose -f docker-compose.cloud.yml up -d")
    
    print()
    
    # 詢問是否立即部署
    try:
        response = input("是否立即部署本地服務？(y/n): ").strip().lower()
        if response == 'y':
            if deploy_containers():
                verify_deployment()
                print()
                log("部署完成！", "OK")
                print()
                print("【訪問服務】")
                print("  本地: http://localhost:8069")
                if cloudflared_ready:
                    print("  外網: https://app.wuchang.org.tw")
            else:
                log("部署失敗，請檢查錯誤訊息", "ERROR")
    except KeyboardInterrupt:
        print()
        log("已取消", "INFO")
    except:
        pass
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
