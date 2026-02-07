#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI筆電連接測試工具
測試不同的連接方式是否可用
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False

def test_network_share(path):
    """測試網絡共享路徑"""
    print(f"📁 測試網絡共享: {path}")
    try:
        if os.path.exists(path):
            print(f"   ✅ 路徑可訪問")
            # 嘗試列出檔案
            try:
                items = list(os.listdir(path))[:5]
                print(f"   ✅ 可以列出檔案（前5個）:")
                for item in items:
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        print(f"      📁 {item}/")
                    else:
                        size = os.path.getsize(item_path)
                        print(f"      📄 {item} ({size} bytes)")
                return True, None
            except Exception as e:
                print(f"   ⚠️  可以訪問但無法列出檔案: {e}")
                return True, str(e)
        else:
            print(f"   ❌ 路徑不存在")
            return False, "路徑不存在"
    except Exception as e:
        print(f"   ❌ 訪問失敗: {e}")
        return False, str(e)

def test_ssh(host, port, username, password):
    """測試SSH連接"""
    if not HAS_PARAMIKO:
        print("   ❌ paramiko未安裝，無法測試SSH")
        print("      安裝方式: pip install paramiko")
        return False, "paramiko未安裝"
    
    print(f"🔐 測試SSH連接: {username}@{host}:{port}")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port=port, username=username, password=password, timeout=10)
        print(f"   ✅ SSH連接成功")
        
        # 測試執行命令
        stdin, stdout, stderr = ssh.exec_command('echo %USERPROFILE%')
        userprofile = stdout.read().decode('utf-8', errors='ignore').strip()
        if userprofile:
            print(f"   ✅ 用戶目錄: {userprofile}")
        
        ssh.close()
        return True, None
    except paramiko.AuthenticationException:
        print(f"   ❌ SSH認證失敗")
        return False, "認證失敗"
    except Exception as e:
        print(f"   ❌ SSH連接失敗: {e}")
        return False, str(e)

def test_path_access(path):
    """測試路徑訪問"""
    print(f"📂 測試路徑訪問: {path}")
    try:
        if os.path.exists(path):
            print(f"   ✅ 路徑存在")
            if os.path.isdir(path):
                print(f"   ✅ 是目錄")
                items = list(os.listdir(path))[:5]
                print(f"   ✅ 目錄內容（前5個）:")
                for item in items:
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        print(f"      📁 {item}/")
                    else:
                        size = os.path.getsize(item_path)
                        print(f"      📄 {item} ({size} bytes)")
            else:
                print(f"   ✅ 是檔案")
                size = os.path.getsize(path)
                print(f"   ✅ 檔案大小: {size} bytes")
            return True, None
        else:
            print(f"   ❌ 路徑不存在")
            return False, "路徑不存在"
    except Exception as e:
        print(f"   ❌ 訪問失敗: {e}")
        return False, str(e)

def main():
    parser = argparse.ArgumentParser(description='測試UI筆電連接')
    parser.add_argument('--method', type=str, choices=['share', 'ssh', 'path'], required=True, help='測試方式')
    parser.add_argument('--path', type=str, help='路徑（用於share或path方式）')
    parser.add_argument('--host', type=str, default='192.168.50.84', help='SSH主機（用於ssh方式）')
    parser.add_argument('--port', type=int, default=22, help='SSH端口（用於ssh方式）')
    parser.add_argument('--user', type=str, help='SSH用戶名（用於ssh方式）')
    parser.add_argument('--password', type=str, help='SSH密碼（用於ssh方式）')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("  UI筆電連接測試工具")
    print("=" * 80)
    print(f"\n執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    success = False
    error = None
    
    if args.method == 'share':
        if not args.path:
            print("❌ 錯誤: --path 參數是必需的（用於share方式）")
            sys.exit(1)
        success, error = test_network_share(args.path)
    
    elif args.method == 'ssh':
        if not args.user or not args.password:
            print("❌ 錯誤: --user 和 --password 參數是必需的（用於ssh方式）")
            sys.exit(1)
        success, error = test_ssh(args.host, args.port, args.user, args.password)
    
    elif args.method == 'path':
        if not args.path:
            print("❌ 錯誤: --path 參數是必需的（用於path方式）")
            sys.exit(1)
        success, error = test_path_access(args.path)
    
    print("\n" + "=" * 80)
    if success:
        print("✅ 測試成功！連接可用")
        print("=" * 80)
        print("\n💡 下一步:")
        if args.method == 'share':
            print(f"   使用以下命令讀取檔案:")
            print(f"   python scripts/read_ui_laptop_files.py --remote-path \"{args.path}\" --list-only")
        elif args.method == 'ssh':
            print(f"   使用以下命令讀取檔案:")
            print(f"   python scripts/read_ui_laptop_files.py --ssh-host \"{args.host}\" --ssh-user \"{args.user}\" --ssh-password \"{args.password}\" --remote-path \"C:\\wuchang V5.1.0\" --list-only")
        elif args.method == 'path':
            print(f"   使用以下命令讀取檔案:")
            print(f"   python scripts/read_ui_laptop_files.py --remote-path \"{args.path}\" --list-only")
    else:
        print("❌ 測試失敗")
        if error:
            print(f"   錯誤: {error}")
        print("=" * 80)
        print("\n💡 建議:")
        print("   1. 檢查網絡連接")
        print("   2. 確認路徑正確")
        print("   3. 檢查權限設置")
        print("   4. 查看配置指南: UI筆電管線配置指南.md")
        sys.exit(1)

if __name__ == '__main__':
    main()
