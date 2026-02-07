#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通知 UI 端電腦 - 設計方案報告通知
"""

import sys
import os
import json
import requests
import socket
from datetime import datetime
from typing import List, Dict, Optional

# UI 設備列表（從之前的偵測結果）
UI_DEVICES = [
    {
        'ip': '192.168.50.84',
        'name': 'LUNGsMSI.wuchang.life',
        'type': '可能的 Odoo 實例',
        'ports': [22, 80, 443, 8080, 8069]
    },
    {
        'ip': '192.168.50.88',
        'name': 'POS-PC.wuchang.life',
        'type': 'POS 系統電腦',
        'ports': []
    },
    {
        'ip': '192.168.50.249',
        'name': 'Home-commput.wuchang.life',
        'type': '本機（當前主機）',
        'ports': [22, 3389]
    }
]

# 通知消息
NOTIFICATION_MESSAGE = {
    'title': '小J 指揮通道設計方案報告',
    'message': '專用指揮通道 UI 設計方案已完成，請查看報告。',
    'timestamp': datetime.now().isoformat(),
    'report_url': 'http://192.168.50.249/design_report',
    'command_center_url': 'http://192.168.50.249/command_center',
    'access_code': 'J2025',
    'details': {
        'designer': 'Little J (小j)',
        'completion_date': '2026-01-07',
        'status': '設計完成，等待部署',
        'features': [
            '系統狀態監控',
            '網絡狀態顯示',
            '快速操作按鈕',
            '命令控制台'
        ]
    }
}

def check_port_open(ip: str, port: int, timeout: float = 1.0) -> bool:
    """檢查端口是否開放"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((ip, port))
        s.close()
        return result == 0
    except Exception:
        return False

def send_http_notification(ip: str, port: int = 80, path: str = '/api/notify') -> Dict:
    """通過 HTTP 發送通知"""
    try:
        url = f"http://{ip}:{port}{path}"
        response = requests.post(
            url,
            json=NOTIFICATION_MESSAGE,
            timeout=5,
            headers={'Content-Type': 'application/json'}
        )
        return {
            'success': response.status_code == 200,
            'status_code': response.status_code,
            'response': response.text[:200]
        }
    except requests.exceptions.ConnectionError:
        return {'success': False, 'error': '連接失敗'}
    except requests.exceptions.Timeout:
        return {'success': False, 'error': '請求超時'}
    except Exception as e:
        return {'success': False, 'error': str(e)[:100]}

def send_odoo_notification(ip: str, port: int = 8069) -> Dict:
    """通過 Odoo 發送通知（如果設備運行 Odoo）"""
    try:
        # 嘗試通過 Odoo Web 界面發送通知
        # 這裡可以通過 Odoo XML-RPC 或 HTTP API
        url = f"http://{ip}:{port}/web"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            # Odoo 可訪問，可以進一步發送通知
            return {
                'success': True,
                'message': f'Odoo 實例可訪問 ({ip}:{port})',
                'suggestion': '可以通過 Odoo 內部通知系統發送消息'
            }
        return {'success': False, 'error': f'HTTP {response.status_code}'}
    except Exception as e:
        return {'success': False, 'error': str(e)[:100]}

def send_ssh_notification(ip: str, port: int = 22, username: str = None) -> Dict:
    """通過 SSH 發送通知（如果支持）"""
    # 這需要 SSH 客戶端，暫時返回建議
    return {
        'success': False,
        'message': 'SSH 通知需要 SSH 客戶端支持',
        'suggestion': f'可以通過 SSH 連接到 {ip}:{port} 發送通知'
    }

def create_notification_file(device: Dict) -> str:
    """創建通知文件供設備讀取"""
    try:
        notification_data = {
            **NOTIFICATION_MESSAGE,
            'target_device': device,
            'notification_method': 'file'
        }
        
        # 創建共享目錄中的通知文件
        notification_dir = 'notifications'
        os.makedirs(notification_dir, exist_ok=True)
        
        filename = f"{notification_dir}/notification_{device['ip'].replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(notification_data, f, ensure_ascii=False, indent=2)
        
        return filename
    except Exception as e:
        return None

def send_network_broadcast(message: str, port: int = 9999) -> Dict:
    """發送網絡廣播通知"""
    try:
        # UDP 廣播
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        data = json.dumps({
            **NOTIFICATION_MESSAGE,
            'broadcast': True
        }).encode('utf-8')
        
        # 發送到本地網絡廣播地址
        local_ip = socket.gethostbyname(socket.gethostname())
        network = '.'.join(local_ip.split('.')[:-1]) + '.255'
        
        sock.sendto(data, (network, port))
        sock.close()
        
        return {
            'success': True,
            'message': f'已發送廣播到 {network}:{port}'
        }
    except Exception as e:
        return {'success': False, 'error': str(e)[:100]}

