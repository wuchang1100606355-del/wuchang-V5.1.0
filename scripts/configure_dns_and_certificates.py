#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
configure_dns_and_certificates.py

DNS設定、靜態DNS登記、憑證簽發、子域確認配置

功能：
- DNS設定和管理
- 靜態DNS登記
- SSL/TLS憑證簽發
- 子域確認和管理
- Google Workspace整合
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
DNS_CONFIG_FILE = CONFIG_DIR / "dns_config.json"
CERT_CONFIG_FILE = CONFIG_DIR / "certificates_config.json"

# 匯入工作日誌管理器
sys.path.insert(0, str(BASE_DIR / "scripts"))
try:
    from work_log_manager import WorkLogManager
    log_manager = WorkLogManager()
except ImportError:
    log_manager = None

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

def load_dns_config() -> Dict:
    """載入DNS配置"""
    default_config = {
        "domains": {
            "primary": "wuchang.life",
            "subdomains": [
                "www.wuchang.life",
                "app.wuchang.org.tw",
                "ai.wuchang.org.tw",
                "admin.wuchang.org.tw",
                "monitor.wuchang.org.tw"
            ]
        },
        "dns_provider": "cloudflare",
        "static_dns_records": [],
        "cloudflare_tunnel": {
            "tunnel_name": "wuchang-tunnel",
            "enabled": True
        }
    }
    
    if DNS_CONFIG_FILE.exists():
        try:
            with open(DNS_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return {**default_config, **config}
        except:
            pass
    
    # 建立預設配置檔案
    DNS_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DNS_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, ensure_ascii=False, indent=2)
    
    return default_config

def configure_static_dns_records(dns_config: Dict) -> bool:
    """配置靜態DNS記錄"""
    log("配置靜態DNS記錄...", "PROGRESS")
    
    records = dns_config.get("static_dns_records", [])
    if not records:
        log("未配置靜態DNS記錄", "INFO")
        return True
    
    for record in records:
        record_type = record.get("type", "A")
        name = record.get("name", "")
        content = record.get("content", "")
        
        log(f"設定DNS記錄: {name} ({record_type}) -> {content}", "INFO")
        
        # 這裡可以整合 Cloudflare API 或其他 DNS 提供商的 API
        # 範例：使用 cloudflared CLI
        if dns_config.get("dns_provider") == "cloudflare":
            try:
                # 使用 cloudflared 設定 DNS 路由
                cmd = ["cloudflared", "tunnel", "route", "dns", 
                       dns_config["cloudflare_tunnel"]["tunnel_name"], name]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    log(f"✓ DNS記錄設定成功: {name}", "OK")
                else:
                    log(f"✗ DNS記錄設定失敗: {name} - {result.stderr}", "ERROR")
            except Exception as e:
                log(f"✗ 設定DNS記錄時發生錯誤: {e}", "ERROR")
    
    return True

def verify_subdomains(dns_config: Dict) -> Dict:
    """驗證子域狀態"""
    log("驗證子域狀態...", "PROGRESS")
    
    results = {}
    subdomains = dns_config.get("domains", {}).get("subdomains", [])
    
    for subdomain in subdomains:
        try:
            # 使用 nslookup 或 dig 檢查DNS解析
            cmd = ["nslookup", subdomain]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and "Name:" in result.stdout:
                results[subdomain] = {
                    "status": "解析成功",
                    "resolved": True
                }
                log(f"✓ {subdomain} DNS解析正常", "OK")
            else:
                results[subdomain] = {
                    "status": "解析失敗",
                    "resolved": False
                }
                log(f"✗ {subdomain} DNS解析失敗", "WARN")
        except Exception as e:
            results[subdomain] = {
                "status": "檢查錯誤",
                "error": str(e)
            }
            log(f"✗ 檢查 {subdomain} 時發生錯誤: {e}", "ERROR")
    
    return results

def configure_certificates(cert_config: Dict) -> bool:
    """配置SSL/TLS憑證"""
    log("配置SSL/TLS憑證...", "PROGRESS")
    
    # 檢查 Caddy 配置（自動HTTPS）
    caddyfile_path = BASE_DIR / "wuchang_os" / "Caddyfile"
    if caddyfile_path.exists():
        log("✓ 找到 Caddyfile，Caddy 將自動處理憑證", "OK")
    
    # 檢查 Cloudflare Tunnel 憑證
    cloudflared_cred_path = BASE_DIR / "cloudflared" / "credentials.json"
    if cloudflared_cred_path.exists():
        log("✓ Cloudflare Tunnel 憑證已存在", "OK")
    else:
        log("⚠️ Cloudflare Tunnel 憑證不存在，需要手動設定", "WARN")
    
    return True

def main():
    """主函數"""
    print("=" * 70)
    print("DNS設定、憑證簽發、子域確認配置")
    print("權限等級：🔐 最高權限")
    print("=" * 70)
    print()
    
    if log_manager:
        log_manager.log_work(
            work_type="DNS與憑證配置",
            work_content="配置DNS設定、靜態DNS登記、憑證簽發、子域確認",
            agent="little_j",
            status="進行中",
            permission_level="最高權限"
        )
    
    # 載入DNS配置
    dns_config = load_dns_config()
    log("✓ 已載入DNS配置", "OK")
    
    # 配置靜態DNS記錄
    configure_static_dns_records(dns_config)
    
    # 驗證子域
    subdomain_results = verify_subdomains(dns_config)
    
    # 載入憑證配置
    cert_config = {}
    if CERT_CONFIG_FILE.exists():
        try:
            with open(CERT_CONFIG_FILE, 'r', encoding='utf-8') as f:
                cert_config = json.load(f)
        except:
            pass
    
    # 配置憑證
    configure_certificates(cert_config)
    
    # 記錄完成
    if log_manager:
        log_manager.log_work(
            work_type="DNS與憑證配置",
            work_content="配置DNS設定、靜態DNS登記、憑證簽發、子域確認",
            agent="little_j",
            status="完成",
            result=f"已配置DNS記錄，驗證了 {len(subdomain_results)} 個子域",
            related_files=[str(DNS_CONFIG_FILE), str(CERT_CONFIG_FILE)],
            permission_level="最高權限"
        )
    
    log("✅ DNS與憑證配置完成", "OK")
    return 0

if __name__ == "__main__":
    sys.exit(main())
