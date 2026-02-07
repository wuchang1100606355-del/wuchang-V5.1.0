#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
偵測目前連入的個人電腦和網絡設備
"""

import subprocess
import socket
import sys
import json
from datetime import datetime
from typing import List, Dict

def get_local_ip():
    """獲取本機 IP 地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return None

def get_hostname(ip: str) -> str:
    """獲取設備主機名"""
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return "Unknown"

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

def get_mac_vendor(mac: str) -> str:
    """根據 MAC 地址推測設備類型（簡化版）"""
    mac_prefix = mac[:8].upper().replace(':', '').replace('-', '')
    # 常見 MAC 前綴
    vendors = {
        '00155D': 'Microsoft/Xbox',
        '001E65': 'Apple',
        '002608': 'Apple',
        '001451': 'Apple',
        '000C29': 'VMware',
        '005056': 'VMware',
        '001B21': 'Intel',
        '00AA01': 'Intel',
        '001DD8': 'Samsung',
        '001CBF': 'Samsung',
        'F0DBE2': 'Apple',
        'ACDE48': 'Apple',
        'F8FFC2': 'Apple',
    }
    for prefix, vendor in vendors.items():
        if mac_prefix.startswith(prefix):
            return vendor
    return "Unknown"

def detect_from_arp():
    """從 ARP 表獲取連接過的設備"""
    devices = []
    try:
        if sys.platform == 'win32':
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True, timeout=10)
            lines = result.stdout.split('\n')
            for line in lines:
                if 'dynamic' in line.lower() or 'static' in line.lower():
                    parts = line.split()
                    if len(parts) >= 2:
                        ip = parts[0]
                        mac = parts[1] if len(parts) > 1 else "Unknown"
                        # 過濾本地 IP
                        if ip.startswith('192.168.') or ip.startswith('10.') or (ip.startswith('172.') and 16 <= int(ip.split('.')[1]) <= 31):
                            try:
                                hostname = get_hostname(ip)
                                vendor = get_mac_vendor(mac)
                                
                                # 檢查常見端口
                                ports = []
                                common_ports = {
                                    22: 'SSH',
                                    80: 'HTTP',
                                    443: 'HTTPS',
                                    8080: 'HTTP-Alt',
                                    5000: 'UPnP',
                                    8069: 'Odoo',
                                    3389: 'RDP',
                                    5900: 'VNC'
                                }
                                
                                for port, name in common_ports.items():
                                    if check_port_open(ip, port, 0.5):
                                        ports.append(f"{name}({port})")
                                
                                devices.append({
                                    'ip': ip,
                                    'mac': mac,
                                    'hostname': hostname,
                                    'vendor': vendor,
                                    'open_ports': ports,
                                    'type': 'LAN Device'
                                })
                            except Exception as e:
                                pass
    except Exception as e:
        print(f"  ⚠ ARP 掃描錯誤: {e}")
    
    return devices

