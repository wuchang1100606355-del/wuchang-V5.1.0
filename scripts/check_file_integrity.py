#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wuchang OS 地端檔案完整性檢查
檢查所有關鍵檔案和目錄是否完整
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# 核心目錄結構
REQUIRED_DIRS = [
    'wuchang_os',
    'wuchang_os/addons',
    'config',
    'scripts',
    'docs',
    'memory_store',
    'tools',
    'logs',
]

# 核心 Odoo 模組
REQUIRED_MODULES = [
    'wuchang_core',
    'wuchang_finance',
    'wuchang_business',
    'wuchang_volunteer',
    'wuchang_web_portal',
    'wuchang_community_campaign',
    'wuchang_design_system',
    'wuchang_ui_compliance',
    'wuchang_property_toolkits',
    'wuchang_award_coach',
    'wuchang_guardian',
    'wuchang_life',
]

# 關鍵文件
REQUIRED_FILES = [
    'README_V5.1.0.md',
    'docker-compose.yml',
    'docker-compose-ai.yml',
    'requirements.txt',
    'package.json',
    'config/odoo.conf',
    'config/official_ai_identity.json',
]

# 關鍵腳本
REQUIRED_SCRIPTS = [
    'scripts/install_wuchang_modules_v2.py',
    'scripts/ai_wake_up.py',
    'scripts/test_local_llm_performance.py',
    'scripts/compare_llm_performance.py',
]

def check_directory(base_path, dir_path):
    """檢查目錄是否存在"""
    full_path = Path(base_path) / dir_path
    exists = full_path.exists() and full_path.is_dir()
    return exists, str(full_path)

def check_file(base_path, file_path):
    """檢查文件是否存在"""
    full_path = Path(base_path) / file_path
    exists = full_path.exists() and full_path.is_file()
    size = full_path.stat().st_size if exists else 0
    return exists, str(full_path), size

def check_module(base_path, module_name):
    """檢查 Odoo 模組是否完整"""
    module_path = Path(base_path) / 'wuchang_os' / 'addons' / module_name
    if not module_path.exists():
        return False, str(module_path), []
    
    required_files = ['__manifest__.py', '__init__.py']
    missing_files = []
    
    for req_file in required_files:
        if not (module_path / req_file).exists():
            missing_files.append(req_file)
    
    return len(missing_files) == 0, str(module_path), missing_files

def print_header():
    """打印標題"""
    print("=" * 80)
    print("  Wuchang OS - 地端檔案完整性檢查")
    print("=" * 80)
    print()

