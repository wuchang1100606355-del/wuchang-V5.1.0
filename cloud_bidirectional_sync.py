#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cloud_bidirectional_sync.py

五常雲端空間雙向同步工具

功能：
- 從雲端下載變更到本機（雲端 -> 本機）
- 從本機上傳變更到雲端（本機 -> 雲端）
- 支援選擇性同步（下載/上傳/雙向）
- 支援僅下載模式（非鏡像：只下載變更，不覆蓋本機較新檔案）
- 支援雙向增量模式（互相增加變更，不覆蓋任何一方較新檔案）

僅下載模式（--download-only）：
- 只下載雲端新增或更新的檔案
- 不覆蓋本機較新的檔案
- 不刪除本機多餘的檔案
- 非鏡像同步，保留本機所有檔案

僅上傳模式（--upload-only）：
- 只上傳本機新增或更新的檔案
- 不覆蓋雲端較新的檔案
- 不刪除雲端多餘的檔案
- 非鏡像同步，保留雲端所有檔案

雙向增量模式（--incremental-both）：
- 互相增加變更：下載雲端新增/更新，上傳本機新增/更新
- 不覆蓋較新檔案：保留任何一方較新的版本
- 非鏡像同步：不會讓任何一方完全鏡像另一方
"""

from __future__ import annotations

import os
import sys
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

try:
    from cloud_sync_config import (
        ensure_wuchang_cloud_path,
        get_sync_directories,
        validate_cloud_path,
    )
except ImportError:
    print("錯誤: 無法導入 cloud_sync_config 模組", file=sys.stderr)
    sys.exit(1)

BASE_DIR = Path(__file__).resolve().parent


def get_file_info(path: Path) -> Optional[Dict]:
    """獲取檔案資訊"""
    try:
        if not path.exists():
            return None
        
        stat = path.stat()
        return {
            "path": str(path),
            "name": path.name,
            "exists": True,
            "size": stat.st_size,
            "mtime": stat.st_mtime,
            "mtime_iso": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        }
    except Exception as e:
        return {
            "path": str(path),
            "exists": False,
            "error": str(e),
        }


def should_skip_file(file_path: Path) -> bool:
    """檢查是否應該跳過此檔案"""
    # 排除 .git、.venv、__pycache__、node_modules 等目錄
    skip_dirs = ['.git', '.venv', '__pycache__', 'node_modules', '.idea', '.vscode']
    for part in file_path.parts:
        if part in skip_dirs:
            return True
    # 排除特定檔案類型
    skip_extensions = ['.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe']
    if file_path.suffix.lower() in skip_extensions:
        return True
    return False


def compare_files(
    local_path: Path, 
    cloud_path: Path, 
    download_only: bool = False, 
    upload_only: bool = False,
    incremental_both: bool = False,  # 雙向增量模式（互相增加變更，不覆蓋）
) -> Dict:
    """
    比較本機和雲端檔案
    
    參數：
        local_path: 本機檔案路徑
        cloud_path: 雲端檔案路徑
        download_only: 是否僅下載模式（非鏡像，不覆蓋本機較新檔案）
        upload_only: 是否僅上傳模式（非鏡像，不覆蓋雲端較新檔案）
        incremental_both: 雙向增量模式（互相增加變更，不覆蓋任何一方較新的檔案）
    """
    local_info = get_file_info(local_path)
    cloud_info = get_file_info(cloud_path)
    
    result = {
        "filename": local_path.name if local_path else cloud_path.name,
        "local": local_info,
        "cloud": cloud_info,
        "action": None,
    }
    
    # 決定需要執行的動作
    if not local_info or not local_info.get("exists"):
        # 本機不存在
        if upload_only:
            # 僅上傳模式：不處理雲端多餘的檔案
            result["action"] = "skip"
        else:
            # 需要下載（新增檔案）
            result["action"] = "download"
    elif not cloud_info or not cloud_info.get("exists"):
        # 雲端不存在
        if download_only:
            # 僅下載模式：不處理本機多餘的檔案
            result["action"] = "skip"
        else:
            # 需要上傳（新增檔案）
            result["action"] = "upload"
    else:
        # 兩邊都存在，比較修改時間
        local_mtime = local_info.get("mtime", 0)
        cloud_mtime = cloud_info.get("mtime", 0)
        
        if incremental_both:
            # 雙向增量模式：只增加變更，不覆蓋較新檔案
            if cloud_mtime > local_mtime:
                # 雲端較新，下載（增加變更）
                result["action"] = "download"
            elif local_mtime > cloud_mtime:
                # 本機較新，上傳（增加變更）
                result["action"] = "upload"
            else:
                # 時間相同，無需同步
                result["action"] = "skip"
        elif cloud_mtime > local_mtime:
            # 雲端較新
            if upload_only:
                # 僅上傳模式：不覆蓋雲端較新的檔案
                result["action"] = "skip"
            else:
                # 需要下載
                result["action"] = "download"
        elif local_mtime > cloud_mtime:
            # 本機較新
            if download_only:
                # 僅下載模式：不覆蓋本機較新的檔案
                result["action"] = "skip"
            else:
                # 需要上傳
                result["action"] = "upload"
        else:
            # 時間相同，無需同步
            result["action"] = "skip"
    
    return result


def download_from_cloud(cloud_path: Path, local_path: Path, backup: bool = True) -> bool:
    """
    從雲端下載檔案到本機
    
    參數：
        cloud_path: 雲端檔案路徑
        local_path: 本機目標路徑
        backup: 是否備份現有本機檔案
    """
    if not cloud_path.exists():
        print(f"⚠️  雲端檔案不存在: {cloud_path}")
        return False
    
    try:
        # 如果本機檔案存在且需要備份
        if local_path.exists() and backup:
            backup_path = local_path.with_suffix(f"{local_path.suffix}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            shutil.copy2(local_path, backup_path)
            print(f"  [備份] 已備份本機檔案: {backup_path.name}")
        
        # 確保目標目錄存在
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 使用臨時檔案確保原子性
        with tempfile.NamedTemporaryFile(delete=False, dir=str(local_path.parent), prefix=local_path.name + ".", suffix=".tmp") as tf:
            tmp_path = Path(tf.name)
        
        try:
            shutil.copy2(cloud_path, tmp_path)
            os.replace(str(tmp_path), str(local_path))  # 原子替換
            print(f"  [下載] {cloud_path.name} -> {local_path}")
            return True
        finally:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except:
                    pass
    except Exception as e:
        print(f"  [錯誤] 下載失敗: {e}")
        return False


def upload_to_cloud(local_path: Path, cloud_path: Path) -> bool:
    """
    從本機上傳檔案到雲端
    
    參數：
        local_path: 本機檔案路徑
        cloud_path: 雲端目標路徑
    """
    if not local_path.exists():
        print(f"⚠️  本機檔案不存在: {local_path}")
        return False
    
    # 驗證雲端路徑
    if not validate_cloud_path(cloud_path):
        print(f"⚠️  警告: 目標路徑不在五常雲端空間內: {cloud_path}")
    
    try:
        # 確保目標目錄存在
        cloud_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 使用臨時檔案確保原子性
        with tempfile.NamedTemporaryFile(delete=False, dir=str(cloud_path.parent), prefix=cloud_path.name + ".", suffix=".tmp") as tf:
            tmp_path = Path(tf.name)
        
        try:
            shutil.copy2(local_path, tmp_path)
            os.replace(str(tmp_path), str(cloud_path))  # 原子替換
            print(f"  [上傳] {local_path.name} -> {cloud_path}")
            return True
        finally:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except:
                    pass
    except Exception as e:
        print(f"  [錯誤] 上傳失敗: {e}")
        return False


def sync_directory(
    local_dir: Path,
    cloud_dir: Path,
    direction: str = "both",  # "download", "upload", "both"
    pattern: str = "*",
    recursive: bool = True,
    download_only: bool = False,  # 僅下載模式（非鏡像）
    upload_only: bool = False,  # 僅上傳模式（非鏡像）
    incremental_both: bool = False,  # 雙向增量模式（互相增加變更，不覆蓋）
) -> Dict:
    """
    同步目錄
    
    參數：
        local_dir: 本機目錄
        cloud_dir: 雲端目錄
        direction: 同步方向 ("download", "upload", "both")
        pattern: 檔案模式（例如 "*.json", "*.md"）
        recursive: 是否遞迴同步子目錄
    """
    results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "local_dir": str(local_dir),
        "cloud_dir": str(cloud_dir),
        "direction": direction,
        "downloaded": [],
        "uploaded": [],
        "skipped": [],
        "errors": [],
    }
    
    # 確保目錄存在
    local_dir.mkdir(parents=True, exist_ok=True)
    cloud_dir.mkdir(parents=True, exist_ok=True)
    
    # 收集要同步的檔案
    files_to_sync = []
    
    if download_only:
        # 僅下載模式：只收集雲端存在的檔案
        if recursive:
            # 遞迴收集雲端檔案
            for root, dirs, files in os.walk(cloud_dir):
                root_path = Path(root)
                for file in files:
                    if pattern == "*" or file.endswith(pattern.replace("*", "")):
                        cloud_file = root_path / file
                        # 計算相對路徑
                        rel_path = cloud_file.relative_to(cloud_dir)
                        local_file = local_dir / rel_path
                        files_to_sync.append((local_file, cloud_file))
        else:
            # 只同步頂層雲端檔案
            for file in cloud_dir.glob(pattern):
                if file.is_file():
                    local_file = local_dir / file.name
                    files_to_sync.append((local_file, file))
    elif upload_only:
        # 僅上傳模式：只收集本機存在的檔案
        if recursive:
            # 遞迴收集本機檔案
            for root, dirs, files in os.walk(local_dir):
                # 排除 .git 和 .venv 目錄
                dirs[:] = [d for d in dirs if d not in ['.git', '.venv', '__pycache__', 'node_modules']]
                root_path = Path(root)
                # 跳過 .git 和 .venv 目錄
                if '.git' in root_path.parts or '.venv' in root_path.parts or '__pycache__' in root_path.parts or 'node_modules' in root_path.parts:
                    continue
                for file in files:
                    if pattern == "*" or file.endswith(pattern.replace("*", "")):
                        local_file = root_path / file
                        # 計算相對路徑
                        rel_path = local_file.relative_to(local_dir)
                        cloud_file = cloud_dir / rel_path
                        files_to_sync.append((local_file, cloud_file))
        else:
            # 只同步頂層本機檔案
            for file in local_dir.glob(pattern):
                if file.is_file():
                    cloud_file = cloud_dir / file.name
                    files_to_sync.append((file, cloud_file))
    else:
        # 雙向模式：收集兩邊的檔案
        if recursive:
            # 遞迴收集檔案
            for root, dirs, files in os.walk(cloud_dir):
                root_path = Path(root)
                for file in files:
                    if pattern == "*" or file.endswith(pattern.replace("*", "")):
                        cloud_file = root_path / file
                        # 計算相對路徑
                        rel_path = cloud_file.relative_to(cloud_dir)
                        local_file = local_dir / rel_path
                        files_to_sync.append((local_file, cloud_file))
            
            # 也檢查本機檔案
            for root, dirs, files in os.walk(local_dir):
                root_path = Path(root)
                for file in files:
                    if pattern == "*" or file.endswith(pattern.replace("*", "")):
                        local_file = root_path / file
                        rel_path = local_file.relative_to(local_dir)
                        cloud_file = cloud_dir / rel_path
                        if (local_file, cloud_file) not in files_to_sync:
                            files_to_sync.append((local_file, cloud_file))
        else:
            # 只同步頂層檔案
            for file in cloud_dir.glob(pattern):
                if file.is_file():
                    local_file = local_dir / file.name
                    files_to_sync.append((local_file, file))
            
            for file in local_dir.glob(pattern):
                if file.is_file():
                    cloud_file = cloud_dir / file.name
                    if (file, cloud_file) not in files_to_sync:
                        files_to_sync.append((file, cloud_file))
    
    # 同步每個檔案
    for local_file, cloud_file in files_to_sync:
        # 跳過不需要同步的檔案
        if should_skip_file(local_file):
            results["skipped"].append(f"{local_file.name} (已排除)")
            continue
        
        comparison = compare_files(
            local_file, 
            cloud_file, 
            download_only=download_only, 
            upload_only=upload_only,
            incremental_both=incremental_both,
        )
        action = comparison["action"]
        
        if action == "download" and direction in ("download", "both") and not upload_only:
            if download_from_cloud(cloud_file, local_file):
                results["downloaded"].append(comparison["filename"])
            else:
                results["errors"].append(f"下載失敗: {comparison['filename']}")
        elif action == "upload" and direction in ("upload", "both") and not download_only:
            if upload_to_cloud(local_file, cloud_file):
                results["uploaded"].append(comparison["filename"])
            else:
                results["errors"].append(f"上傳失敗: {comparison['filename']}")
        else:
            skip_reason = ""
            if incremental_both:
                if action == "skip" and local_file.exists() and cloud_file.exists():
                    local_mtime = comparison["local"].get("mtime", 0) if comparison["local"] else 0
                    cloud_mtime = comparison["cloud"].get("mtime", 0) if comparison["cloud"] else 0
                    if local_mtime == cloud_mtime:
                        skip_reason = " (雙向增量：檔案已同步)"
                    elif local_mtime > cloud_mtime:
                        skip_reason = " (雙向增量：本機較新，保留本機版本)"
                    else:
                        skip_reason = " (雙向增量：雲端較新，保留雲端版本)"
            elif download_only and action == "upload":
                skip_reason = " (僅下載模式：不覆蓋本機較新檔案)"
            elif download_only and not cloud_file.exists():
                skip_reason = " (僅下載模式：不處理本機多餘檔案)"
            elif upload_only and action == "download":
                skip_reason = " (僅上傳模式：不覆蓋雲端較新檔案)"
            elif upload_only and not local_file.exists():
                skip_reason = " (僅上傳模式：不處理雲端多餘檔案)"
            results["skipped"].append(comparison["filename"] + skip_reason)
    
    return results


def print_sync_results(results: Dict):
    """列印同步結果"""
    print("\n" + "=" * 60)
    print("同步結果")
    print("=" * 60)
    print(f"同步時間: {results['timestamp']}")
    print(f"同步方向: {results['direction']}")
    print(f"本機目錄: {results['local_dir']}")
    print(f"雲端目錄: {results['cloud_dir']}")
    print()
    
    if results["downloaded"]:
        print(f"下載 ({len(results['downloaded'])} 個):")
        for f in results["downloaded"][:10]:
            print(f"  ✓ {f}")
        if len(results["downloaded"]) > 10:
            print(f"  ... 還有 {len(results['downloaded']) - 10} 個")
        print()
    
    if results["uploaded"]:
        print(f"上傳 ({len(results['uploaded'])} 個):")
        for f in results["uploaded"][:10]:
            print(f"  ✓ {f}")
        if len(results["uploaded"]) > 10:
            print(f"  ... 還有 {len(results['uploaded']) - 10} 個")
        print()
    
    if results["skipped"]:
        print(f"跳過 ({len(results['skipped'])} 個):")
        for f in results["skipped"][:10]:
            print(f"  - {f}")
        if len(results["skipped"]) > 10:
            print(f"  ... 還有 {len(results['skipped']) - 10} 個")
        print()
    
    if results["errors"]:
        print(f"錯誤 ({len(results['errors'])} 個):")
        for e in results["errors"]:
            print(f"  ✗ {e}")
        print()
    
    print("=" * 60)


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="五常雲端空間雙向同步工具")
    parser.add_argument(
        "--direction",
        choices=["download", "upload", "both"],
        default="both",
        help="同步方向: download(雲端->本機), upload(本機->雲端), both(雙向)",
    )
    parser.add_argument(
        "--local-dir",
        type=str,
        help="本機目錄（預設為腳本所在目錄）",
    )
    parser.add_argument(
        "--cloud-dir",
        type=str,
        help="雲端目錄（相對於五常雲端空間，例如: reports, scripts）",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="*",
        help="檔案模式（例如: *.json, *.md, *）",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="不遞迴同步子目錄",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="僅列出需要同步的檔案，不實際執行",
    )
    parser.add_argument(
        "--download-only",
        action="store_true",
        help="僅下載模式（非鏡像）：只下載變更，不覆蓋本機較新檔案，不刪除本機多餘檔案（自動設定 --direction download）",
    )
    parser.add_argument(
        "--upload-only",
        action="store_true",
        help="僅上傳模式（非鏡像）：只上傳變更，不覆蓋雲端較新檔案，不刪除雲端多餘檔案（自動設定 --direction upload）",
    )
    parser.add_argument(
        "--incremental-both",
        action="store_true",
        help="雙向增量模式：互相增加變更，不覆蓋任何一方較新的檔案（自動設定 --direction both）",
    )
    
    args = parser.parse_args()
    
    # 獲取雲端路徑
    cloud_base = ensure_wuchang_cloud_path()
    if not cloud_base:
        print("錯誤: 無法找到五常雲端空間路徑", file=sys.stderr)
        print("請確認 Google Drive 已同步，或設定 WUCHANG_CLOUD_PATH 環境變數", file=sys.stderr)
        return 1
    
    # 如果使用特殊模式，自動設定 direction
    if sum([args.download_only, args.upload_only, args.incremental_both]) > 1:
        print("錯誤: --download-only、--upload-only 和 --incremental-both 不能同時使用", file=sys.stderr)
        return 1
    
    if args.download_only:
        if args.direction != "download":
            print("注意: --download-only 模式自動設定 --direction download", file=sys.stderr)
        args.direction = "download"
    elif args.upload_only:
        if args.direction != "upload":
            print("注意: --upload-only 模式自動設定 --direction upload", file=sys.stderr)
        args.direction = "upload"
    elif args.incremental_both:
        if args.direction != "both":
            print("注意: --incremental-both 模式自動設定 --direction both", file=sys.stderr)
        args.direction = "both"
    
    # 決定本機和雲端目錄
    local_dir = Path(args.local_dir).resolve() if args.local_dir else BASE_DIR
    if args.cloud_dir:
        cloud_dir = cloud_base / args.cloud_dir
    else:
        # 預設使用與本機目錄同名的雲端子目錄
        cloud_dir = cloud_base / local_dir.name
    
    print("=" * 60)
    if args.download_only:
        print("五常雲端空間僅下載同步（非鏡像）")
    elif args.upload_only:
        print("五常雲端空間僅上傳同步（非鏡像）")
    elif args.incremental_both:
        print("五常雲端空間雙向增量同步（互相增加變更）")
    else:
        print("五常雲端空間雙向同步")
    print("=" * 60)
    print()
    print(f"本機目錄: {local_dir}")
    print(f"雲端目錄: {cloud_dir}")
    print(f"同步方向: {args.direction}")
    print(f"檔案模式: {args.pattern}")
    print(f"遞迴同步: {not args.no_recursive}")
    if args.download_only:
        print(f"僅下載模式: 是（非鏡像，不覆蓋本機較新檔案，不刪除本機多餘檔案）")
    elif args.upload_only:
        print(f"僅上傳模式: 是（非鏡像，不覆蓋雲端較新檔案，不刪除雲端多餘檔案）")
    elif args.incremental_both:
        print(f"雙向增量模式: 是（互相增加變更，不覆蓋任何一方較新的檔案）")
    print()
    
    if args.list:
        # 僅列出需要同步的檔案
        print("需要同步的檔案：")
        # TODO: 實現列出功能
        return 0
    
    # 執行同步
    results = sync_directory(
        local_dir,
        cloud_dir,
        direction=args.direction,
        pattern=args.pattern,
        recursive=not args.no_recursive,
        download_only=args.download_only,
        upload_only=args.upload_only,
        incremental_both=args.incremental_both,
    )
    
    # 列印結果
    print_sync_results(results)
    
    # 返回碼
    if results["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
