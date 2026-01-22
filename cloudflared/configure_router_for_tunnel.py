#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置路由器以支援 Cloudflare Tunnel
確保伺服器在路由器內部網路可被 Cloudflare Tunnel 訪問
"""

import sys
import json
from pathlib import Path

# 設定 UTF-8 編碼
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    from router_full_control import RouterFullControl
    ROUTER_AVAILABLE = True
except ImportError:
    ROUTER_AVAILABLE = False
    print("⚠️  router_full_control 模組未找到，將跳過路由器配置")

BASE_DIR = Path(__file__).resolve().parent.parent

# Cloudflare Tunnel 服務配置
TUNNEL_SERVICES = [
    {
        "name": "Caddy (首頁)",
        "internal_port": 80,
        "external_port": 8080,  # 可選，如果使用端口轉發
        "protocol": "TCP",
        "description": "Cloudflare Tunnel - Caddy Web Server"
    },
    {
        "name": "Odoo ERP",
        "internal_port": 8069,
        "external_port": 8069,
        "protocol": "TCP",
        "description": "Cloudflare Tunnel - Odoo ERP System"
    },
    {
        "name": "Open WebUI",
        "internal_port": 8080,
        "external_port": 8081,
        "protocol": "TCP",
        "description": "Cloudflare Tunnel - Open WebUI"
    },
    {
        "name": "Portainer",
        "internal_port": 9000,
        "external_port": 9000,
        "protocol": "TCP",
        "description": "Cloudflare Tunnel - Portainer"
    },
    {
        "name": "Uptime Kuma",
        "internal_port": 3001,
        "external_port": 3001,
        "protocol": "TCP",
        "description": "Cloudflare Tunnel - Uptime Kuma"
    }
]


def get_server_internal_ip() -> str:
    """取得伺服器內部 IP（需要手動輸入或自動偵測）"""
    # TODO: 自動偵測伺服器內部 IP
    # 目前需要手動輸入
    return input("請輸入伺服器內部 IP (例如: 192.168.50.100): ").strip()


def configure_router_port_forwarding(router: RouterFullControl, server_ip: str):
    """配置路由器端口轉發"""
    print("\n" + "=" * 60)
    print("配置路由器端口轉發")
    print("=" * 60)
    
    if not router.logged_in:
        print("❌ 路由器未登入，無法配置")
        return False
    
    success_count = 0
    for service in TUNNEL_SERVICES:
        print(f"\n配置 {service['name']}...")
        try:
            result = router.add_port_forwarding_rule(
                external_port=service['external_port'],
                internal_ip=server_ip,
                internal_port=service['internal_port'],
                protocol=service['protocol'],
                description=service['description']
            )
            if result:
                print(f"  ✅ 端口轉發配置成功: {service['external_port']} -> {server_ip}:{service['internal_port']}")
                success_count += 1
            else:
                print(f"  ❌ 端口轉發配置失敗: {service['name']}")
        except Exception as e:
            print(f"  ❌ 配置錯誤: {e}")
    
    print(f"\n配置完成: {success_count}/{len(TUNNEL_SERVICES)} 個服務")
    return success_count > 0


def check_ddns_status(router: RouterFullControl):
    """檢查 DDNS 狀態"""
    print("\n" + "=" * 60)
    print("檢查 DDNS 狀態")
    print("=" * 60)
    
    if not router.logged_in:
        print("❌ 路由器未登入，無法檢查")
        return
    
    try:
        ddns_status = router.get_ddns_status()
        print(f"DDNS 狀態: {json.dumps(ddns_status, ensure_ascii=False, indent=2)}")
        
        if ddns_status.get('enabled'):
            print("✅ DDNS 已啟用")
        else:
            print("⚠️  DDNS 未啟用，建議啟用以確保外部訪問")
    except Exception as e:
        print(f"❌ 檢查 DDNS 狀態時發生錯誤: {e}")


def update_config_for_router(config_path: Path, server_ip: str, use_port_forwarding: bool = False):
    """更新 config.yml 以適應路由器內部網路"""
    print("\n" + "=" * 60)
    print("更新 config.yml")
    print("=" * 60)
    
    if not config_path.exists():
        print(f"❌ 配置檔案不存在: {config_path}")
        return False
    
    # 讀取現有配置
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 根據是否使用端口轉發來更新服務地址
    if use_port_forwarding:
        # 使用路由器 IP + 外部端口
        replacements = {
            'http://wuchangv510-caddy-1:80': f'http://{server_ip}:8080',
            'http://wuchangv510-wuchang-web-1:8069': f'http://{server_ip}:8069',
            'http://wuchangv510-open-webui-1:8080': f'http://{server_ip}:8081',
            'http://wuchangv510-portainer-1:9000': f'http://{server_ip}:9000',
            'http://wuchangv510-uptime-kuma-1:3001': f'http://{server_ip}:3001',
        }
    else:
        # 使用伺服器內部 IP + 內部端口（直接訪問）
        replacements = {
            'http://wuchangv510-caddy-1:80': f'http://{server_ip}:80',
            'http://wuchangv510-wuchang-web-1:8069': f'http://{server_ip}:8069',
            'http://wuchangv510-open-webui-1:8080': f'http://{server_ip}:8080',
            'http://wuchangv510-portainer-1:9000': f'http://{server_ip}:9000',
            'http://wuchangv510-uptime-kuma-1:3001': f'http://{server_ip}:3001',
        }
    
    # 執行替換
    updated = False
    for old, new in replacements.items():
        if old in content:
            content = content.replace(old, new)
            print(f"  ✅ 更新: {old} -> {new}")
            updated = True
    
    if updated:
        # 備份原檔案
        backup_path = config_path.with_suffix('.yml.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(open(config_path, 'r', encoding='utf-8').read())
        print(f"  📄 原檔案已備份到: {backup_path}")
        
        # 寫入新配置
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ 配置檔案已更新: {config_path}")
        return True
    else:
        print("  ℹ️  配置檔案無需更新")
        return False


def main():
    """主函數"""
    print("=" * 60)
    print("Cloudflare Tunnel 路由器接替配置")
    print("=" * 60)
    
    # 1. 取得伺服器內部 IP
    print("\n[1] 取得伺服器內部 IP")
    server_ip = get_server_internal_ip()
    if not server_ip:
        print("❌ 未提供伺服器內部 IP，退出")
        return
    
    print(f"✅ 伺服器內部 IP: {server_ip}")
    
    # 2. 配置路由器（如果可用）
    router = None
    if ROUTER_AVAILABLE:
        print("\n[2] 連接路由器")
        router = RouterFullControl()
        if router.login():
            print("✅ 路由器登入成功")
            
            # 檢查 DDNS 狀態
            check_ddns_status(router)
            
            # 詢問是否配置端口轉發
            use_port_forwarding = input("\n是否配置路由器端口轉發？(y/n): ").strip().lower() == 'y'
            
            if use_port_forwarding:
                configure_router_port_forwarding(router, server_ip)
        else:
            print("⚠️  路由器登入失敗，將跳過路由器配置")
            use_port_forwarding = False
    else:
        print("\n[2] 跳過路由器配置（模組未找到）")
        use_port_forwarding = False
    
    # 3. 更新 config.yml
    print("\n[3] 更新 config.yml")
    config_path = BASE_DIR / "cloudflared" / "config.yml"
    update_config_for_router(config_path, server_ip, use_port_forwarding)
    
    # 4. 總結
    print("\n" + "=" * 60)
    print("配置完成")
    print("=" * 60)
    print(f"\n伺服器內部 IP: {server_ip}")
    print(f"使用端口轉發: {'是' if use_port_forwarding else '否'}")
    print(f"\n下一步:")
    print("  1. 檢查 config.yml 是否正確")
    print("  2. 在伺服器上部署 Cloudflare Tunnel")
    print("  3. 驗證 HTTPS 訪問")


if __name__ == "__main__":
    main()
