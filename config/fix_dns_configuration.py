#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_dns_configuration.py

DNS 配置修復腳本

自動化修復 DNS 和 Cloudflare Tunnel 配置問題
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Optional

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
CLOUDFLARED_DIR = BASE_DIR / "cloudflared"
CONFIG_FILE = CLOUDFLARED_DIR / "config.yml"
CREDENTIALS_FILE = CLOUDFLARED_DIR / "credentials.json"


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


def check_cloudflared_installed() -> bool:
    """檢查 cloudflared 是否安裝"""
    try:
        result = subprocess.run(
            ["cloudflared", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False
    except Exception:
        return False


def find_credentials_files() -> list:
    """查找可能的憑證檔案"""
    home = Path.home()
    possible_paths = [
        home / ".cloudflared",
        Path("C:/Users") / Path.home().name / ".cloudflared",
    ]
    
    credentials = []
    for base_path in possible_paths:
        if base_path.exists():
            for file in base_path.glob("*.json"):
                if "tunnel" in file.name.lower() or len(file.name) > 30:  # Tunnel ID 格式
                    credentials.append(file)
    
    return credentials


def update_config_file(tunnel_id: Optional[str] = None):
    """更新配置檔案"""
    log("更新 Cloudflare Tunnel 配置檔案...", "PROGRESS")
    
    # 確保目錄存在
    CLOUDFLARED_DIR.mkdir(parents=True, exist_ok=True)
    
    # 完整的配置內容
    config_content = """# Cloudflare Tunnel 配置
# 自動生成/更新時間: 2026-01-20

tunnel: {tunnel_id}
credentials-file: /etc/cloudflared/credentials.json

ingress:
  # Odoo ERP 系統
  - hostname: app.wuchang.org.tw
    service: http://wuchangv510-wuchang-web-1:8069
  
  # Open WebUI (AI 介面)
  - hostname: ai.wuchang.org.tw
    service: http://wuchangv510-open-webui-1:8080
  
  # Portainer (容器管理)
  - hostname: admin.wuchang.org.tw
    service: http://wuchangv510-portainer-1:9000
  
  # Uptime Kuma (監控)
  - hostname: monitor.wuchang.org.tw
    service: http://wuchangv510-uptime-kuma-1:3001
  
  # 預設規則（必須放在最後）
  - service: http_status:404
"""
    
    # 如果有提供 Tunnel ID，使用它；否則保持佔位符
    if tunnel_id:
        config_content = config_content.format(tunnel_id=tunnel_id)
    else:
        config_content = config_content.format(tunnel_id="<tunnel-id>")
    
    CONFIG_FILE.write_text(config_content, encoding="utf-8")
    log(f"配置檔案已更新: {CONFIG_FILE}", "OK")


def copy_credentials_file(source: Path) -> bool:
    """複製憑證檔案"""
    try:
        import shutil
        shutil.copy2(source, CREDENTIALS_FILE)
        log(f"憑證檔案已複製: {CREDENTIALS_FILE}", "OK")
        return True
    except Exception as e:
        log(f"複製憑證檔案失敗: {e}", "ERROR")
        return False


def list_available_tunnels() -> list:
    """列出可用的隧道"""
    try:
        result = subprocess.run(
            ["cloudflared", "tunnel", "list"],
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            tunnels = []
            for line in lines[2:]:  # 跳過標題行
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        tunnels.append({
                            "id": parts[0],
                            "name": parts[1] if len(parts) > 1 else ""
                        })
            return tunnels
        return []
    except Exception as e:
        log(f"列出隧道時發生錯誤: {e}", "WARN")
        return []


def check_docker_compose_service_names():
    """檢查 Docker Compose 中的服務名稱"""
    compose_file = BASE_DIR / "docker-compose.cloud.yml"
    if not compose_file.exists():
        compose_file = BASE_DIR / "docker-compose.unified.yml"
    
    if compose_file.exists():
        try:
            with open(compose_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 查找容器名稱
                import re
                container_names = re.findall(r'container_name:\s*([^\s]+)', content)
                return container_names
        except Exception:
            pass
    
    return []


def restart_cloudflared_container():
    """重啟 Cloudflare Tunnel 容器"""
    log("重啟 Cloudflare Tunnel 容器...", "PROGRESS")
    
    try:
        result = subprocess.run(
            ["docker", "restart", "wuchangv510-cloudflared-1"],
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            log("容器已重啟", "OK")
            return True
        else:
            log(f"重啟容器失敗: {result.stderr}", "ERROR")
            return False
    except Exception as e:
        log(f"重啟容器時發生錯誤: {e}", "ERROR")
        return False


def main():
    """主函數"""
    print("=" * 70)
    print("DNS 配置修復工具")
    print("=" * 70)
    print()
    
    # 1. 檢查 cloudflared 是否安裝
    log("檢查 cloudflared 是否安裝...", "PROGRESS")
    cloudflared_installed = check_cloudflared_installed()
    
    if cloudflared_installed:
        log("cloudflared 已安裝", "OK")
    else:
        log("cloudflared 未安裝", "WARN")
        log("請先安裝 cloudflared:", "INFO")
        log("  下載: https://github.com/cloudflare/cloudflared/releases", "INFO")
        log("  或使用 Docker: docker pull cloudflare/cloudflared:latest", "INFO")
        print()
    
    # 2. 查找憑證檔案
    log("查找 Cloudflare 憑證檔案...", "PROGRESS")
    credentials = find_credentials_files()
    
    if credentials:
        log(f"找到 {len(credentials)} 個可能的憑證檔案:", "OK")
        for cred in credentials:
            print(f"   - {cred}")
        
        if len(credentials) == 1:
            # 自動複製
            if copy_credentials_file(credentials[0]):
                log("憑證檔案已自動複製", "OK")
        else:
            log("發現多個憑證檔案，請手動選擇", "INFO")
    else:
        log("未找到憑證檔案", "WARN")
        log("需要執行: cloudflared tunnel login", "INFO")
    print()
    
    # 3. 列出可用隧道
    tunnel_id = None
    if cloudflared_installed:
        log("列出可用的隧道...", "PROGRESS")
        tunnels = list_available_tunnels()
        
        if tunnels:
            log(f"找到 {len(tunnels)} 個隧道:", "OK")
            for tunnel in tunnels:
                print(f"   - {tunnel['name']} ({tunnel['id']})")
            
            # 查找 wuchang-tunnel
            wuchang_tunnel = next((t for t in tunnels if 'wuchang' in t['name'].lower()), None)
            if wuchang_tunnel:
                tunnel_id = wuchang_tunnel['id']
                log(f"使用隧道: {wuchang_tunnel['name']} ({tunnel_id})", "OK")
            elif len(tunnels) == 1:
                tunnel_id = tunnels[0]['id']
                log(f"使用唯一隧道: {tunnels[0]['name']} ({tunnel_id})", "OK")
        else:
            log("未找到隧道", "WARN")
            log("需要執行: cloudflared tunnel create wuchang-tunnel", "INFO")
    print()
    
    # 4. 更新配置檔案
    update_config_file(tunnel_id)
    print()
    
    # 5. 檢查 Docker 服務名稱
    log("檢查 Docker 服務配置...", "PROGRESS")
    container_names = check_docker_compose_service_names()
    if container_names:
        log(f"找到 {len(container_names)} 個容器配置", "OK")
    print()
    
    # 6. 總結和後續步驟
    print("=" * 70)
    print("【修復總結】")
    print("=" * 70)
    print()
    
    if CREDENTIALS_FILE.exists():
        log("✅ 憑證檔案: 已就緒", "OK")
    else:
        log("❌ 憑證檔案: 需要手動設定", "ERROR")
        print("   執行: cloudflared tunnel login")
        print("   然後複製憑證到: cloudflared/credentials.json")
        print()
    
    if tunnel_id:
        log(f"✅ Tunnel ID: 已設定 ({tunnel_id})", "OK")
    else:
        log("⚠️ Tunnel ID: 需要手動設定", "WARN")
        print("   1. 執行: cloudflared tunnel create wuchang-tunnel")
        print("   2. 編輯 cloudflared/config.yml，將 <tunnel-id> 替換為實際 ID")
        print()
    
    log(f"✅ 配置檔案: 已更新 ({CONFIG_FILE})", "OK")
    print()
    
    # 7. 提供完整修復步驟
    print("=" * 70)
    print("【完整修復步驟】")
    print("=" * 70)
    print()
    
    steps = []
    
    if not cloudflared_installed:
        steps.append("1. 安裝 cloudflared（如果還沒有）")
    
    if not CREDENTIALS_FILE.exists():
        steps.append("2. 執行: cloudflared tunnel login")
        steps.append("3. 複製憑證: 將 %USERPROFILE%\\.cloudflared\\<tunnel-id>.json 複製到 cloudflared\\credentials.json")
    
    if not tunnel_id:
        steps.append("4. 執行: cloudflared tunnel create wuchang-tunnel")
        steps.append("5. 編輯 cloudflared/config.yml，將 <tunnel-id> 替換為實際 ID")
    
    steps.append("6. 配置 DNS 路由:")
    steps.append("   cloudflared tunnel route dns wuchang-tunnel app.wuchang.org.tw")
    steps.append("   cloudflared tunnel route dns wuchang-tunnel ai.wuchang.org.tw")
    steps.append("   cloudflared tunnel route dns wuchang-tunnel admin.wuchang.org.tw")
    steps.append("   cloudflared tunnel route dns wuchang-tunnel monitor.wuchang.org.tw")
    
    steps.append("7. 重啟容器: docker restart wuchangv510-cloudflared-1")
    steps.append("8. 驗證: python check_dns_status.py")
    
    for step in steps:
        print(f"   {step}")
    print()
    
    # 8. 詢問是否重啟容器
    if CREDENTIALS_FILE.exists() and (tunnel_id or CONFIG_FILE.exists()):
        print("=" * 70)
        print("【立即執行】")
        print("=" * 70)
        print()
        
        try:
            restart = input("是否現在重啟 Cloudflare Tunnel 容器？(y/n): ").strip().lower()
            if restart == 'y':
                if restart_cloudflared_container():
                    log("修復完成！", "OK")
                    log("請等待幾秒後執行: python check_dns_status.py 驗證", "INFO")
                else:
                    log("容器重啟失敗，請手動執行: docker restart wuchangv510-cloudflared-1", "WARN")
        except (EOFError, KeyboardInterrupt):
            log("跳過容器重啟", "INFO")
    
    print()
    log("修復腳本執行完成", "OK")
    
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
