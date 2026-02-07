#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POS 設備 AnyDesk 設定腳本
用途：為 POS 設備（v3_mix_edla_gl）設定 AnyDesk 遠程桌面
"""

import requests
import argparse
from datetime import datetime

DEFAULT_VM_IP = "192.168.50.249"
DEFAULT_ANYDESK_ID = "748464958"  # v3_mix_edla_gl 的 AnyDesk ID


def update_anydesk_config(
    device_name="v3_mix_edla_gl",
    anydesk_id=None,
    anydesk_password=None,
    anydesk_configured=True,
    vm_ip=None
):
    """更新 POS 設備的 AnyDesk 設定"""
    
    vm_ip = vm_ip or DEFAULT_VM_IP
    
    # 先查詢設備
    query_url = f"http://{vm_ip}:8069/api/device/android/status"
    
    print(f"正在查詢設備: {device_name}")
    try:
        query_response = requests.get(
            query_url,
            params={'ip': '192.168.50.86'},  # v3_mix_edla_gl 的 IP
            timeout=10
        )
        
        if query_response.status_code == 200:
            device_info = query_response.json().get('device', {})
            device_id = device_info.get('id')
            print(f"✅ 找到設備 ID: {device_id}")
        else:
            print(f"⚠ 無法查詢設備，將使用納管 API 更新")
            device_id = None
    except Exception as e:
        print(f"⚠ 查詢設備失敗: {e}，將使用納管 API 更新")
        device_id = None
    
    # 使用納管 API 更新 AnyDesk 資訊
    enrollment_url = f"http://{vm_ip}:8069/api/device/enroll/android"
    
    enrollment_data = {
        'device_name': device_name,
        'ip_address': '192.168.50.86',
        'port': 41895,
        'os_version': '13',
        'developer_mode': True,
        'anydesk_id': anydesk_id or DEFAULT_ANYDESK_ID,
        'anydesk_password': anydesk_password or '',
        'anydesk_configured': anydesk_configured,
        'debug_options': {
            'usb': True,
            'gpu': True,
            'wifi': True
        }
    }
    
    print(f"\n正在更新 AnyDesk 設定...")
    print(f"  AnyDesk ID: {enrollment_data['anydesk_id']}")
    print(f"  設定狀態: {'已完成' if anydesk_configured else '未完成'}")
    
    try:
        response = requests.post(
            enrollment_url,
            json=enrollment_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ AnyDesk 設定已更新！")
            print(f"   設備: {result.get('device', {}).get('name', 'N/A')}")
            print(f"   AnyDesk ID: {result.get('device', {}).get('anydesk_id', 'N/A')}")
            print(f"   設定狀態: {'已完成' if result.get('device', {}).get('anydesk_configured') else '未完成'}")
            return result
        else:
            print(f"❌ 更新失敗: HTTP {response.status_code}")
            print(f"   回應: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ 無法連接到 VM 伺服器 {vm_ip}:8069")
        return None
    except Exception as e:
        print(f"❌ 更新失敗: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='POS 設備 AnyDesk 設定')
    parser.add_argument('--device-name', type=str, default='v3_mix_edla_gl',
                        help='設備名稱（預設: v3_mix_edla_gl）')
    parser.add_argument('--anydesk-id', type=str, default=DEFAULT_ANYDESK_ID,
                        help=f'AnyDesk ID（預設: {DEFAULT_ANYDESK_ID}）')
    parser.add_argument('--anydesk-password', type=str, default=None,
                        help='AnyDesk 密碼（可選）')
    parser.add_argument('--configured', action='store_true', default=False,
                        help='標記為已設定完成')
    parser.add_argument('--not-configured', action='store_true', default=False,
                        help='標記為未設定完成')
    parser.add_argument('--vm-ip', type=str, default=DEFAULT_VM_IP,
                        help=f'VM 伺服器 IP（預設: {DEFAULT_VM_IP}）')
    
    args = parser.parse_args()
    
    anydesk_configured = True if args.configured else (False if args.not_configured else False)
    
    print("=" * 60)
    print("  POS 設備 AnyDesk 設定")
    print("=" * 60)
    print()
    print(f"設備: {args.device_name}")
    print(f"AnyDesk ID: {args.anydesk_id}")
    print(f"設定狀態: {'已完成' if anydesk_configured else '未完成'}")
    print()
    
    result = update_anydesk_config(
        device_name=args.device_name,
        anydesk_id=args.anydesk_id,
        anydesk_password=args.anydesk_password,
        anydesk_configured=anydesk_configured,
        vm_ip=args.vm_ip
    )
    
    if result:
        print()
        print("下一步：")
        print("  1. 在設備上完成 AnyDesk 設定")
        print("  2. 測試遠程連線")
        print("  3. 確認設定完成後，執行：")
        print(f"     python scripts\\configure_anydesk_pos.py --configured")
        return 0
    else:
        return 1


if __name__ == '__main__':
    exit(main())
