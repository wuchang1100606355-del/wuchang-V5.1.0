#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome OS 設備納管客戶端腳本
用於 Chrome OS 設備主動連接並納管到系統
"""

import sys
import json
import requests
import socket
from datetime import datetime

# 配置
SERVER_URL = "http://192.168.50.249"  # 本地服務器
ENROLLMENT_PORT = 3477  # Chrome OS 納管端口
ENROLLMENT_ENDPOINT = f"{SERVER_URL}/api/device/enroll/chrome_os"

def get_local_ip():
    """獲取本機 IP 地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def get_device_info():
    """獲取設備信息"""
    return {
        'device_id': f"CHROME_OS_{get_local_ip().replace('.', '_')}",
        'device_name': f"Chrome OS Device ({socket.gethostname()})",
        'ip_address': get_local_ip(),
        'mac_address': '',  # Chrome OS 可能無法直接獲取 MAC
        'port': ENROLLMENT_PORT,
        'os_version': 'Chrome OS',
        'timestamp': datetime.now().isoformat()
    }

def enroll_device():
    """執行設備納管"""
    print("=" * 70)
    print("  Chrome OS 設備納管")
    print("=" * 70)
    print()
    print(f"服務器: {SERVER_URL}")
    print(f"端口: {ENROLLMENT_PORT}")
    print()
    
    device_info = get_device_info()
    print("設備信息:")
    print(f"  設備 ID: {device_info['device_id']}")
    print(f"  設備名稱: {device_info['device_name']}")
    print(f"  IP 地址: {device_info['ip_address']}")
    print(f"  端口: {device_info['port']}")
    print()
    
    print("正在連接到納管服務器...")
    try:
        response = requests.post(
            ENROLLMENT_ENDPOINT,
            json=device_info,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ 納管成功!")
            print()
            print("納管結果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        else:
            print(f"✗ 納管失敗 (狀態碼: {response.status_code})")
            print(f"  響應: {response.text[:200]}")
            return 1
    except requests.exceptions.ConnectionError:
        print(f"✗ 無法連接到服務器: {SERVER_URL}")
        print("  請確認服務器正在運行")
        return 1
    except Exception as e:
        print(f"✗ 納管錯誤: {e}")
        return 1

def send_heartbeat():
    """發送心跳"""
    heartbeat_endpoint = f"{SERVER_URL}/api/device/chrome_os/heartbeat"
    device_info = get_device_info()
    
    try:
        response = requests.post(
            heartbeat_endpoint,
            json={'ip_address': device_info['ip_address']},
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        if response.status_code == 200:
            print(f"✓ 心跳發送成功: {datetime.now().strftime('%H:%M:%S')}")
        else:
            print(f"⚠ 心跳發送失敗: {response.status_code}")
    except Exception as e:
        print(f"⚠ 心跳錯誤: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'heartbeat':
        send_heartbeat()
    else:
        sys.exit(enroll_device())