def main():
    """主函數"""
    print_header()
    
    base_path = Path(__file__).parent.parent
    print(f"檢查路徑: {base_path}")
    print(f"檢查時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {
        'directories': [],
        'files': [],
        'modules': [],
        'scripts': []
    }
    
    # 檢查目錄
    print("[1/4] 檢查核心目錄結構...")
    print("-" * 80)
    for dir_path in REQUIRED_DIRS:
        exists, full_path = check_directory(base_path, dir_path)
        status = "✓" if exists else "✗"
        results['directories'].append({
            'path': dir_path,
            'exists': exists,
            'full_path': full_path
        })
        print(f"  {status} {dir_path}")
        if not exists:
            print(f"    路徑: {full_path} (不存在)")
    print()
    
    # 檢查文件
    print("[2/4] 檢查關鍵文件...")
    print("-" * 80)
    for file_path in REQUIRED_FILES:
        exists, full_path, size = check_file(base_path, file_path)
        status = "✓" if exists else "✗"
        size_str = f"({size:,} bytes)" if exists else "(不存在)"
        results['files'].append({
            'path': file_path,
            'exists': exists,
            'full_path': full_path,
            'size': size
        })
        print(f"  {status} {file_path} {size_str}")
    print()
    
    # 檢查模組
    print("[3/4] 檢查 Odoo 模組完整性...")
    print("-" * 80)
    for module_name in REQUIRED_MODULES:
        complete, full_path, missing = check_module(base_path, module_name)
        status = "✓" if complete else "✗"
        results['modules'].append({
            'name': module_name,
            'complete': complete,
            'path': full_path,
            'missing_files': missing
        })
        if complete:
            print(f"  {status} {module_name}")
        else:
            print(f"  {status} {module_name} (缺少: {', '.join(missing)})")
    print()
    
    # 檢查腳本
    print("[4/4] 檢查關鍵腳本...")
    print("-" * 80)
    for script_path in REQUIRED_SCRIPTS:
        exists, full_path, size = check_file(base_path, script_path)
        status = "✓" if exists else "✗"
        size_str = f"({size:,} bytes)" if exists else "(不存在)"
        results['scripts'].append({
            'path': script_path,
            'exists': exists,
            'full_path': full_path,
            'size': size
        })
        print(f"  {status} {script_path} {size_str}")
    print()
    
    # 統計結果
    print("=" * 80)
    print("檢查結果統計")
    print("=" * 80)
    
    dir_count = sum(1 for d in results['directories'] if d['exists'])
    file_count = sum(1 for f in results['files'] if f['exists'])
    module_count = sum(1 for m in results['modules'] if m['complete'])
    script_count = sum(1 for s in results['scripts'] if s['exists'])
    
    print(f"目錄: {dir_count}/{len(REQUIRED_DIRS)} 存在")
    print(f"文件: {file_count}/{len(REQUIRED_FILES)} 存在")
    print(f"模組: {module_count}/{len(REQUIRED_MODULES)} 完整")
    print(f"腳本: {script_count}/{len(REQUIRED_SCRIPTS)} 存在")
    print()
    
    # 完整性百分比
    total_items = len(REQUIRED_DIRS) + len(REQUIRED_FILES) + len(REQUIRED_MODULES) + len(REQUIRED_SCRIPTS)
    complete_items = dir_count + file_count + module_count + script_count
    completeness = (complete_items / total_items * 100) if total_items > 0 else 0
    
    print(f"總體完整性: {complete_items}/{total_items} ({completeness:.1f}%)")
    print()
    
    # 缺失項目
    missing_items = []
    
    for d in results['directories']:
        if not d['exists']:
            missing_items.append(f"目錄: {d['path']}")
    
    for f in results['files']:
        if not f['exists']:
            missing_items.append(f"文件: {f['path']}")
    
    for m in results['modules']:
        if not m['complete']:
            missing_items.append(f"模組: {m['name']} (缺少: {', '.join(m['missing_files'])})")
    
    for s in results['scripts']:
        if not s['exists']:
            missing_items.append(f"腳本: {s['path']}")
    
    if missing_items:
        print("=" * 80)
        print("缺失項目:")
        print("=" * 80)
        for item in missing_items:
            print(f"  ✗ {item}")
        print()
    else:
        print("=" * 80)
        print("✓ 所有關鍵檔案和目錄完整！")
        print("=" * 80)
        print()
    
    # 保存報告
    try:
        report_file = base_path / 'logs' / f'file_integrity_check_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        report = {
            'timestamp': datetime.now().isoformat(),
            'base_path': str(base_path),
            'completeness_percentage': completeness,
            'results': results,
            'summary': {
                'directories': {'found': dir_count, 'total': len(REQUIRED_DIRS)},
                'files': {'found': file_count, 'total': len(REQUIRED_FILES)},
                'modules': {'complete': module_count, 'total': len(REQUIRED_MODULES)},
                'scripts': {'found': script_count, 'total': len(REQUIRED_SCRIPTS)}
            },
            'missing_items': missing_items
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 檢查報告已保存至: {report_file}")
    except Exception as e:
        print(f"⚠ 保存報告失敗: {e}")
    
    return 0 if completeness >= 90 else 1

if __name__ == '__main__':
    sys.exit(main())
