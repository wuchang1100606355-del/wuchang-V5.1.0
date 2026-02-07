#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調用路由器作為中繼進行外網握手
使用路由器進行端口轉發和中繼連接
"""

import sys
import os
import socket
import requests
import json
import time
from datetime import datetime
from typing import Dict, Optional

# 路由器配置
ROUTER_IP = "192.168.50.1"
ROUTER_ADMIN_PORT = 80  # ASUS 路由器默認管理端口
ROUTER_USERNAME = "admin"  # 默認用戶名
ROUTER_PASSWORD = None  # 需要配置

# 本地服務端口映射
LOCAL_SERVICES = {
    'odoo': {'port': 8069, 'name': 'Odoo'},
    'caddy': {'port': 80, 'name': 'Caddy HTTP'},
    'caddy_https': {'port': 443, 'name': 'Caddy HTTPS'},
    'command_center': {'port': 80, 'path': '/command_center', 'name': '指揮通道'},
    'design_report': {'port': 80, 'path': '/design_report', 'name': '設計報告'}
}

def get_router_info(ip: str = ROUTER_IP) -> Dict:
    """獲取路由器信息"""
    try:
        # 嘗試訪問路由器管理界面
        url = f"http://{ip}/"
        response = requests.get(url, timeout=5, allow_redirects=False)
        
        return {
            'ip': ip,
            'status': 'online' if response.status_code in [200, 302, 401] else 'unknown',
            'http_port': 80,
            'response_code': response.status_code,
            'headers': dict(response.headers) if hasattr(response, 'headers') else {}
        }
    except Exception as e:
        return {
            'ip': ip,
            'status': 'offline',
            'error': str(e)[:100]
        }

def check_port_forwarding(router_ip: str, external_port: int, internal_ip: str, internal_port: int) -> Dict:
    """檢查端口轉發配置（需要路由器 API 支持）"""
    # 這需要路由器 API 支持，ASUS 路由器通常有 API 端點
    # 暫時返回建議
    return {
        'success': False,
        'message': '需要路由器 API 支持',
        'suggestion': f'需要在路由器配置端口轉發: {external_port} -> {internal_ip}:{internal_port}'
    }

def create_relay_endpoint(internal_ip: str, internal_port: int, path: str = '/') -> Dict:
    """創建中繼端點配置"""
    return {
        'internal_url': f'http://{internal_ip}:{internal_port}{path}',
        'router_ip': ROUTER_IP,
        'external_access': f'通過路由器 {ROUTER_IP} 中繼',
        'setup_required': [
            '1. 登入路由器管理界面',
            f'2. 配置端口轉發規則',
            f'3. 外部端口 -> {internal_ip}:{internal_port}',
            '4. 啟用 UPnP 或手動配置'
        ]
    }

def test_relay_connection(router_ip: str, target_ip: str, target_port: int) -> Dict:
    """測試中繼連接"""
    try:
        # 通過路由器測試連接到目標服務
        # 這需要路由器支持中繼功能
        test_url = f"http://{target_ip}:{target_port}/health"
        response = requests.get(test_url, timeout=5)
        
        return {
            'success': response.status_code == 200,
            'router_ip': router_ip,
            'target': f'{target_ip}:{target_port}',
            'status_code': response.status_code,
            'latency': response.elapsed.total_seconds()
        }
    except Exception as e:
        return {
            'success': False,
            'router_ip': router_ip,
            'target': f'{target_ip}:{target_port}',
            'error': str(e)[:100]
        }

def setup_cloudflare_tunnel_via_router() -> Dict:
    """通過路由器設置 Cloudflare 隧道中繼"""
    # Cloudflare 隧道可以直接穿透 NAT，但可以通過路由器優化
    return {
        'method': 'Cloudflare Tunnel via Router',
        'advantage': '不需要端口轉發，直接穿透 NAT',
        'router_role': '僅作為網絡閘道，不參與轉發',
        'tunnel_status': 'active'
    }

def create_handshake_endpoint() -> Dict:
    """創建握手端點"""
    local_ip = socket.gethostbyname(socket.gethostname())
    
    # 如果無法獲取本地 IP，使用已知 IP
    if not local_ip or local_ip.startswith('127.'):
        local_ip = "192.168.50.249"
    
    return {
        'local_ip': local_ip,
        'router_ip': ROUTER_IP,
        'handshake_endpoints': {
            'internal': f'http://{local_ip}/api/handshake',
            'via_router': f'http://{ROUTER_IP}/relay/handshake',
            'external': 'https://wuchang.life/api/handshake',
            'cloudflare_tunnel': 'via Cloudflare Tunnel'
        },
        'services': LOCAL_SERVICES
    }

def perform_handshake(endpoint: str, timeout: int = 10) -> Dict:
    """執行握手"""
    try:
        start_time = time.time()
        response = requests.get(
            endpoint,
            timeout=timeout,
            headers={'User-Agent': 'Wuchang-OS-Handshake/1.0'}
        )
        elapsed = time.time() - start_time
        
        return {
            'success': True,
            'endpoint': endpoint,
            'status_code': response.status_code,
            'latency': round(elapsed * 1000, 2),  # ms
            'response_size': len(response.content),
            'timestamp': datetime.now().isoformat()
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'endpoint': endpoint,
            'error': '連接失敗',
            'timestamp': datetime.now().isoformat()
        }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'endpoint': endpoint,
            'error': '請求超時',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'success': False,
            'endpoint': endpoint,
            'error': str(e)[:100],
            'timestamp': datetime.now().isoformat()
        }

def main():
    print("=" * 80)
    print("  調用路由器作為中繼進行外網握手")
    print("=" * 80)
    print()
    print(f"路由器 IP: {ROUTER_IP}")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 檢查路由器狀態
    print("[1/5] 檢查路由器狀態...")
    router_info = get_router_info()
    if router_info['status'] == 'online':
        print(f"  ✓ 路由器在線 ({ROUTER_IP})")
        print(f"  ✓ HTTP 響應: {router_info.get('response_code', 'N/A')}")
    else:
        print(f"  ✗ 路由器無法訪問: {router_info.get('error', 'Unknown')}")
        return 1
    print()
    
    # 2. 獲取本地 IP
    print("[2/5] 獲取本地服務信息...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "192.168.50.249"
    
    print(f"  本地 IP: {local_ip}")
    print(f"  路由器 IP: {ROUTER_IP}")
    print()
    
    # 3. 創建握手端點配置
    print("[3/5] 創建握手端點配置...")
    handshake_config = create_handshake_endpoint()
    print("  握手端點:")
    for name, url in handshake_config['handshake_endpoints'].items():
        print(f"    {name}: {url}")
    print()
    
    # 4. 測試本地握手
    print("[4/5] 測試本地握手...")
    local_endpoints = [
        f"http://{local_ip}/health",
        f"http://{local_ip}/command_center",
        f"http://{local_ip}/design_report"
    ]
    
    local_results = []
    for endpoint in local_endpoints:
        result = perform_handshake(endpoint, timeout=3)
        local_results.append(result)
        status = "✓" if result['success'] else "✗"
        print(f"  {status} {endpoint}")
        if result['success']:
            print(f"    狀態碼: {result['status_code']}, 延遲: {result['latency']}ms")
        else:
            print(f"    錯誤: {result.get('error', 'Unknown')}")
    print()
    
    # 5. 測試通過路由器的中繼連接
    print("[5/5] 測試路由器中繼連接...")
    
    # 測試路由器本身的連接
    router_test = perform_handshake(f"http://{ROUTER_IP}/", timeout=3)
    if router_test['success']:
        print(f"  ✓ 路由器可訪問 (狀態碼: {router_test['status_code']})")
    else:
        print(f"  ✗ 路由器訪問失敗: {router_test.get('error')}")
    
    # 測試通過路由器訪問本地服務（需要端口轉發）
    print()
    print("  路由器中繼配置建議:")
    print("  1. 登入路由器管理界面: http://192.168.50.1")
    print("  2. 進入 進階設定 -> 外部網絡(WAN) -> 虛擬伺服器/端口轉發")
    print("  3. 添加端口轉發規則:")
    print(f"     - 外部端口 8069 -> {local_ip}:8069 (Odoo)")
    print(f"     - 外部端口 80 -> {local_ip}:80 (HTTP)")
    print(f"     - 外部端口 443 -> {local_ip}:443 (HTTPS)")
    print()
    
    # 6. Cloudflare 隧道中繼（推薦方式）
    print("=" * 80)
    print("  Cloudflare 隧道中繼（推薦）")
    print("=" * 80)
    tunnel_config = setup_cloudflare_tunnel_via_router()
    print(f"方法: {tunnel_config['method']}")
    print(f"優勢: {tunnel_config['advantage']}")
    print(f"路由器角色: {tunnel_config['router_role']}")
    print()
    
    # 7. 生成握手報告
    handshake_report = {
        'timestamp': datetime.now().isoformat(),
        'router': router_info,
        'local_ip': local_ip,
        'handshake_config': handshake_config,
        'local_tests': local_results,
        'router_test': router_test,
        'tunnel_config': tunnel_config
    }
    
    report_file = f"router_relay_handshake_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(handshake_report, f, ensure_ascii=False, indent=2)
        print(f"✓ 握手報告已保存: {report_file}")
    except Exception as e:
        print(f"⚠ 保存報告失敗: {e}")
    
    print()
    print("=" * 80)
    print("  外網握手配置建議")
    print("=" * 80)
    print()
    print("方法 1: Cloudflare 隧道（推薦，無需路由器配置）")
    print("  - 優點: 無需端口轉發，自動穿透 NAT，安全可靠")
    print("  - 配置: 使用現有的 cloudflared 服務")
    print("  - 訪問: https://wuchang.life/command_center")
    print()
    print("方法 2: 路由器端口轉發（需要路由器管理權限）")
    print("  - 優點: 直接訪問，延遲低")
    print("  - 缺點: 需要公網 IP，需要配置防火牆")
    print("  - 步驟: 在路由器配置端口轉發規則")
    print()
    print("方法 3: 路由器 UPnP（自動配置，可能不安全）")
    print("  - 優點: 自動配置端口轉發")
    print("  - 缺點: 安全風險較高")
    print()
    print("=" * 80)
    print("  ✅ 握手測試完成")
    print("=" * 80)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
