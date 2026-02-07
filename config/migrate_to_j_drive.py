#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
migrate_to_j_drive.py

將本機非系統檔案遷移到 J 磁碟，C 磁碟留下符號連結

功能：
- 識別 C:\\wuchang V5.1.0 中的非系統檔案
- 遷移到 J 磁碟對應位置
- 在 C 磁碟創建符號連結
- 保持路徑兼容性
"""

from __future__ import annotations

import os
import sys
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

# C 磁碟源目錄
C_SOURCE = Path(r"C:\wuchang V5.1.0\wuchang-V5.1.0")

# J 磁碟目標目錄
J_TARGET = Path(r"J:\wuchang V5.1.0\wuchang-V5.1.0")

# 需要遷移的目錄（非系統檔案）
MIGRATE_DIRS = [
    "local_storage",
    "data",
    "uploads",
    "backups",
    "logs",
    "cache",
    "temp",
]

# 需要遷移的檔案模式
MIGRATE_FILE_PATTERNS = [
    "*.json",
    "*.log",
    "*.db",
    "*.sqlite",
    "*.sqlite3",
]

# 排除的目錄和檔案
EXCLUDE_PATTERNS = [
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "*.pyc",
    "*.pyo",
    "*.pyd",
]


def is_system_file(file_path: Path) -> bool:
    """判斷是否為系統檔案（不應遷移）"""
    # 系統檔案擴展名（不遷移）
    system_extensions = {".py", ".md", ".yml", ".yaml", ".txt", ".html", ".css", ".js", ".bat", ".ps1", ".sh"}
    if file_path.suffix.lower() in system_extensions:
        return True
    
    # 排除特定系統目錄
    for pattern in EXCLUDE_PATTERNS:
        if pattern in file_path.parts:
            return True
    
    return False


def should_migrate(path: Path, source_base: Path) -> bool:
    """判斷是否應該遷移（非系統檔案）"""
    # 檢查是否在排除列表中
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path.parts:
            return False
    
    # 如果是目錄，檢查是否在遷移列表中
    if path.is_dir():
        return path.name in MIGRATE_DIRS
    
    # 如果是檔案
    if path.is_file():
        # 排除系統檔案（Python 源碼、配置文件等）
        if is_system_file(path):
            return False
        
        # 檢查是否在需要遷移的目錄中（優先判斷）
        relative_path = path.relative_to(source_base)
        for migrate_dir in MIGRATE_DIRS:
            if migrate_dir in relative_path.parts:
                # 在遷移目錄中，且不是系統檔案
                return True
        
        # 檢查檔案模式（僅對根目錄的檔案）
        if len(relative_path.parts) == 1:  # 只在根目錄檢查模式
            for pattern in MIGRATE_FILE_PATTERNS:
                if path.match(pattern):
                    return True
    
    return False


def create_symlink(source: Path, target: Path) -> bool:
    """創建符號連結（Windows）"""
    try:
        # 確保目標目錄存在
        target.parent.mkdir(parents=True, exist_ok=True)
        
        # 如果目標已存在，先刪除
        if target.exists() or target.is_symlink():
            if target.is_symlink():
                target.unlink()
            elif target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        
        # 創建符號連結
        if source.is_dir():
            # 目錄符號連結
            os.symlink(source, target, target_is_directory=True)
        else:
            # 檔案符號連結
            os.symlink(source, target, target_is_directory=False)
        
        return True
    except OSError as e:
        if e.winerror == 1314:  # ERROR_PRIVILEGE_NOT_HELD
            print(f"  需要管理員權限創建符號連結: {target}")
            return False
        else:
            print(f"  創建符號連結失敗: {e}")
            return False
    except Exception as e:
        print(f"  創建符號連結失敗: {e}")
        return False


def migrate_file_or_dir(source: Path, target: Path, create_link: bool = True) -> Dict:
    """遷移檔案或目錄"""
    result = {
        "source": str(source),
        "target": str(target),
        "link": None,
        "success": False,
        "error": None,
    }
    
    try:
        # 確保目標父目錄存在
        target.parent.mkdir(parents=True, exist_ok=True)
        
        # 如果目標已存在，先備份
        if target.exists():
            backup_path = target.with_suffix(f"{target.suffix}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            if target.is_dir():
                shutil.move(str(target), str(backup_path))
            else:
                shutil.move(str(target), str(backup_path))
            print(f"  [備份] 已備份現有目標: {backup_path.name}")
        
        # 遷移檔案或目錄
        if source.is_dir():
            shutil.copytree(source, target, dirs_exist_ok=True)
        else:
            shutil.copy2(source, target)
        
        print(f"  [遷移] {source.name} -> {target}")
        
        # 刪除源檔案/目錄（遷移後）
        try:
            if source.is_dir():
                shutil.rmtree(source)
            else:
                source.unlink()
            print(f"  [刪除] 已刪除源檔案: {source.name}")
        except Exception as e:
            print(f"  [警告] 無法刪除源檔案: {e}")
        
        # 創建符號連結
        if create_link:
            link_path = source
            if create_symlink(target, link_path):
                result["link"] = str(link_path)
                print(f"  [連結] 已創建符號連結: {link_path} -> {target}")
            else:
                result["error"] = "symlink_failed"
                return result
        
        result["success"] = True
        return result
        
    except Exception as e:
        result["error"] = str(e)
        print(f"  [錯誤] 遷移失敗: {e}")
        return result


def scan_for_migration(source_dir: Path, target_base: Path) -> List[Dict]:
    """掃描需要遷移的檔案和目錄"""
    items_to_migrate = []
    
    if not source_dir.exists():
        return items_to_migrate
    
    # 遞迴掃描目錄
    for root, dirs, files in os.walk(source_dir):
        root_path = Path(root)
        
        # 過濾排除的目錄
        dirs[:] = [d for d in dirs if d not in [p for p in EXCLUDE_PATTERNS if not p.startswith("*")]]
        
        # 檢查目錄本身
        if root_path != source_dir:  # 跳過根目錄
            relative_path = root_path.relative_to(source_dir)
            if should_migrate(root_path, source_dir):
                target_path = target_base / relative_path
                total_size = sum(f.stat().st_size for f in root_path.rglob("*") if f.is_file())
                items_to_migrate.append({
                    "source": root_path,
                    "target": target_path,
                    "type": "directory",
                    "size": total_size,
                })
        
        # 檢查檔案
        for file in files:
            file_path = root_path / file
            if should_migrate(file_path, source_dir):
                relative_path = file_path.relative_to(source_dir)
                target_path = target_base / relative_path
                items_to_migrate.append({
                    "source": file_path,
                    "target": target_path,
                    "type": "file",
                    "size": file_path.stat().st_size,
                })
    
    return items_to_migrate


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="將本機非系統檔案遷移到 J 磁碟，C 磁碟留下符號連結")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="模擬模式，不實際執行遷移",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="執行實際遷移（需要明確指定）",
    )
    parser.add_argument(
        "--source",
        type=str,
        default=str(C_SOURCE),
        help="源目錄（預設: C:\\wuchang V5.1.0\\wuchang-V5.1.0）",
    )
    parser.add_argument(
        "--target",
        type=str,
        default=str(J_TARGET),
        help="目標目錄（預設: J:\\wuchang V5.1.0\\wuchang-V5.1.0）",
    )
    parser.add_argument(
        "--no-link",
        action="store_true",
        help="不創建符號連結（僅遷移）",
    )
    
    args = parser.parse_args()
    
    source_dir = Path(args.source)
    target_dir = Path(args.target)
    
    print("=" * 70)
    print("本機非系統檔案遷移到 J 磁碟")
    print("=" * 70)
    print()
    print(f"源目錄: {source_dir}")
    print(f"目標目錄: {target_dir}")
    print(f"模式: {'模擬模式' if args.dry_run else '實際遷移'}")
    print(f"創建符號連結: {'否' if args.no_link else '是'}")
    print()
    
    # 檢查源目錄
    if not source_dir.exists():
        print(f"錯誤: 源目錄不存在: {source_dir}", file=sys.stderr)
        return 1
    
    # 掃描需要遷移的項目
    print("正在掃描需要遷移的檔案和目錄...")
    items_to_migrate = scan_for_migration(source_dir, target_dir)
    
    if not items_to_migrate:
        print("沒有找到需要遷移的檔案或目錄")
        return 0
    
    print(f"找到 {len(items_to_migrate)} 個項目需要遷移")
    print()
    
    # 顯示遷移列表
    total_size = 0
    print("遷移列表：")
    for i, item in enumerate(items_to_migrate, 1):
        size_mb = item["size"] / (1024 * 1024)
        total_size += item["size"]
        print(f"  {i}. {item['source'].name} ({item['type']}, {size_mb:.2f} MB)")
    print()
    print(f"總大小: {total_size / (1024 * 1024 * 1024):.2f} GB")
    print()
    
    if args.dry_run:
        print("這是模擬模式，不會實際執行遷移。")
        print("使用 --execute 來執行實際遷移。")
        return 0
    
    # 需要明確指定 --execute
    if not args.execute:
        print("錯誤: 需要明確指定 --execute 來執行實際遷移", file=sys.stderr)
        print("這是為了安全考慮，避免意外遷移檔案", file=sys.stderr)
        return 1
    
    # 確認
    try:
        print("警告: 此操作將遷移檔案到 J 磁碟並在 C 磁碟創建符號連結")
        confirm = input("是否繼續遷移？(yes/N): ").strip().lower()
        if confirm != "yes":
            print("已取消")
            return 0
    except KeyboardInterrupt:
        print("\n已取消")
        return 0
    
    # 執行遷移
    print()
    print("=" * 70)
    print("開始遷移")
    print("=" * 70)
    print()
    
    results = []
    for item in items_to_migrate:
        print(f"遷移: {item['source'].name}")
        result = migrate_file_or_dir(
            item["source"],
            item["target"],
            create_link=not args.no_link,
        )
        results.append(result)
        print()
    
    # 顯示結果
    print("=" * 70)
    print("遷移結果")
    print("=" * 70)
    
    success_count = sum(1 for r in results if r["success"])
    failed_count = len(results) - success_count
    
    print(f"成功: {success_count} 個")
    if failed_count > 0:
        print(f"失敗: {failed_count} 個")
        print()
        print("失敗項目：")
        for r in results:
            if not r["success"]:
                print(f"  - {r['source']}: {r.get('error', 'unknown')}")
    
    print("=" * 70)
    
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
