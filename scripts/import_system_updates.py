#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系統更新檔案匯入工具
從 migration_pack 或其他指定目錄匯入更新檔案到系統
"""

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime

# 專案根目錄
PROJECT_ROOT = Path(__file__).parent.parent
MIGRATION_PACK_DIR = PROJECT_ROOT / "migration_pack"
WUCHANG_OS_DIR = PROJECT_ROOT / "wuchang_os"

# 更新檔案類型映射
UPDATE_FILE_PATTERNS = {
    # 模型檔案
    "models": {
        "source_pattern": "**/*.py",
        "target_dir": "wuchang_os/addons/*/models",
        "description": "模型檔案"
    },
    # 視圖檔案
    "views": {
        "source_pattern": "**/*.xml",
        "target_dir": "wuchang_os/addons/*/views",
        "description": "視圖檔案"
    },
    # 控制器檔案
    "controllers": {
        "source_pattern": "**/*.py",
        "target_dir": "wuchang_os/addons/*/controllers",
        "description": "控制器檔案"
    },
    # 數據檔案
    "data": {
        "source_pattern": "**/*.xml",
        "target_dir": "wuchang_os/addons/*/data",
        "description": "數據檔案"
    },
    # 配置文件
    "config": {
        "source_pattern": "**/*.conf",
        "target_dir": "wuchang_os",
        "description": "配置文件"
    },
    # Caddyfile
    "caddyfile": {
        "source_pattern": "**/Caddyfile",
        "target_dir": "wuchang_os",
        "description": "Caddy 配置文件"
    },
    # Manifest 檔案
    "manifest": {
        "source_pattern": "**/__manifest__.py",
        "target_dir": "wuchang_os/addons/*",
        "description": "模組清單檔案"
    }
}

def print_header():
    """打印標題"""
    print("=" * 80)
    print("  系統更新檔案匯入工具")
    print("=" * 80)
    print(f"  執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  專案根目錄: {PROJECT_ROOT}")
    print("=" * 80)
    print()

def find_update_files(source_dir):
    """找出所有更新檔案"""
    update_files = []
    
    if not source_dir.exists():
        print(f"❌ 源目錄不存在: {source_dir}")
        return update_files
    
    # 遍歷 migration_pack/wuchang_os/addons
    addons_source = source_dir / "wuchang_os" / "addons"
    if addons_source.exists():
        for addon_dir in addons_source.iterdir():
            if addon_dir.is_dir():
                addon_name = addon_dir.name
                target_addon_dir = WUCHANG_OS_DIR / "addons" / addon_name
                
                # 檢查各個子目錄
                for subdir in ["models", "views", "controllers", "data", "security"]:
                    source_subdir = addon_dir / subdir
                    target_subdir = target_addon_dir / subdir
                    
                    if source_subdir.exists():
                        for file_path in source_subdir.rglob("*"):
                            if file_path.is_file() and not file_path.name.startswith("__"):
                                update_files.append({
                                    "source": file_path,
                                    "target": target_subdir / file_path.relative_to(source_subdir),
                                    "type": subdir,
                                    "addon": addon_name
                                })
                
                # 檢查根目錄檔案 (__manifest__.py, __init__.py 等)
                for file_path in addon_dir.glob("*.py"):
                    if file_path.name in ["__manifest__.py", "__init__.py"]:
                        update_files.append({
                            "source": file_path,
                            "target": target_addon_dir / file_path.name,
                            "type": "root",
                            "addon": addon_name
                        })
    
    # 檢查 Caddyfile
    caddyfile_source = source_dir / "wuchang_os" / "Caddyfile"
    if caddyfile_source.exists():
        update_files.append({
            "source": caddyfile_source,
            "target": WUCHANG_OS_DIR / "Caddyfile",
            "type": "config",
            "addon": None
        })
    
    return update_files

def backup_file(file_path):
    """備份現有檔案"""
    if file_path.exists():
        backup_dir = PROJECT_ROOT / "backups" / "import_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / file_path.relative_to(PROJECT_ROOT)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        return backup_path
    return None

def import_file(file_info, dry_run=False, force=False):
    """匯入單個檔案"""
    source = file_info["source"]
    target = file_info["target"]
    
    # 確保目標目錄存在
    target.parent.mkdir(parents=True, exist_ok=True)
    
    # 檢查目標檔案是否存在
    if target.exists() and not force:
        # 比較檔案內容
        try:
            with open(source, 'rb') as f1, open(target, 'rb') as f2:
                if f1.read() == f2.read():
                    return {"status": "skipped", "reason": "檔案內容相同"}
        except Exception:
            pass
    
    # 獲取相對路徑（安全的）
    def get_relative_path(path, base):
        try:
            return str(path.relative_to(base))
        except ValueError:
            return str(path)
    
    if dry_run:
        backup_path = backup_file(target) if target.exists() else None
        return {
            "status": "would_import",
            "source": get_relative_path(source, PROJECT_ROOT),
            "target": get_relative_path(target, PROJECT_ROOT),
            "backup": get_relative_path(backup_path, PROJECT_ROOT) if backup_path else None
        }
    
    # 備份現有檔案
    backup_path = backup_file(target)
    
    try:
        # 複製檔案
        shutil.copy2(source, target)
        
        return {
            "status": "imported",
            "source": get_relative_path(source, PROJECT_ROOT),
            "target": get_relative_path(target, PROJECT_ROOT),
            "backup": get_relative_path(backup_path, PROJECT_ROOT) if backup_path else None
        }
    except Exception as e:
        return {
            "status": "error",
            "source": get_relative_path(source, PROJECT_ROOT),
            "target": get_relative_path(target, PROJECT_ROOT),
            "error": str(e)
        }

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="匯入系統更新檔案")
    parser.add_argument("--source", type=str, default=str(MIGRATION_PACK_DIR),
                       help="源目錄路徑 (預設: migration_pack)")
    parser.add_argument("--dry-run", action="store_true",
                       help="預覽模式，不實際匯入檔案")
    parser.add_argument("--force", action="store_true",
                       help="強制覆蓋現有檔案")
    parser.add_argument("--module", type=str,
                       help="只匯入指定模組")
    parser.add_argument("--type", type=str, choices=["models", "views", "controllers", "data", "config"],
                       help="只匯入指定類型的檔案")
    
    args = parser.parse_args()
    
    print_header()
    
    source_dir = Path(args.source)
    if not source_dir.exists():
        print(f"❌ 源目錄不存在: {source_dir}")
        return 1
    
    print(f"📂 掃描源目錄: {source_dir}")
    print()
    
    # 找出所有更新檔案
    update_files = find_update_files(source_dir)
    
    # 過濾
    if args.module:
        update_files = [f for f in update_files if f.get("addon") == args.module]
    
    if args.type:
        update_files = [f for f in update_files if f.get("type") == args.type]
    
    if not update_files:
        print("❌ 未找到任何更新檔案")
        return 1
    
    print(f"✅ 找到 {len(update_files)} 個更新檔案")
    print()
    
    # 按模組和類型分組顯示
    grouped = {}
    for file_info in update_files:
        addon = file_info.get("addon", "系統")
        file_type = file_info.get("type", "其他")
        key = f"{addon}/{file_type}"
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(file_info)
    
    print("📋 更新檔案清單:")
    for key, files in sorted(grouped.items()):
        print(f"  {key}: {len(files)} 個檔案")
    print()
    
    if args.dry_run:
        print("🔍 預覽模式 (Dry Run)")
        print()
    
    # 匯入檔案
    results = []
    for file_info in update_files:
        result = import_file(file_info, dry_run=args.dry_run, force=args.force)
        results.append({**result, **file_info})
    
    # 統計結果
    stats = {
        "imported": 0,
        "skipped": 0,
        "would_import": 0,
        "error": 0
    }
    
    for result in results:
        status = result["status"]
        if status == "imported":
            stats["imported"] += 1
        elif status == "skipped":
            stats["skipped"] += 1
        elif status == "would_import":
            stats["would_import"] += 1
        elif status == "error":
            stats["error"] += 1
    
    # 顯示結果
    print()
    print("=" * 80)
    print("  匯入結果")
    print("=" * 80)
    
    if args.dry_run:
        print(f"  將匯入: {stats['would_import']} 個檔案")
        print(f"  將跳過: {stats['skipped']} 個檔案")
    else:
        print(f"  已匯入: {stats['imported']} 個檔案")
        print(f"  已跳過: {stats['skipped']} 個檔案")
    
    if stats["error"] > 0:
        print(f"  錯誤: {stats['error']} 個檔案")
        print()
        print("  錯誤詳情:")
        for result in results:
            if result["status"] == "error":
                print(f"    ❌ {result['target']}: {result.get('error', 'Unknown error')}")
    
    print()
    
    # 保存結果到 JSON
    results_file = PROJECT_ROOT / "logs" / f"import_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 將結果轉換為可序列化的格式
    serializable_results = []
    for result in results:
        serializable_results.append({
            "status": result["status"],
            "source": str(result.get("source", "")),
            "target": str(result.get("target", "")),
            "type": result.get("type", ""),
            "addon": result.get("addon", ""),
            "backup": str(result.get("backup", "")) if result.get("backup") else None,
            "error": result.get("error"),
            "reason": result.get("reason")
        })
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "source_dir": str(source_dir),
            "dry_run": args.dry_run,
            "force": args.force,
            "stats": stats,
            "results": serializable_results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"📄 結果已保存至: {results_file}")
    print()
    
    if args.dry_run:
        print("💡 提示: 使用 --dry-run=false 或移除 --dry-run 參數以實際匯入檔案")
    else:
        print("✅ 匯入完成！")
        print()
        print("🚀 下一步:")
        print("  1. 檢查匯入的檔案")
        print("  2. 重啟 Odoo 服務")
        print("  3. 升級相關模組: docker exec <container> odoo -u <module_name> -d <database>")
    
    print()
    print("=" * 80)
    
    return 0 if stats["error"] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
