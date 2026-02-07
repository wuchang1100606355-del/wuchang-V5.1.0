#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設備連接納管腳本 - Chrome OS 設備 (端口 3477)
"""

import sys
import os
import json
import socket
import requests
from datetime import datetime
from typing import Dict, Optional

# 設備配置
DEVICE_TYPE = "CHROME_OS"
DEVICE_PORT = 3477
LOCAL_IP = "192.168.50.249"
ROUTER_IP = "192.168.50.1"

def check_port_availability(port: int, host: str = '0.0.0.0') -> bool:
    """檢查端口是否可用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.bind((host, port))
            return True
    except OSError:
        return False

def get_device_info(ip: str, port: int) -> Dict:
    """獲取設備信息"""
    try:
        # 嘗試連接到設備
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        result = s.connect_ex((ip, port))
        s.close()
        
        if result == 0:
            return {
                'ip': ip,
                'port': port,
                'status': 'connected',
                'reachable': True
            }
        else:
            return {
                'ip': ip,
                'port': port,
                'status': 'unreachable',
                'reachable': False
            }
    except Exception as e:
        return {
            'ip': ip,
            'port': port,
            'status': 'error',
            'error': str(e),
            'reachable': False
        }

def register_device(device_info: Dict) -> Dict:
    """註冊設備到系統"""
    enrollment_data = {
        'device_id': f"CHROME_OS_{device_info.get('ip', '').replace('.', '_')}",
        'device_type': 'CHROME_OS',
        'device_name': f"Chrome OS Device ({device_info.get('ip', 'Unknown')})",
        'ip_address': device_info.get('ip'),
        'port': DEVICE_PORT,
        'enrollment_time': datetime.now().isoformat(),
        'status': 'enrolled',
        'managed_by': 'Little J (小j)',
        'network': {
            'local_network': '192.168.50.0/24',
            'router_ip': ROUTER_IP,
            'connection_method': 'direct' if device_info.get('reachable') else 'relay'
        },
        'capabilities': {
            'web_access': True,
            'api_access': True,
            'remote_control': False,
            'file_sharing': False
        },
        'access_urls': {
            'command_center': f"http://{LOCAL_IP}/command_center",
            'design_report': f"http://{LOCAL_IP}/design_report",
            'handshake': f"http://{LOCAL_IP}/api/handshake"
        }
    }
    
    return enrollment_data

def create_enrollment_endpoint():
    """創建設備納管端點配置"""
    return {
        'endpoint': f'/api/device/enroll/{DEVICE_TYPE.lower()}',
        'port': DEVICE_PORT,
        'protocol': 'HTTP/HTTPS',
        'method': 'POST',
        'required_fields': ['device_id', 'device_name', 'ip_address', 'port']
    }

def main():
    print("=" * 80)
    print("  設備連接納管 - Chrome OS (端口 3477)")
    print("=" * 80)
    print()
    print(f"設備類型: {DEVICE_TYPE}")
    print(f"端口: {DEVICE_PORT}")
    print(f"納管時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 檢查端口狀態
    print("[1/4] 檢查端口 3477 狀態...")
    port_available = check_port_availability(DEVICE_PORT)
    if port_available:
        print(f"  ✓ 端口 {DEVICE_PORT} 可用")
    else:
        print(f"  ⚠ 端口 {DEVICE_PORT} 已被占用或不可用")
    print()
    
    # 2. 掃描網絡中的 Chrome OS 設備
    print("[2/4] 掃描網絡中的 Chrome OS 設備...")
    # 這裡可以擴展為實際的設備發現邏輯
    potential_devices = [
        {'ip': '192.168.50.84', 'name': 'LUNGsMSI'},
        {'ip': '192.168.50.88', 'name': 'POS-PC'},
    ]
    
    chrome_devices = []
    for device in potential_devices:
        info = get_device_info(device['ip'], DEVICE_PORT)
        if info.get('reachable') or device['name'].upper() in ['CHROME', 'CHROMEBOOK']:
            chrome_devices.append({**device, **info})
    
    if chrome_devices:
        print(f"  找到 {len(chrome_devices)} 個可能的 Chrome OS 設備:")
        for dev in chrome_devices:
            print(f"    • {dev.get('name', 'Unknown')} ({dev.get('ip')})")
    else:
        print("  ⚠ 未發現 Chrome OS 設備（需要手動指定 IP）")
    print()
    
    # 3. 創建設備納管配置
    print("[3/4] 創建設備納管配置...")
    enrollment_config = create_enrollment_endpoint()
    print(f"  端點: {enrollment_config['endpoint']}")
    print(f"  端口: {enrollment_config['port']}")
    print(f"  協議: {enrollment_config['protocol']}")
    print()
    
    # 4. 註冊設備（示例）
    print("[4/4] 註冊設備...")
    if chrome_devices:
        for device in chrome_devices:
            enrollment_data = register_device(device)
            print(f"  註冊設備: {enrollment_data['device_name']}")
            print(f"    設備 ID: {enrollment_data['device_id']}")
            print(f"    狀態: {enrollment_data['status']}")
    else:
        # 創建通用 Chrome OS 設備配置
        sample_device = {'ip': '0.0.0.0', 'port': DEVICE_PORT}
        enrollment_data = register_device(sample_device)
        print(f"  創建通用配置: {enrollment_data['device_name']}")
        print(f"    端口: {enrollment_data['port']}")
        print(f"    狀態: 等待連接")
    print()
    
    # 保存配置
    config_file = f'chrome_os_enrollment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'device_type': DEVICE_TYPE,
                'port': DEVICE_PORT,
                'enrollment_config': enrollment_config,
                'devices': chrome_devices if chrome_devices else [enrollment_data]
            }, f, ensure_ascii=False, indent=2)
        print(f"✓ 配置已保存: {config_file}")
    except Exception as e:
        print(f"⚠ 保存配置失敗: {e}")
    
    print()
    print("=" * 80)
    print("  設備納管配置完成")
    print("=" * 80)
    print()
    print("下一步:")
    print("  1. 配置 Odoo 設備管理端點")
    print("  2. 設置端口 3477 的服務監聽")
    print("  3. 配置設備訪問權限")
    print(f"  4. Chrome OS 設備可通過端口 {DEVICE_PORT} 連接")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
