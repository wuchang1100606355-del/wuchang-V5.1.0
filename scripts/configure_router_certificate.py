#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置 ASUS 路由器伺服器憑證
從路由器管理界面獲取證書並配置到系統
"""

import sys
import os
import requests
import json
from datetime import datetime
from pathlib import Path

ROUTER_IP = "192.168.50.1"
ROUTER_ADMIN_URL = f"http://{ROUTER_IP}"
CERT_ENDPOINT = "http://www.asusrouter.com/cert_key.tar"

def check_router_access():
    """檢查路由器訪問"""
    try:
        response = requests.get(ROUTER_ADMIN_URL, timeout=5)
        return {
            'accessible': response.status_code in [200, 401, 302],
            'status_code': response.status_code,
            'requires_auth': response.status_code == 401
        }
    except Exception as e:
        return {
            'accessible': False,
            'error': str(e)
        }

def download_cert_from_router():
    """從路由器下載證書（需要認證）"""
    print("=" * 80)
    print("  ASUS 路由器伺服器憑證配置")
    print("=" * 80)
    print()
    print(f"路由器 IP: {ROUTER_IP}")
    print(f"管理界面: {ROUTER_ADMIN_URL}")
    print()
    
    # 檢查路由器訪問
    print("[1/4] 檢查路由器訪問...")
    access = check_router_access()
    if access.get('accessible'):
        print(f"  ✓ 路由器可訪問 (狀態碼: {access.get('status_code')})")
        if access.get('requires_auth'):
            print(f"  ⚠ 需要認證才能訪問")
    else:
        print(f"  ✗ 路由器無法訪問: {access.get('error', 'Unknown')}")
        return 1
    print()
    
    # 說明證書獲取方式
    print("[2/4] 證書獲取方式說明...")
    print("  方式 1: 通過路由器管理界面下載")
    print(f"    1. 訪問: {ROUTER_ADMIN_URL}")
    print("    2. 登入路由器管理界面")
    print("    3. 進入: 系統管理 → 系統設定 → 憑證設定")
    print("    4. 下載伺服器憑證 (cert_key.tar)")
    print()
    print("  方式 2: 使用 API (需要認證)")
    print(f"    URL: {CERT_ENDPOINT}")
    print("    注意: 可能需要從路由器內部網絡訪問")
    print()
    
    # 檢查證書文件
    print("[3/4] 檢查現有證書文件...")
    cert_dir = Path("router_certificates")
    cert_dir.mkdir(exist_ok=True)
    
    cert_files = list(cert_dir.glob("*.crt")) + list(cert_dir.glob("*.key")) + list(cert_dir.glob("*.pem"))
    if cert_files:
        print(f"  找到 {len(cert_files)} 個證書文件:")
        for cert_file in cert_files:
            size = cert_file.stat().st_size
            print(f"    • {cert_file.name} ({size} bytes)")
    else:
        print("  ⚠ 未找到證書文件")
    print()
    
    # 生成配置建議
    print("[4/4] 生成配置建議...")
    
    config = {
        'router_info': {
            'ip': ROUTER_IP,
            'admin_url': ROUTER_ADMIN_URL,
            'cert_endpoint': CERT_ENDPOINT
        },
        'certificate_paths': {
            'cert_dir': str(cert_dir.absolute()),
            'suggested_cert_path': str(cert_dir / 'server.crt'),
            'suggested_key_path': str(cert_dir / 'server.key')
        },
        'caddy_config': {
            'method': 'auto_https',
            'comment': 'Caddy 已配置自動 HTTPS，無需手動配置路由器證書',
            'alternative': '如果需要在 Caddy 中使用路由器證書，可以配置 tls 指令'
        },
        'router_config': {
            'enable_https': True,
            'upload_certificate': '通過管理界面上傳證書',
            'certificate_location': '系統管理 → 系統設定 → 憑證設定'
        }
    }
    
    # 保存配置
    config_file = cert_dir / "router_cert_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ 配置已保存: {config_file}")
    print()
    
    print("=" * 80)
    print("  配置建議")
    print("=" * 80)
    print()
    print("推薦方案: 使用 Caddy 自動 HTTPS")
    print("  • Caddy 已配置自動 SSL/TLS 證書")
    print("  • 通過 Cloudflare 隧道提供外網訪問")
    print("  • 無需手動配置路由器證書")
    print()
    print("如果需要路由器本地 HTTPS:")
    print("  1. 從路由器管理界面下載證書")
    print("  2. 解壓證書文件到 router_certificates/ 目錄")
    print("  3. 在路由器管理界面上傳並啟用證書")
    print()
    print(f"證書目錄: {cert_dir.absolute()}")
    
    return 0

def main():
    return download_cert_from_router()

if __name__ == '__main__':
    sys.exit(main())
