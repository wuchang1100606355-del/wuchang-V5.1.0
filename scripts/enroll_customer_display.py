#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客戶顯示器納管腳本
用途：將客戶顯示器納管到 Wuchang OS 系統
"""

import requests
import argparse
import socket
from datetime import datetime

DEFAULT_VM_IP = "192.168.50.249"
# 客戶顯示器就是 Chrome OS 設備，使用 Chrome OS 納管端點或客戶顯示器相容端點
DEFAULT_ENROLLMENT_URL_CUSTOMER_DISPLAY = f"http://{DEFAULT_VM_IP}:8069/api/device/enroll/customer_display"
DEFAULT_ENROLLMENT_URL_CHROME_OS = f"http://{DEFAULT_VM_IP}:8069/api/device/enroll/chrome_os"


def get_local_ip():
    """獲取本機 IP 地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'


def enroll_customer_display(
    device_name=None,
    ip_address=None,
    port=None,
    mac_address=None,
    display_url=None,
    vm_ip=None
):
    """納管客戶顯示器到系統"""
    
    vm_ip = vm_ip or DEFAULT_VM_IP
    # 使用客戶顯示器相容端點（會轉發到 Chrome OS 納管）
    enrollment_url = f"http://{vm_ip}:8069/api/device/enroll/customer_display"
    
    # 準備納管資料
    enrollment_data = {
        'device_name': device_name or f"Customer Display ({datetime.now().strftime('%H:%M:%S')})",
        'ip_address': ip_address or get_local_ip(),
        'port': port or 3477,
        'mac_address': mac_address or '',
        'device_purpose': 'customer_display',  # 標記為客戶顯示器
        'display_url': display_url or f'http://{vm_ip}:8069/pos/customer_display',
        'enrollment_time': datetime.now().isoformat(),
    }
    
    print(f"正在納管客戶顯示器到: {enrollment_url}")
    print(f"設備資訊:")
    print(f"  名稱: {enrollment_data['device_name']}")
    print(f"  IP 地址: {enrollment_data['ip_address']}")
    print(f"  通訊埠: {enrollment_data['port']}")
    print(f"  顯示 URL: {enrollment_data['display_url']}")
    print()
    
    try:
        response = requests.post(
            enrollment_url,
            json=enrollment_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 客戶顯示器納管成功！")
            print(f"   設備 ID: {result.get('device', {}).get('id', 'N/A')}")
            print(f"   狀態: {result.get('status', 'N/A')}")
            print(f"   動作: {result.get('action', 'N/A')}")
            return result
        else:
            print(f"❌ 納管失敗: HTTP {response.status_code}")
            print(f"   回應: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ 無法連接到 VM 伺服器 {vm_ip}:8069")
        print("   請確認：")
        print("     1. VM 伺服器的 Odoo 服務正在運行")
        print("     2. 網路連線正常")
        print("     3. IP 地址正確")
        return None
    except Exception as e:
        print(f"❌ 納管失敗: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='客戶顯示器納管')
    parser.add_argument('--device-name', type=str, default=None,
                        help='設備名稱（預設: 自動生成）')
    parser.add_argument('--ip', type=str, default=None,
                        help='設備 IP 地址（預設: 自動偵測）')
    parser.add_argument('--port', type=int, default=None,
                        help='設備通訊埠（可選）')
    parser.add_argument('--mac', type=str, default=None,
                        help='MAC 地址（可選）')
    parser.add_argument('--display-url', type=str, default=None,
                        help='顯示 URL（預設: http://VM_IP:8069/pos/customer_display）')
    parser.add_argument('--vm-ip', type=str, default=DEFAULT_VM_IP,
                        help=f'VM 伺服器 IP（預設: {DEFAULT_VM_IP}）')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  客戶顯示器納管")
    print("=" * 60)
    print()
    
    # 執行納管
    result = enroll_customer_display(
        device_name=args.device_name,
        ip_address=args.ip,
        port=args.port,
        mac_address=args.mac,
        display_url=args.display_url,
        vm_ip=args.vm_ip
    )
    
    if result:
        print()
        print("下一步：")
        print("  1. 在 Odoo 中確認設備記錄")
        print("  2. 在 Sister Control 中配置客戶顯示器 URL")
        print("  3. 測試客戶顯示器連線和功能")
        return 0
    else:
        return 1


if __name__ == '__main__':
    exit(main())
