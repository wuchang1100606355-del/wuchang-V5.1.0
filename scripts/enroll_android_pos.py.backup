#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android POS 設備納管腳本
用途：將 Android POS 設備納管到 Wuchang OS 系統
"""

import sys
import json
import socket
import requests
import subprocess
from datetime import datetime
from typing import Dict, Optional

# 預設設定
DEFAULT_VM_IP = "192.168.50.84"
DEFAULT_ENROLLMENT_URL = f"http://{DEFAULT_VM_IP}:8069/api/device/enroll/android"

def get_device_info_android():
    """獲取 Android 設備資訊（需要在設備上執行）"""
    device_info = {
        'device_name': None,
        'android_version': None,
        'device_id': None,
        'ip_address': None,
        'mac_address': None,
        'developer_mode': False,
        'demo_mode': False,
    }
    
    try:
        # 獲取設備名稱
        result = subprocess.run(['getprop', 'ro.product.model'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            device_info['device_name'] = result.stdout.strip()
        
        # 獲取 Android 版本
        result = subprocess.run(['getprop', 'ro.build.version.release'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            device_info['android_version'] = result.stdout.strip()
        
        # 獲取設備 ID
        result = subprocess.run(['getprop', 'ro.serialno'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            device_info['device_id'] = result.stdout.strip()
        
        # 檢查開發者模式
        result = subprocess.run(['getprop', 'ro.debuggable'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            device_info['developer_mode'] = result.stdout.strip() == '1'
        
        # 檢查 Demo Mode（UI 示範模式）
        result = subprocess.run(['settings', 'get', 'global', 'device_demo_mode'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            device_info['demo_mode'] = result.stdout.strip() == '1'
        
    except Exception as e:
        print(f"⚠ 無法獲取部分設備資訊: {e}")
    
    return device_info

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

def get_mac_address():
    """獲取 MAC 地址"""
    try:
        import uuid
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                       for elements in range(0,2*6,2)][::-1])
        return mac
    except Exception:
        return '00:00:00:00:00:00'

def enroll_device(device_name, android_version, device_id=None, ip_address=None, 
                 port=None, mac_address=None, developer_mode=False, demo_mode=False, vm_ip=None):
    """納管 Android POS 設備到系統"""
    
    vm_ip = vm_ip or DEFAULT_VM_IP
    enrollment_url = f"http://{vm_ip}:8069/api/device/enroll/android"
    
    # 準備納管資料
    enrollment_data = {
        'device_id': device_id or f"ANDROID_{device_name.replace(' ', '_').upper()}",
        'device_name': device_name,
        'device_type': 'pos',
        'os_type': 'android',
        'os_version': android_version,
        'ip_address': ip_address or get_local_ip(),
        'port': port,
        'mac_address': mac_address or get_mac_address(),
        'developer_mode': developer_mode,
        'demo_mode': demo_mode,
        'debug_options': {
            'usb': True,  # USB 偵錯已開啟
            'gpu': True,  # GPU 偵錯已開啟
            'wifi': True,  # WiFi 偵錯已開啟
        },
        'enrollment_time': datetime.now().isoformat(),
        'capabilities': {
            'kiosk_mode': True,
            'remote_management': True,
            'app_deployment': True,
            'data_sync': True,
        }
    }
    
    print(f"正在納管設備到: {enrollment_url}")
    print(f"設備資訊:")
    print(f"  名稱: {device_name}")
    print(f"  Android 版本: {android_version}")
    print(f"  設備 ID: {enrollment_data['device_id']}")
    print(f"  IP 地址: {enrollment_data['ip_address']}")
    if port:
        print(f"  通訊埠: {port}")
    print(f"  開發者模式: {'已開啟' if developer_mode else '未開啟'}")
    print(f"  Demo 模式: {'已開啟' if demo_mode else '未開啟'}")
    print(f"  偵錯選項:")
    print(f"    USB 偵錯: ✅ 已開啟")
    print(f"    GPU 偵錯: ✅ 已開啟")
    print(f"    WiFi 偵錯: ✅ 已開啟")
    print()
    
    try:
        response = requests.post(
            enrollment_url,
            json=enrollment_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 設備納管成功！")
            print(f"   設備 ID: {result.get('device', {}).get('id', 'N/A')}")
            print(f"   狀態: {result.get('status', 'N/A')}")
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

def check_demo_mode_requirement():
    """檢查是否需要開啟 Demo Mode"""
    print("=" * 60)
    print("關於 Android UI 示範模式 (Demo Mode)")
    print("=" * 60)
    print()
    print("❓ 是否需要開啟 Demo Mode？")
    print()
    print("📋 Demo Mode 的作用：")
    print("  • 顯示示範內容（如時間、電池等）")
    print("  • 通常用於零售展示環境")
    print("  • 會顯示「示範模式」標記")
    print()
    print("✅ 對於 POS 設備：")
    print("  • 通常不需要開啟 Demo Mode")
    print("  • 開發者模式已足夠進行設備管理")
    print("  • 如果需要 Kiosk 模式，應使用 Google Workspace MDM")
    print()
    print("💡 建議：")
    print("  • 保持 Demo Mode 關閉")
    print("  • 使用 Google Workspace MDM 進行 Kiosk 模式設定")
    print("  • 透過 MDM 鎖定到 Odoo POS 應用程式")
    print()
    print("=" * 60)
    print()

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Android POS 設備納管')
    parser.add_argument('--device-name', type=str, default='v3_mix_edla_gl',
                        help='設備名稱（預設: v3_mix_edla_gl）')
    parser.add_argument('--android-version', type=str, default='13',
                        help='Android 版本（預設: 13）')
    parser.add_argument('--device-id', type=str, default=None,
                        help='設備 ID（預設: 自動生成）')
    parser.add_argument('--ip', type=str, default='192.168.50.86',
                        help='設備 IP 地址（預設: 192.168.50.86）')
    parser.add_argument('--port', type=int, default=41895,
                        help='設備通訊埠（預設: 41895）')
    parser.add_argument('--mac', type=str, default=None,
                        help='MAC 地址（預設: 自動偵測）')
    parser.add_argument('--vm-ip', type=str, default=DEFAULT_VM_IP,
                        help=f'VM 伺服器 IP（預設: {DEFAULT_VM_IP}）')
    parser.add_argument('--developer-mode', action='store_true',
                        help='標記開發者模式已開啟')
    parser.add_argument('--demo-mode', action='store_true',
                        help='標記 Demo Mode 已開啟（不建議）')
    parser.add_argument('--check-demo', action='store_true',
                        help='檢查 Demo Mode 需求說明')
    
    args = parser.parse_args()
    
    # 顯示 Demo Mode 說明
    if args.check_demo:
        check_demo_mode_requirement()
        return 0
    
    print("=" * 60)
    print("  Android POS 設備納管")
    print("=" * 60)
    print()
    
    # 嘗試獲取設備資訊（如果在 Android 設備上執行）
    try:
        android_info = get_device_info_android()
        if android_info.get('device_name'):
            print("✓ 偵測到 Android 設備資訊")
            device_name = args.device_name or android_info['device_name']
            android_version = args.android_version or android_info.get('android_version', '13')
            device_id = args.device_id or android_info.get('device_id')
            developer_mode = args.developer_mode or android_info.get('developer_mode', False)
            demo_mode = args.demo_mode or android_info.get('demo_mode', False)
        else:
            # 使用命令行參數
            device_name = args.device_name
            android_version = args.android_version
            device_id = args.device_id
            developer_mode = args.developer_mode
            demo_mode = args.demo_mode
    except Exception:
        # 使用命令行參數
        device_name = args.device_name
        android_version = args.android_version
        device_id = args.device_id
        developer_mode = args.developer_mode
        demo_mode = args.demo_mode
    
    # 檢查 Demo Mode
    if demo_mode:
        print("⚠ 警告: Demo Mode 已開啟")
        print("   建議關閉 Demo Mode，使用 Google Workspace MDM 進行 Kiosk 模式設定")
        print()
    
    # 執行納管
    result = enroll_device(
        device_name=device_name,
        android_version=android_version,
        device_id=device_id,
        ip_address=args.ip,
        port=args.port,
        mac_address=args.mac,
        developer_mode=developer_mode,
        demo_mode=demo_mode,
        vm_ip=args.vm_ip
    )
    
    if result:
        print()
        print("=" * 60)
        print("  納管完成")
        print("=" * 60)
        print()
        print("下一步：")
        print("  1. 在 Google Workspace Admin Console 註冊此設備")
        print("  2. 設定 Kiosk 模式（鎖定到 Odoo POS 應用）")
        print("  3. 配置 Google Drive 同步")
        print("  4. 測試設備連線和功能")
        print()
        return 0
    else:
        print()
        print("=" * 60)
        print("  納管失敗")
        print("=" * 60)
        print()
        return 1

if __name__ == '__main__':
    import argparse
    sys.exit(main())
