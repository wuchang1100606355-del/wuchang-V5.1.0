#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接讀取UI筆電地端檔案工具
支援多種訪問方式：網絡共享、SSH、本地路徑
"""

import os
import sys
import argparse
from pathlib import Path
import json
from datetime import datetime

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False
    print("⚠️  警告: paramiko未安裝，SSH功能將不可用")
    print("   安裝方式: pip install paramiko")

def test_network_share(path):
    """測試網絡共享路徑是否可訪問"""
    try:
        if os.path.exists(path):
            return True, None
        return False, "路徑不存在"
    except Exception as e:
        return False, str(e)

def list_files_ssh(host, port, username, password, remote_path):
    """使用SSH列出遠程檔案"""
    if not HAS_PARAMIKO:
        return None, "paramiko未安裝"
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port=port, username=username, password=password, timeout=10)
        
        # 列出檔案
        stdin, stdout, stderr = ssh.exec_command(f'powershell -Command "Get-ChildItem -Path \'{remote_path}\' -Recurse -ErrorAction SilentlyContinue | Select-Object FullName, Length, LastWriteTime | ConvertTo-Json"')
        
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        
        ssh.close()
        
        if error and 'error' in error.lower():
            return None, error
        
        try:
            files = json.loads(output)
            if not isinstance(files, list):
                files = [files]
            return files, None
        except:
            # 如果不是JSON，嘗試解析文本輸出
            return output, None
            
    except Exception as e:
        return None, str(e)

def list_files_network_share(share_path, max_depth=3, search_pattern=None):
    """列出網絡共享路徑的檔案"""
    files = []
    errors = []
    found_wuchang = False
    
    try:
        if not os.path.exists(share_path):
            return [], [f"路徑不存在: {share_path}"]
        
        # 如果指定了搜尋模式，先搜尋目錄
        if search_pattern:
            print(f"   🔍 搜尋包含 '{search_pattern}' 的目錄...")
            for root, dirs, filenames in os.walk(share_path):
                # 檢查目錄名稱
                for dir_name in dirs:
                    if search_pattern.lower() in dir_name.lower():
                        found_path = os.path.join(root, dir_name)
                        print(f"   ✅ 找到: {found_path}")
                        found_wuchang = True
                        # 從這個目錄開始掃描
                        share_path = found_path
                        break
                if found_wuchang:
                    break
        
        # 遍歷檔案
        count = 0
        for root, dirs, filenames in os.walk(share_path):
            depth = root.replace(share_path, '').count(os.sep)
            if depth >= max_depth:
                dirs[:] = []  # 不繼續深入
                continue
            
            for filename in filenames:
                try:
                    file_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(file_path, share_path)
                    stat = os.stat(file_path)
                    
                    files.append({
                        'path': rel_path,
                        'full_path': file_path,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                    count += 1
                    if count % 100 == 0:
                        print(f"   📁 已掃描 {count} 個檔案...", end='\r')
                except Exception as e:
                    errors.append(f"無法讀取 {file_path}: {e}")
        
        if count > 0:
            print(f"   📁 總共掃描 {count} 個檔案")
        
        return files, errors
        
    except Exception as e:
        return [], [str(e)]

def read_file_content(file_path, encoding='utf-8', max_size=10*1024*1024):
    """讀取檔案內容（限制大小）"""
    try:
        stat = os.stat(file_path)
        if stat.st_size > max_size:
            return None, f"檔案太大 ({stat.st_size} bytes)，超過限制 ({max_size} bytes)"
        
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            content = f.read()
        
        return content, None
        
    except Exception as e:
        return None, str(e)

def main():
    parser = argparse.ArgumentParser(description='直接讀取UI筆電地端檔案')
    parser.add_argument('--remote-path', type=str, help='遠程路徑（網絡共享或SSH路徑）')
    parser.add_argument('--ssh-host', type=str, default='192.168.50.84', help='SSH主機地址')
    parser.add_argument('--ssh-port', type=int, default=22, help='SSH端口')
    parser.add_argument('--ssh-user', type=str, help='SSH用戶名')
    parser.add_argument('--ssh-password', type=str, help='SSH密碼')
    parser.add_argument('--list-only', action='store_true', help='僅列出檔案，不讀取內容')
    parser.add_argument('--read-file', type=str, help='讀取指定檔案（相對路徑）')
    parser.add_argument('--output', type=str, help='輸出檔案路徑')
    parser.add_argument('--max-depth', type=int, default=3, help='最大深度')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("  直接讀取UI筆電地端檔案工具")
    print("=" * 80)
    print(f"\n執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 嘗試不同的訪問方式
    files = []
    errors = []
    
    # 方式1: 網絡共享
    if args.remote_path and os.path.exists(args.remote_path):
        print(f"📁 使用網絡共享訪問: {args.remote_path}")
        # 自動搜尋wuchang相關目錄
        files, errors = list_files_network_share(args.remote_path, args.max_depth, search_pattern='wuchang')
        print(f"   ✅ 找到 {len(files)} 個檔案")
        if errors:
            print(f"   ⚠️  有 {len(errors)} 個錯誤")
    
    # 方式2: SSH
    elif args.ssh_user and args.ssh_password:
        print(f"🔐 使用SSH訪問: {args.ssh_host}:{args.ssh_port}")
        result, error = list_files_ssh(
            args.ssh_host, 
            args.ssh_port, 
            args.ssh_user, 
            args.ssh_password,
            args.remote_path or 'C:\\wuchang V5.1.0'
        )
        if error:
            print(f"   ❌ SSH錯誤: {error}")
        else:
            print(f"   ✅ SSH連接成功")
            if isinstance(result, list):
                files = result
            else:
                print(f"   輸出: {result[:500]}...")
    
    # 方式3: 嘗試常見路徑
    else:
        print("🔍 嘗試自動偵測可訪問路徑...")
        common_paths = [
            "\\192.168.50.84\\Users",
            "\\192.168.50.84\\C$",
            "\\192.168.50.84\\D$",
            "\\192.168.50.84\\wuchang",
            "\\192.168.50.84\\wuchang V5.1.0",
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                print(f"   ✅ 找到可訪問路徑: {path}")
                files, errors = list_files_network_share(path, args.max_depth)
                print(f"     找到 {len(files)} 個檔案")
                break
    
    # 顯示檔案列表
    if files:
        print(f"\n📋 檔案列表（前20個）:")
        for i, file_info in enumerate(files[:20], 1):
            if isinstance(file_info, dict):
                path = file_info.get('path', file_info.get('FullName', '未知'))
                size = file_info.get('size', file_info.get('Length', 0))
                print(f"   {i}. {path} ({size} bytes)")
            else:
                print(f"   {i}. {file_info}")
        
        if len(files) > 20:
            print(f"   ... 還有 {len(files) - 20} 個檔案")
    
    # 讀取指定檔案
    if args.read_file and files:
        print(f"\n📖 讀取檔案: {args.read_file}")
        # 找到對應的檔案
        target_file = None
        for file_info in files:
            if isinstance(file_info, dict):
                path = file_info.get('path', file_info.get('FullName', ''))
                if args.read_file in path or path.endswith(args.read_file):
                    target_file = file_info.get('full_path', file_info.get('FullName', ''))
                    break
        
        if target_file and os.path.exists(target_file):
            content, error = read_file_content(target_file)
            if error:
                print(f"   ❌ 讀取失敗: {error}")
            else:
                print(f"   ✅ 讀取成功 ({len(content)} 字元)")
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"   💾 已儲存到: {args.output}")
                else:
                    print(f"\n   內容預覽（前500字元）:")
                    print("   " + "-" * 70)
                    print("   " + content[:500].replace('\n', '\n   '))
                    if len(content) > 500:
                        print("   ...")
        else:
            print(f"   ❌ 找不到檔案: {args.read_file}")
    
    # 輸出結果
    if args.output and not args.read_file:
        result = {
            'timestamp': datetime.now().isoformat(),
            'files': files,
            'errors': errors,
            'total_files': len(files)
        }
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 結果已儲存到: {args.output}")
    
    if errors:
        print(f"\n⚠️  錯誤列表:")
        for error in errors[:10]:
            print(f"   - {error}")
        if len(errors) > 10:
            print(f"   ... 還有 {len(errors) - 10} 個錯誤")
    
    print("\n" + "=" * 80)
    print("✅ 完成")
    print("=" * 80)

if __name__ == '__main__':
    main()
