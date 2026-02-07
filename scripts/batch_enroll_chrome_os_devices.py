#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量納管 Chrome OS 設備腳本
用途：將昨日已納管的 Chrome OS 設備批量寫入管理系統
"""

import requests
import argparse
import json
from datetime import datetime, timedelta

DEFAULT_VM_IP = "192.168.50.249"
DEFAULT_ENROLLMENT_URL = f"http://{DEFAULT_VM_IP}:8069/api/device/enroll/chrome_os"


def enroll_chrome_os_device(
    device_name,
    ip_address,
    port=3477,
    mac_address=None,
    device_purpose=None,
    display_url=None,
    vm_ip=None
):
    """納管 Chrome OS 設備"""
    
    vm_ip = vm_ip or DEFAULT_VM_IP
    enrollment_url = f"http://{vm_ip}:8069/api/device/enroll/chrome_os"
    
    enrollment_data = {
        'device_id': f"CHROME_OS_{device_name.replace(' ', '_').upper()}",
        'device_name': device_name,
        'ip_address': ip_address,
        'port': port,
        'mac_address': mac_address or '',
        'device_purpose': device_purpose or '',  # 'customer_display', 'signage', 'other'
        'display_url': display_url or '',
        'enrollment_time': datetime.now().isoformat(),
    }
    
    try:
        response = requests.post(
            enrollment_url,
            json=enrollment_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {device_name} ({ip_address}:{port}) - {result.get('action', 'N/A')}")
            return result
        else:
            print(f"❌ {device_name} ({ip_address}:{port}) - HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ {device_name} ({ip_address}:{port}) - {e}")
        return None


def batch_enroll_from_file(devices_file, vm_ip=None):
    """從檔案批量納管設備"""
    
    try:
        with open(devices_file, 'r', encoding='utf-8') as f:
            devices = json.load(f)
    except Exception as e:
        print(f"❌ 無法讀取設備檔案: {e}")
        return False
    
    print("=" * 60)
    print("  批量納管 Chrome OS 設備")
    print("=" * 60)
    print()
    
    success_count = 0
    fail_count = 0
    
    for device in devices:
        result = enroll_chrome_os_device(
            device_name=device.get('name', 'Unknown'),
            ip_address=device.get('ip'),
            port=device.get('port', 3477),
            mac_address=device.get('mac'),
            device_purpose=device.get('purpose', ''),  # 'customer_display', 'signage', 'other'
            display_url=device.get('display_url', ''),
            vm_ip=vm_ip
        )
        
        if result:
            success_count += 1
        else:
            fail_count += 1
    
    print()
    print("=" * 60)
    print(f"  納管完成: 成功 {success_count} 個，失敗 {fail_count} 個")
    print("=" * 60)
    
    return fail_count == 0


def main():
    parser = argparse.ArgumentParser(description='批量納管 Chrome OS 設備')
    parser.add_argument('--devices-file', type=str, required=True,
                        help='設備清單檔案（JSON 格式）')
    parser.add_argument('--vm-ip', type=str, default=DEFAULT_VM_IP,
                        help=f'VM 伺服器 IP（預設: {DEFAULT_VM_IP}）')
    parser.add_argument('--create-template', action='store_true',
                        help='建立範本檔案')
    
    args = parser.parse_args()
    
    # 建立範本檔案
    if args.create_template:
        template = {
            "devices": [
                {
                    "name": "Chrome OS Customer Display 1",
                    "ip": "192.168.50.XXX",
                    "port": 3477,
                    "mac": "XX:XX:XX:XX:XX:XX",
                    "purpose": "customer_display",
                    "display_url": "http://192.168.50.249:8069/pos/customer_display"
                },
                {
                    "name": "Chrome OS Device 2",
                    "ip": "192.168.50.XXX",
                    "port": 3477,
                    "mac": "",
                    "purpose": "other"
                }
            ]
        }
        template_file = "chrome_os_devices_template.json"
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        print(f"✅ 範本檔案已建立: {template_file}")
        return 0
    
    # 批量納管
    success = batch_enroll_from_file(args.devices_file, args.vm_ip)
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
