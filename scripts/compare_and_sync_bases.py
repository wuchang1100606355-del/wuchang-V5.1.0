#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
兩基地端檔案比較與最優同步工具
比較兩個基地端的檔案差異並執行最優同步
"""

import os
import sys
import hashlib
import json
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import subprocess

PROJECT_ROOT = Path(__file__).parent.parent

def print_header(title):
    """打印標題"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)
    print()

def get_file_hash(file_path):
    """獲取檔案雜湊值"""
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        return None

def scan_directory(directory, ignore_patterns=None):
    """掃描目錄並返回檔案列表（相對路徑、大小、修改時間、雜湊）"""
    if ignore_patterns is None:
        ignore_patterns = [
            '.git', '__pycache__', '.pyc', 'node_modules',
            'volumes', 'backups', 'logs', '.env'
        ]
    
    directory = Path(directory)
    if not directory.exists():
        return {}
    
    files_info = {}
    
    for file_path in directory.rglob('*'):
        # 跳過忽略模式
        if any(pattern in str(file_path) for pattern in ignore_patterns):
            continue
        
        if file_path.is_file():
            try:
                rel_path = file_path.relative_to(directory)
                stat = file_path.stat()
                
                files_info[str(rel_path)] = {
                    'path': str(file_path),
                    'relative_path': str(rel_path),
                    'size': stat.st_size,
                    'mtime': stat.st_mtime,
                    'hash': get_file_hash(file_path)
                }
            except Exception as e:
                print(f"  ⚠️  掃描檔案失敗: {file_path} - {e}")
    
    return files_info

def compare_bases(base1_path, base2_path, base1_name="基地端1", base2_name="基地端2"):
    """比較兩個基地端的檔案"""
    print_header(f"比較 {base1_name} 和 {base2_name}")
    
    print(f"  [掃描] {base1_name}: {base1_path}")
    base1_files = scan_directory(base1_path)
    print(f"    找到 {len(base1_files)} 個檔案")
    
    print(f"  [掃描] {base2_name}: {base2_path}")
    base2_files = scan_directory(base2_path)
    print(f"    找到 {len(base2_files)} 個檔案")
    
    # 分析差異
    base1_only = set(base1_files.keys()) - set(base2_files.keys())
    base2_only = set(base2_files.keys()) - set(base1_files.keys())
    common = set(base1_files.keys()) & set(base2_files.keys())
    
    # 比較共同檔案的內容
    different = []
    identical = []
    
    for file_path in common:
        file1 = base1_files[file_path]
        file2 = base2_files[file_path]
        
        if file1['hash'] != file2['hash']:
            different.append({
                'path': file_path,
                'base1': file1,
                'base2': file2
            })
        else:
            identical.append(file_path)
    
    print()
    print(f"  [分析結果]")
    print(f"    相同檔案: {len(identical)} 個")
    print(f"    不同檔案: {len(different)} 個")
    print(f"    {base1_name} 獨有: {len(base1_only)} 個")
    print(f"    {base2_name} 獨有: {len(base2_only)} 個")
    
    comparison_result = {
        'base1_name': base1_name,
        'base2_name': base2_name,
        'base1_path': str(base1_path),
        'base2_path': str(base2_path),
        'base1_files': {k: {'size': v['size'], 'mtime': v['mtime'], 'hash': v['hash']} 
                        for k, v in base1_files.items()},
        'base2_files': {k: {'size': v['size'], 'mtime': v['mtime'], 'hash': v['hash']} 
                        for k, v in base2_files.items()},
        'identical': list(identical),
        'different': [
            {
                'path': d['path'],
                'base1_size': d['base1']['size'],
                'base1_mtime': d['base1']['mtime'],
                'base2_size': d['base2']['size'],
                'base2_mtime': d['base2']['mtime']
            }
            for d in different
        ],
        'base1_only': list(base1_only),
        'base2_only': list(base2_only),
        'timestamp': datetime.now().isoformat()
    }
    
    return comparison_result

def determine_best_version(file_path, base1_info, base2_info, strategy='newer'):
    """決定最佳版本（使用較新的檔案或較大的檔案）"""
    if strategy == 'newer':
        return 'base1' if base1_info['mtime'] > base2_info['mtime'] else 'base2'
    elif strategy == 'larger':
        return 'base1' if base1_info['size'] > base2_info['size'] else 'base2'
    else:
        return 'base1'  # 預設使用 base1

