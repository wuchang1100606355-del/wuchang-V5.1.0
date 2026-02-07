#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI筆電檔案同步工具
在區網上偵測UI筆電並進行檔案比較與同步
"""

import os
import sys
import json
import socket
import subprocess
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent

def print_header(title):
    """打印標題"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)
    print()

def detect_ui_laptops():
    """偵測區網中的UI筆電"""
    print_header("偵測區網中的UI筆電")
    
    # 查找最近的設備記錄
    logs_dir = PROJECT_ROOT / "logs"
    device_files = list(logs_dir.glob("connected_devices_*.json"))
    
    if not device_files:
        print("  ❌ 未找到設備記錄，請先執行設備偵測")
        return None
    
    # 使用最新的記錄
    latest_file = max(device_files, key=lambda p: p.stat().st_mtime)
    print(f"  [使用記錄] {latest_file.name}")
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            devices = json.load(f)
        
        # 尋找UI筆電（MSI、Laptop等關鍵字）
        ui_laptops = []
        for device in devices:
            hostname = device.get('hostname', '').lower()
            ip = device.get('ip', '')
            device_type = device.get('type', '')
            
            # 判斷是否為UI筆電
            is_ui_laptop = (
                'msi' in hostname or
                'laptop' in hostname or
                (device_type and 'active' in device_type.lower()) or
                ip.startswith('192.168.50.8')
            )
            
            if is_ui_laptop:
                ui_laptops.append(device)
        
        if ui_laptops:
            print(f"  ✅ 找到 {len(ui_laptops)} 個UI筆電設備：")
            for laptop in ui_laptops:
                print(f"    - {laptop.get('hostname', 'Unknown')} ({laptop.get('ip', 'Unknown')})")
            return ui_laptops
        else:
            print("  ⚠️  未找到UI筆電設備")
            return None
    
    except Exception as e:
        print(f"  ❌ 讀取設備記錄失敗: {e}")
        return None

def check_network_connectivity(ip):
    """檢查網絡連接性"""
    try:
        socket.gethostbyname(ip)
        return True
    except Exception:
        return False

def check_network_share(ip, share_name='wuchang'):
    """檢查網絡共享"""
    # 嘗試訪問網絡共享
    share_path = f"\\\\{ip}\\{share_name}"
    
    try:
        if os.path.exists(share_path):
            return share_path
        else:
            # 嘗試常見的共享名稱
            for common_share in ['C$', 'Users', 'wuchang', 'share']:
                test_path = f"\\\\{ip}\\{common_share}"
                if os.path.exists(test_path):
                    return test_path
    except Exception:
        pass
    
    return None

def get_base_paths():
    """獲取兩個基地端的路徑"""
    base1_path = PROJECT_ROOT  # 當前系統
    base2_path = None
    
    # 尋找可能的遠端路徑
    # 1. 檢查是否有配置檔案
    config_file = PROJECT_ROOT / "config" / "sync_config.json"
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                base2_path = config.get('remote_base_path')
        except Exception:
            pass
    
    # 2. 檢查常見的共享路徑
    if not base2_path:
        common_paths = [
            r"\\192.168.50.88\wuchang",
            r"\\192.168.50.84\wuchang",
            r"\\192.168.50.1\wuchang",
        ]
        for path in common_paths:
            if os.path.exists(path):
                base2_path = Path(path)
                break
    
    return base1_path, base2_path

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="UI筆電檔案同步工具")
    parser.add_argument('--remote-ip', type=str, help='遠端IP地址')
    parser.add_argument('--remote-path', type=str, help='遠端路徑（網絡共享或本地路徑）')
    parser.add_argument('--sync-strategy', type=str, choices=['newer', 'larger'], 
                       default='newer', help='同步策略')
    parser.add_argument('--dry-run', action='store_true', help='預覽模式')
    
    args = parser.parse_args()
    
    print_header("UI筆電檔案同步工具")
    print(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 步驟1: 偵測UI筆電
    ui_laptops = detect_ui_laptops()
    
    # 步驟2: 確定遠端路徑
    base1_path, base2_path = get_base_paths()
    
    if args.remote_path:
        base2_path = Path(args.remote_path)
    elif args.remote_ip:
        # 嘗試訪問網絡共享
        share_path = check_network_share(args.remote_ip)
        if share_path:
            base2_path = Path(share_path)
        else:
            print(f"  ⚠️  無法訪問 {args.remote_ip} 的網絡共享")
            print("     請使用 --remote-path 指定路徑")
            return 1
    
    if not base2_path:
        print("  ❌ 未找到遠端基地端路徑")
        print("     請使用 --remote-path 指定路徑")
        print("     例如: python scripts/sync_with_ui_laptop.py --remote-path \\\\192.168.50.88\\wuchang")
        return 1
    
    if not base2_path.exists():
        print(f"  ❌ 遠端路徑不存在: {base2_path}")
        return 1
    
    print(f"  [基地端1] 本地: {base1_path}")
    print(f"  [基地端2] 遠端: {base2_path}")
    print()
    
    # 步驟3: 執行比較和同步
    print("  [執行] 檔案比較與同步...")
    
    compare_script = PROJECT_ROOT / "scripts" / "compare_and_sync_bases.py"
    
    cmd = [
        sys.executable,
        str(compare_script),
        "--base1", str(base1_path),
        "--base2", str(base2_path),
        "--base1-name", "本地基地端",
        "--base2-name", "UI筆電基地端",
        "--sync-to", "base1",  # 同步到本地
        "--strategy", args.sync_strategy
    ]
    
    if args.dry_run:
        cmd.append("--dry-run")
    
    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode
    except Exception as e:
        print(f"  ❌ 執行失敗: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