def detect_from_docker_logs():
    """從 Docker 日誌中檢測訪問的 IP"""
    accessed_ips = {}
    try:
        result = subprocess.run(
            ['docker', 'logs', '--tail', '500', 'wuchangv510-wuchang-web-1'],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        lines = result.stdout.split('\n')
        for line in lines:
            # 尋找 IP 地址模式
            import re
            ip_pattern = r'\b(?:192\.168\.|10\.|172\.(?:1[6-9]|2[0-9]|3[0-1])\.)\d{1,3}\.\d{1,3}\b'
            ips = re.findall(ip_pattern, line)
            
            for ip in ips:
                if ip not in accessed_ips:
                    accessed_ips[ip] = {
                        'first_seen': datetime.now().isoformat(),
                        'access_count': 0,
                        'type': 'Odoo Access'
                    }
                accessed_ips[ip]['access_count'] += 1
    except Exception as e:
        print(f"  ⚠ Docker 日誌掃描錯誤: {e}")
    
    return accessed_ips

def detect_active_connections():
    """檢測當前活躍的 TCP 連接"""
    active_conns = []
    try:
        if sys.platform == 'win32':
            result = subprocess.run(
                ['netstat', '-an'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            lines = result.stdout.split('\n')
            local_ip = get_local_ip()
            
            for line in lines:
                if 'ESTABLISHED' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        local_addr = parts[1]
                        remote_addr = parts[2] if len(parts) > 2 else None
                        
                        if remote_addr and (remote_addr.startswith('192.168.') or 
                                           remote_addr.startswith('10.') or 
                                           (remote_addr.startswith('172.') and 16 <= int(remote_addr.split('.')[1]) <= 31)):
                            if remote_addr not in [conn['ip'] for conn in active_conns]:
                                try:
                                    hostname = get_hostname(remote_addr.split(':')[0])
                                    active_conns.append({
                                        'ip': remote_addr.split(':')[0],
                                        'port': remote_addr.split(':')[1] if ':' in remote_addr else 'Unknown',
                                        'hostname': hostname,
                                        'type': 'Active Connection',
                                        'status': 'ESTABLISHED'
                                    })
                                except Exception:
                                    pass
    except Exception as e:
        print(f"  ⚠ 活躍連接掃描錯誤: {e}")
    
    return active_conns

def main():
    print("=" * 80)
    print("  偵測目前連入的個人電腦和網絡設備")
    print("=" * 80)
    print()
    
    local_ip = get_local_ip()
    print(f"本機 IP 地址: {local_ip}")
    print(f"網絡範圍: {local_ip.rsplit('.', 1)[0]}.0/24")
    print()
    
    # 1. 從 ARP 表獲取設備
    print("[1/3] 掃描 ARP 表（連接過的設備）...")
    arp_devices = detect_from_arp()
    print(f"  找到 {len(arp_devices)} 個設備")
    print()
    
    # 2. 檢測活躍連接
    print("[2/3] 檢測當前活躍連接...")
    active_conns = detect_active_connections()
    print(f"  找到 {len(active_conns)} 個活躍的本地連接")
    print()
    
    # 3. 從 Docker 日誌檢測訪問
    print("[3/3] 檢查 Odoo 訪問日誌...")
    accessed_ips = detect_from_docker_logs()
    print(f"  找到 {len(accessed_ips)} 個訪問 IP")
    print()
    
    # 合併結果
    all_devices = {}
    
    for device in arp_devices:
        ip = device['ip']
        if ip not in all_devices:
            all_devices[ip] = device
        else:
            all_devices[ip].update(device)
    
    for conn in active_conns:
        ip = conn['ip']
        if ip not in all_devices:
            all_devices[ip] = {
                'ip': ip,
                'hostname': conn.get('hostname', 'Unknown'),
                'type': conn.get('type', 'Unknown'),
                'active_connections': [conn]
            }
        else:
            if 'active_connections' not in all_devices[ip]:
                all_devices[ip]['active_connections'] = []
            all_devices[ip]['active_connections'].append(conn)
    
    for ip, info in accessed_ips.items():
        if ip not in all_devices:
            all_devices[ip] = {
                'ip': ip,
                'hostname': get_hostname(ip),
                'type': info.get('type', 'Unknown'),
                'access_count': info.get('access_count', 0),
                'first_seen': info.get('first_seen', 'Unknown')
            }
        else:
            all_devices[ip]['access_count'] = info.get('access_count', 0)
            all_devices[ip]['first_seen'] = info.get('first_seen', 'Unknown')
    
    # 排除本機 IP
    if local_ip in all_devices:
        del all_devices[local_ip]
    
    # 輸出結果
    print("=" * 80)
    print("  偵測結果")
    print("=" * 80)
    print()
    
    if not all_devices:
        print("  ⚠ 未發現其他連接的設備")
        return
    
    # 按 IP 排序
    sorted_devices = sorted(all_devices.items(), key=lambda x: socket.inet_aton(x[0]))
    
    for ip, info in sorted_devices:
        print(f"設備: {ip}")
        print(f"  主機名: {info.get('hostname', 'Unknown')}")
        if 'vendor' in info:
            print(f"  廠商: {info.get('vendor', 'Unknown')}")
        if 'mac' in info:
            print(f"  MAC 地址: {info.get('mac', 'Unknown')}")
        if 'open_ports' in info and info['open_ports']:
            print(f"  開放端口: {', '.join(info['open_ports'])}")
        if 'access_count' in info:
            print(f"  Odoo 訪問次數: {info.get('access_count', 0)}")
        if 'active_connections' in info:
            print(f"  活躍連接: {len(info['active_connections'])} 個")
        print(f"  類型: {info.get('type', 'Unknown')}")
        print()
    
    # 保存結果
    try:
        result_file = f'connected_devices_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'local_ip': local_ip,
                'devices': all_devices
            }, f, ensure_ascii=False, indent=2)
        print(f"✓ 結果已保存至: {result_file}")
    except Exception as e:
        print(f"⚠ 保存結果失敗: {e}")
    
    print()
    print("=" * 80)
    print("  偵測完成")
    print("=" * 80)

if __name__ == '__main__':
    main()