def sync_files(comparison_result, target_base, sync_strategy='newer', dry_run=False):
    """同步檔案到目標基地端"""
    print_header(f"同步檔案到 {target_base}")
    
    base1_path = Path(comparison_result['base1_path'])
    base2_path = Path(comparison_result['base2_path'])
    
    if target_base == 'base1':
        source_base = base2_path
        target_base_path = base1_path
        source_name = comparison_result['base2_name']
        target_name = comparison_result['base1_name']
    else:
        source_base = base1_path
        target_base_path = base2_path
        source_name = comparison_result['base1_name']
        target_name = comparison_result['base2_name']
    
    sync_operations = []
    
    # 同步不同的檔案
    for diff in comparison_result['different']:
        file_path = diff['path']
        
        if target_base == 'base1':
            base1_info = comparison_result['base1_files'].get(file_path)
            base2_info = comparison_result['base2_files'].get(file_path)
        else:
            base1_info = comparison_result['base1_files'].get(file_path)
            base2_info = comparison_result['base2_files'].get(file_path)
        
        best_version = determine_best_version(file_path, base1_info, base2_info, sync_strategy)
        
        if best_version != target_base:
            # 需要同步
            source_file = source_base / file_path
            target_file = target_base_path / file_path
            
            sync_operations.append({
                'type': 'update',
                'source': str(source_file),
                'target': str(target_file),
                'reason': f"使用 {source_name} 的版本（較新）"
            })
    
    # 同步獨有檔案
    if target_base == 'base1':
        only_files = comparison_result['base2_only']
        source_base_path = base2_path
    else:
        only_files = comparison_result['base1_only']
        source_base_path = base1_path
    
    for file_path in only_files:
        source_file = source_base_path / file_path
        target_file = target_base_path / file_path
        
        sync_operations.append({
            'type': 'copy',
            'source': str(source_file),
            'target': str(target_file),
            'reason': f"從 {source_name} 複製新檔案"
        })
    
    print(f"  [同步計劃]")
    print(f"    更新檔案: {len([op for op in sync_operations if op['type'] == 'update'])} 個")
    print(f"    複製檔案: {len([op for op in sync_operations if op['type'] == 'copy'])} 個")
    print(f"    總計: {len(sync_operations)} 個操作")
    print()
    
    if dry_run:
        print("  [預覽模式] 以下操作將被執行：")
        for i, op in enumerate(sync_operations[:10], 1):  # 只顯示前10個
            print(f"    {i}. {op['type']}: {op['target']}")
            print(f"       理由: {op['reason']}")
        if len(sync_operations) > 10:
            print(f"    ... 還有 {len(sync_operations) - 10} 個操作")
        return sync_operations
    
    # 執行同步
    print("  [執行同步]")
    success_count = 0
    error_count = 0
    
    for op in sync_operations:
        try:
            target_file = Path(op['target'])
            source_file = Path(op['source'])
            
            # 創建目標目錄
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 備份現有檔案
            if target_file.exists() and op['type'] == 'update':
                backup_file = target_file.with_suffix(target_file.suffix + '.backup')
                shutil.copy2(target_file, backup_file)
            
            # 複製檔案
            shutil.copy2(source_file, target_file)
            success_count += 1
            
        except Exception as e:
            print(f"    ❌ 同步失敗: {op['target']} - {e}")
            error_count += 1
    
    print()
    print(f"  ✅ 同步完成: 成功 {success_count} 個, 失敗 {error_count} 個")
    
    return {
        'operations': sync_operations,
        'success_count': success_count,
        'error_count': error_count
    }

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="兩基地端檔案比較與同步工具")
    parser.add_argument('--base1', type=str, required=True, help='基地端1路徑')
    parser.add_argument('--base2', type=str, required=True, help='基地端2路徑')
    parser.add_argument('--base1-name', type=str, default='基地端1', help='基地端1名稱')
    parser.add_argument('--base2-name', type=str, default='基地端2', help='基地端2名稱')
    parser.add_argument('--sync-to', type=str, choices=['base1', 'base2', 'bidirectional'], 
                       default='bidirectional', help='同步方向')
    parser.add_argument('--strategy', type=str, choices=['newer', 'larger'], 
                       default='newer', help='同步策略（newer=較新, larger=較大）')
    parser.add_argument('--dry-run', action='store_true', help='預覽模式，不實際執行')
    parser.add_argument('--output', type=str, help='輸出比較結果JSON檔案')
    
    args = parser.parse_args()
    
    print_header("兩基地端檔案比較與同步工具")
    print(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    base1_path = Path(args.base1)
    base2_path = Path(args.base2)
    
    if not base1_path.exists():
        print(f"❌ 基地端1不存在: {base1_path}")
        return 1
    
    if not base2_path.exists():
        print(f"❌ 基地端2不存在: {base2_path}")
        return 1
    
    # 步驟1: 比較
    comparison_result = compare_bases(
        base1_path, base2_path, 
        args.base1_name, args.base2_name
    )
    
    # 保存比較結果
    if args.output:
        output_file = Path(args.output)
    else:
        output_file = PROJECT_ROOT / "logs" / f"base_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comparison_result, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 比較結果已保存至: {output_file}\n")
    
    # 步驟2: 同步
    if args.sync_to == 'bidirectional':
        print("⚠️  雙向同步需要手動指定目標，請使用 --sync-to base1 或 --sync-to base2")
        return 0
    
    sync_result = sync_files(
        comparison_result, 
        args.sync_to, 
        args.strategy,
        args.dry_run
    )
    
    if args.dry_run:
        print("\n💡 這是預覽模式，未實際執行同步")
        print("   移除 --dry-run 參數以實際執行同步")
    else:
        print("\n✅ 同步完成")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
