#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_wuchang_to_cloud.py

同步 C:\\wuchang V5.1.0 與五常雲端空間

功能：
- 從 C:\\wuchang V5.1.0 同步到五常雲端空間
- 支援雙向增量同步（互相增加變更，不覆蓋）- 預設模式
- 支援雙向同步、僅下載、僅上傳模式
- 自動配置目錄映射

預設模式：雙向增量（incremental-both）
- 互相增加變更：下載雲端新增/更新，上傳本機新增/更新
- 不覆蓋較新檔案：保留任何一方較新的版本
- 非鏡像同步：不會讓任何一方完全鏡像另一方
"""

from __future__ import annotations

import sys
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

try:
    from cloud_bidirectional_sync import main as sync_main
    from cloud_sync_config import ensure_wuchang_cloud_path
except ImportError as e:
    print(f"錯誤: 無法導入必要模組: {e}", file=sys.stderr)
    sys.exit(1)

WUCHANG_LOCAL = Path(r"C:\wuchang V5.1.0\wuchang-V5.1.0")


def get_sync_mapping() -> dict[str, tuple[Path, str]]:
    """
    獲取 C:\\wuchang V5.1.0 與五常雲端空間的目錄映射
    
    返回：字典 {本地目錄名稱: (本地路徑, 雲端目錄名稱)}
    """
    cloud_base = ensure_wuchang_cloud_path()
    
    return {
        "local_storage": (
            WUCHANG_LOCAL / "local_storage",
            "local_storage"
        ),
        "scripts": (
            WUCHANG_LOCAL,
            "scripts"
        ),
        "reports": (
            WUCHANG_LOCAL,
            "reports"
        ),
        "config": (
            WUCHANG_LOCAL,
            "config"
        ),
    }


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="同步 C:\\wuchang V5.1.0 與五常雲端空間"
    )
    parser.add_argument(
        "--mode",
        choices=["download", "upload", "both", "download-only", "upload-only", "incremental-both"],
        default="incremental-both",
        help="同步模式: incremental-both(雙向增量-互相增加變更，預設), download(雲端->本機), upload(本機->雲端), both(雙向), download-only(僅下載變更), upload-only(僅上傳變更)",
    )
    parser.add_argument(
        "--category",
        choices=["all", "local_storage", "scripts", "reports", "config"],
        default="all",
        help="同步類別: all(全部), local_storage(本地儲存), scripts(腳本), reports(報告), config(配置)",
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
    
    args = parser.parse_args()
    
    # 檢查本地目錄是否存在
    if not WUCHANG_LOCAL.exists():
        print(f"錯誤: 本地目錄不存在: {WUCHANG_LOCAL}", file=sys.stderr)
        print("請確認 C:\\wuchang V5.1.0\\wuchang-V5.1.0 目錄存在", file=sys.stderr)
        return 1
    
    # 獲取雲端路徑
    cloud_base = ensure_wuchang_cloud_path()
    if not cloud_base:
        print("錯誤: 無法找到五常雲端空間路徑", file=sys.stderr)
        print("請確認 Google Drive 已同步，或設定 WUCHANG_CLOUD_PATH 環境變數", file=sys.stderr)
        return 1
    
    print("=" * 70)
    print("C:\\wuchang V5.1.0 與五常雲端空間同步")
    print("=" * 70)
    print()
    print(f"本地目錄: {WUCHANG_LOCAL}")
    print(f"雲端空間: {cloud_base}")
    print(f"同步模式: {args.mode}")
    if args.mode == "incremental-both":
        print("  說明: 雙向增量同步（互相增加變更，不覆蓋較新檔案）")
    print(f"同步類別: {args.category}")
    print()
    
    # 獲取目錄映射
    sync_mapping = get_sync_mapping()
    
    # 決定要同步的目錄
    if args.category == "all":
        categories_to_sync = list(sync_mapping.keys())
    else:
        categories_to_sync = [args.category]
    
    # 執行同步
    results = []
    for category in categories_to_sync:
        if category not in sync_mapping:
            print(f"⚠️  未知類別: {category}")
            continue
        
        local_path, cloud_dir_name = sync_mapping[category]
        cloud_path = cloud_base / cloud_dir_name
        
        print("-" * 70)
        print(f"同步類別: {category}")
        print(f"  本地: {local_path}")
        print(f"  雲端: {cloud_path}")
        print("-" * 70)
        print()
        
        try:
            # 直接調用同步邏輯
            from cloud_bidirectional_sync import sync_directory, print_sync_results
            
            # 決定同步參數
            if args.mode == "download-only":
                direction = "download"
                download_only = True
                upload_only = False
                incremental_both = False
            elif args.mode == "upload-only":
                direction = "upload"
                download_only = False
                upload_only = True
                incremental_both = False
            elif args.mode == "incremental-both":
                direction = "both"
                download_only = False
                upload_only = False
                incremental_both = True
            else:
                direction = args.mode
                download_only = False
                upload_only = False
                incremental_both = False
            
            result = sync_directory(
                local_path,
                cloud_path,
                direction=direction,
                pattern=args.pattern,
                recursive=not args.no_recursive,
                download_only=download_only,
                upload_only=upload_only,
                incremental_both=incremental_both,
            )
            
            results.append({
                "category": category,
                "result": result,
            })
            
            # 顯示結果
            print_sync_results(result)
            
        except Exception as e:
            print(f"❌ 同步 {category} 失敗: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            results.append({
                "category": category,
                "result": {
                    "downloaded": [],
                    "uploaded": [],
                    "skipped": [],
                    "errors": [str(e)],
                },
            })
    
    # 總結
    print()
    print("=" * 70)
    print("同步總結")
    print("=" * 70)
    
    total_downloaded = sum(len(r["result"]["downloaded"]) for r in results)
    total_uploaded = sum(len(r["result"]["uploaded"]) for r in results)
    total_skipped = sum(len(r["result"]["skipped"]) for r in results)
    total_errors = sum(len(r["result"]["errors"]) for r in results)
    
    print(f"總下載: {total_downloaded} 個檔案")
    print(f"總上傳: {total_uploaded} 個檔案")
    print(f"總跳過: {total_skipped} 個檔案")
    if total_errors > 0:
        print(f"總錯誤: {total_errors} 個")
    
    print("=" * 70)
    
    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