def notify_device(device: Dict) -> Dict:
    """通知單個設備"""
    ip = device['ip']
    name = device['name']
    ports = device.get('ports', [])
    
    print(f"\n通知設備: {name} ({ip})")
    print("-" * 70)
    
    results = {
        'device': device,
        'methods': []
    }
    
    # 方法 1: HTTP 通知（如果有 Web 服務）
    if 80 in ports or 8080 in ports:
        http_port = 80 if 80 in ports else 8080
        print(f"  [1] 嘗試 HTTP 通知 ({ip}:{http_port})...")
        result = send_http_notification(ip, http_port)
        results['methods'].append({
            'method': 'HTTP',
            'port': http_port,
            **result
        })
        if result.get('success'):
            print(f"    ✓ HTTP 通知發送成功")
        else:
            print(f"    ⚠ HTTP 通知失敗: {result.get('error', 'Unknown')}")
    
    # 方法 2: Odoo 通知（如果有 Odoo）
    if 8069 in ports:
        print(f"  [2] 檢測到 Odoo 實例 ({ip}:8069)...")
        result = send_odoo_notification(ip, 8069)
        results['methods'].append({
            'method': 'Odoo',
            'port': 8069,
            **result
        })
        if result.get('success'):
            print(f"    ✓ Odoo 實例可訪問")
            print(f"    💡 建議: 可以通過 Odoo 內部通知系統發送消息")
        else:
            print(f"    ⚠ Odoo 通知: {result.get('error', 'Unknown')}")
    
    # 方法 3: SSH 通知（如果有 SSH）
    if 22 in ports:
        print(f"  [3] 檢測到 SSH 端口 ({ip}:22)...")
        result = send_ssh_notification(ip, 22)
        results['methods'].append({
            'method': 'SSH',
            'port': 22,
            **result
        })
        print(f"    💡 建議: {result.get('suggestion', '可以通過 SSH 連接發送通知')}")
    
    # 方法 4: 創建通知文件
    print(f"  [4] 創建通知文件...")
    filename = create_notification_file(device)
    if filename:
        results['methods'].append({
            'method': 'File',
            'file': filename,
            'success': True
        })
        print(f"    ✓ 通知文件已創建: {filename}")
        print(f"    💡 建議: 可以通過共享目錄或文件同步方式讓設備讀取")
    else:
        results['methods'].append({
            'method': 'File',
            'success': False,
            'error': '無法創建文件'
        })
        print(f"    ⚠ 無法創建通知文件")
    
    return results

def main():
    print("=" * 70)
    print("  通知 UI 端電腦 - 設計方案報告通知")
    print("=" * 70)
    print()
    print(f"通知時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"通知內容: {NOTIFICATION_MESSAGE['title']}")
    print()
    
    # 檢查設備連接狀態
    print("檢查設備連接狀態...")
    active_devices = []
    
    for device in UI_DEVICES:
        ip = device['ip']
        # 檢查是否可 ping
        try:
            result = os.system(f"ping -n 1 -w 1000 {ip} >nul 2>&1")
            if result == 0:
                active_devices.append(device)
                print(f"  ✓ {device['name']} ({ip}) - 在線")
            else:
                print(f"  ⚠ {device['name']} ({ip}) - 離線或無法連接")
        except Exception:
            print(f"  ⚠ {device['name']} ({ip}) - 檢查失敗")
    
    print()
    
    if not active_devices:
        print("⚠ 沒有發現在線的 UI 設備")
        print()
        print("建議:")
        print("  1. 檢查網絡連接")
        print("  2. 確認設備 IP 地址")
        print("  3. 檢查防火牆設置")
        return 1
    
    print(f"發現 {len(active_devices)} 個在線設備，開始發送通知...")
    print()
    
    # 發送通知
    all_results = []
    for device in active_devices:
        if device['ip'] == '192.168.50.249':
            print(f"跳過本機: {device['name']}")
            continue
        
        result = notify_device(device)
        all_results.append(result)
        print()
    
    # 發送網絡廣播
    print("發送網絡廣播通知...")
    broadcast_result = send_network_broadcast(NOTIFICATION_MESSAGE['message'])
    if broadcast_result.get('success'):
        print(f"  ✓ {broadcast_result['message']}")
    else:
        print(f"  ⚠ 廣播失敗: {broadcast_result.get('error')}")
    
    print()
    print("=" * 70)
    print("  通知發送完成")
    print("=" * 70)
    print()
    
    # 生成通知報告
    notification_report = {
        'timestamp': datetime.now().isoformat(),
        'message': NOTIFICATION_MESSAGE,
        'results': all_results,
        'broadcast': broadcast_result
    }
    
    report_file = f"notification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(notification_report, f, ensure_ascii=False, indent=2)
    
    print(f"通知報告已保存: {report_file}")
    print()
    
    # 總結
    print("通知方法總結:")
    print("  1. HTTP 通知 - 通過 Web 服務發送")
    print("  2. Odoo 通知 - 如果設備運行 Odoo")
    print("  3. SSH 通知 - 通過 SSH 連接（需要配置）")
    print("  4. 文件通知 - 創建通知文件供設備讀取")
    print("  5. 網絡廣播 - UDP 廣播到整個網絡")
    print()
    print("💡 UI 設備可以通過以下方式查看報告:")
    print(f"  - 直接訪問: {NOTIFICATION_MESSAGE['report_url']}")
    print(f"  - 指揮通道: {NOTIFICATION_MESSAGE['command_center_url']}")
    print(f"  - 訪問代碼: {NOTIFICATION_MESSAGE['access_code']}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
