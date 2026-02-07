#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
偵測設備並查找納管方案
"""

import sys
import os
import socket
import subprocess
import json
import re
from datetime import datetime

TARGET_IP = "192.168.50.88"

def get_device_info(ip):
    """獲取設備詳細信息"""
    info = {
        'ip': ip,
        'hostname': 'Unknown',
        'mac': 'Unknown',
        'vendor': 'Unknown',
        'ports': [],
        'device_type': 'unknown',
        'os_type': 'Unknown'
    }
    
    try:
        # 獲取主機名
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            info['hostname'] = hostname
        except:
            pass
        
        # 從 ARP 表獲取 MAC 地址
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(['arp', '-a', ip], capture_output=True, text=True, check=False)
                match = re.search(r'(\w{2}-\w{2}-\w{2}-\w{2}-\w{2}-\w{2})', result.stdout, re.IGNORECASE)
                if match:
                    info['mac'] = match.group(1).upper()
            else:  # Linux/WSL
                result = subprocess.run(['arp', '-n', ip], capture_output=True, text=True, check=False)
                match = re.search(r'(\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2})', result.stdout, re.IGNORECASE)
                if match:
                    info['mac'] = match.group(1).upper()
        except:
            pass
        
        # 掃描常用端口
        common_ports = {
            22: 'SSH',
            80: 'HTTP',
            443: 'HTTPS',
            3389: 'RDP',
            8069: 'Odoo',
            8080: 'HTTP-Alt',
            3477: 'Chrome OS/STUN',
            5000: 'Custom API',
            9000: 'Portainer',
            3001: 'Uptime Kuma'
        }
        
        for port, name in common_ports.items():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                result = s.connect_ex((ip, port))
                s.close()
                if result == 0:
                    info['ports'].append({'port': port, 'name': name})
            except:
                pass
        
        # 根據端口推斷設備類型
        port_names = [p['name'] for p in info['ports']]
        if 3477 in [p['port'] for p in info['ports']]:
            info['device_type'] = 'chrome_os'
            info['os_type'] = 'Chrome OS'
        elif 'Odoo' in port_names:
            info['device_type'] = 'workstation'
            info['os_type'] = 'Linux/Windows with Odoo'
        elif 'RDP' in port_names:
            info['device_type'] = 'workstation'
            info['os_type'] = 'Windows'
        elif 'SSH' in port_names and 'HTTP' in port_names:
            info['device_type'] = 'workstation'
            info['os_type'] = 'Linux'
        elif 'POS' in info['hostname'].upper():
            info['device_type'] = 'pos'
            info['os_type'] = 'POS System'
        
        # 根據主機名判斷
        if 'POS' in info['hostname'].upper():
            info['device_type'] = 'pos'
            info['os_type'] = 'POS System'
        elif 'CHROME' in info['hostname'].upper():
            info['device_type'] = 'chrome_os'
            info['os_type'] = 'Chrome OS'
            
    except Exception as e:
        print(f"  ⚠ 獲取設備信息時出錯: {e}")
    
    return info

def check_enrollment_status(ip):
    """檢查設備是否已納管（模擬，實際應查詢 Odoo）"""
    # 這裡應該查詢 Odoo 數據庫
    # 暫時返回模擬數據
    return {
        'enrolled': False,
        'device_id': None,
        'enrollment_date': None,
        'status': 'unknown'
    }

def find_suitable_plans(device_info):
    """查找適用的納管方案"""
    suitable_plans = []
    
    device_type = device_info['device_type']
    
    # 根據設備類型匹配方案
    if device_type == 'chrome_os':
        suitable_plans.append({
            'plan_id': 'device_control_plan_chrome_os_default',
            'plan_name': 'Chrome OS 設備長期納管方案',
            'match_reason': '設備類型匹配 (Chrome OS)',
            'priority': 'high',
            'port': 3477
        })
    
    # 如果設備有監控需求，添加全設備監控方案
    suitable_plans.append({
        'plan_id': 'device_control_plan_all_monitoring',
        'plan_name': '全設備長期監控方案',
        'match_reason': '適用於所有設備',
        'priority': 'medium'
    })
    
    # 如果設備是路由器或網絡設備
    if device_info.get('ports') and any(p['port'] == 80 for p in device_info['ports']):
        suitable_plans.append({
            'plan_id': 'device_control_plan_router_relay',
            'plan_name': '路由器中繼長期控制方案',
            'match_reason': '檢測到網絡服務',
            'priority': 'critical'
        })
    
    return suitable_plans

def main():
    print("=" * 80)
    print(f"  偵測設備 {TARGET_IP} 並查找納管方案")
    print("=" * 80)
    print()
    print(f"目標 IP: {TARGET_IP}")
    print(f"偵測時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 檢查設備是否在線
    print("[1/4] 檢查設備連接狀態...")
    try:
        result = subprocess.run(
            ['ping', '-n', '1', '-w', '1000', TARGET_IP] if os.name == 'nt' 
            else ['ping', '-c', '1', '-W', '1', TARGET_IP],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"  ✓ 設備 {TARGET_IP} 在線")
        else:
            print(f"  ⚠ 設備 {TARGET_IP} 可能離線或無法訪問")
            return 1
    except Exception as e:
        print(f"  ⚠ 無法檢查設備狀態: {e}")
    print()
    
    # 2. 獲取設備詳細信息
    print("[2/4] 獲取設備詳細信息...")
    device_info = get_device_info(TARGET_IP)
    print(f"  主機名: {device_info['hostname']}")
    print(f"  MAC 地址: {device_info['mac']}")
    print(f"  設備類型: {device_info['device_type']}")
    print(f"  操作系統: {device_info['os_type']}")
    
    if device_info['ports']:
        port_list = ', '.join([f"{p['name']}({p['port']})" for p in device_info['ports']])
        print(f"  開放端口: {port_list}")
    else:
        print(f"  開放端口: 未檢測到常用端口")
    print()
    
    # 3. 檢查納管狀態
    print("[3/4] 檢查設備納管狀態...")
    enrollment_status = check_enrollment_status(TARGET_IP)
    if enrollment_status['enrolled']:
        print(f"  ✓ 設備已納管")
        print(f"    設備 ID: {enrollment_status['device_id']}")
        print(f"    納管時間: {enrollment_status['enrollment_date']}")
        print(f"    狀態: {enrollment_status['status']}")
    else:
        print(f"  ⚠ 設備尚未納管")
    print()
    
    # 4. 查找適用的納管方案
    print("[4/4] 查找適用的納管方案...")
    suitable_plans = find_suitable_plans(device_info)
    
    if suitable_plans:
        print(f"  找到 {len(suitable_plans)} 個適用方案:")
        for i, plan in enumerate(suitable_plans, 1):
            print(f"\n  方案 {i}: {plan['plan_name']}")
            print(f"    方案 ID: {plan['plan_id']}")
            print(f"    匹配原因: {plan['match_reason']}")
            print(f"    優先級: {plan['priority']}")
            if 'port' in plan:
                print(f"    相關端口: {plan['port']}")
    else:
        print(f"  ⚠ 未找到完全匹配的方案，建議創建新方案")
    print()
    
    # 生成報告
    report = {
        'timestamp': datetime.now().isoformat(),
        'target_ip': TARGET_IP,
        'device_info': device_info,
        'enrollment_status': enrollment_status,
        'suitable_plans': suitable_plans,
        'recommendations': []
    }
    
    # 生成建議
    if not enrollment_status['enrolled']:
        report['recommendations'].append({
            'action': 'enroll',
            'message': '設備尚未納管，建議執行納管操作',
            'suggested_plan': suitable_plans[0]['plan_id'] if suitable_plans else None
        })
    
    if device_info['device_type'] == 'chrome_os' and 3477 in [p['port'] for p in device_info['ports']]:
        report['recommendations'].append({
            'action': 'enroll_chrome_os',
            'message': '檢測到 Chrome OS 設備，建議使用 Chrome OS 納管方案',
            'endpoint': f'/api/device/enroll/chrome_os',
            'port': 3477
        })
    
    # 保存報告
    report_file = f'device_detection_report_{TARGET_IP.replace(".", "_")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"✓ 偵測報告已保存: {report_file}")
    except Exception as e:
        print(f"⚠ 保存報告失敗: {e}")
    
    print()
    print("=" * 80)
    print("  偵測完成")
    print("=" * 80)
    print()
    
    # 顯示建議
    if report['recommendations']:
        print("建議操作:")
        for rec in report['recommendations']:
            print(f"  • {rec['message']}")
            if 'endpoint' in rec:
                print(f"    端點: {rec['endpoint']}")
            if 'port' in rec:
                print(f"    端口: {rec['port']}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
