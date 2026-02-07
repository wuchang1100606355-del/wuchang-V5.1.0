#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
create_cloud_symlink.py

將 C 碟目錄改為符號連結，指向雲端目錄
這樣可以節省 C 碟空間，同時保持路徑兼容性
"""

from __future__ import annotations

import os
import sys
import shutil
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

C_SOURCE = Path(r"C:\wuchang V5.1.0\wuchang-V5.1.0")
CLOUD_TARGET = Path(r"J:\共用雲端硬碟\五常雲端空間\wuchang-V5.1.0")


def create_symlink_to_cloud(source: Path, target: Path, dry_run: bool = False) -> bool:
    """將 C 碟目錄改為指向雲端的符號連結"""
    
    if not target.exists():
        print(f"錯誤: 雲端目標目錄不存在: {target}")
        return False
    
    if not source.exists():
        print(f"錯誤: 源目錄不存在: {source}")
        return False
    
    # 檢查是否已經是符號連結
    if source.is_symlink():
        try:
            current_target = source.readlink()
            if current_target == target:
                print(f"✓ 已經是正確的符號連結: {source} -> {target}")
                return True
            else:
                print(f"⚠️  現有符號連結指向不同位置: {current_target}")
                print(f"   需要更新為: {target}")
        except:
            print(f"⚠️  無法讀取現有符號連結")
    
    if dry_run:
        print(f"[模擬] 將創建符號連結: {source} -> {target}")
        print(f"      這會將現有目錄移動到備份位置，然後創建符號連結")
        return True
    
    # 備份現有目錄
    backup_path = source.parent / f"{source.name}.backup_before_symlink"
    if backup_path.exists():
        backup_path = source.parent / f"{source.name}.backup_before_symlink_{Path(target).stat().st_mtime}"
    
    try:
        print(f"正在備份現有目錄到: {backup_path}")
        if source.is_symlink():
            source.unlink()
        else:
            shutil.move(str(source), str(backup_path))
        
        # 創建符號連結
        print(f"正在創建符號連結: {source} -> {target}")
        os.symlink(target, source, target_is_directory=True)
        
        # 驗證
        if source.is_symlink():
            actual_target = source.readlink()
            if actual_target == target:
                print(f"✓ 符號連結創建成功")
                print(f"  備份位置: {backup_path}")
                return True
            else:
                print(f"⚠️  符號連結指向不正確: {actual_target}")
                return False
        else:
            print(f"⚠️  符號連結創建失敗")
            return False
            
    except OSError as e:
        if e.winerror == 1314:  # ERROR_PRIVILEGE_NOT_HELD
            print(f"錯誤: 需要管理員權限創建符號連結")
            print(f"請以管理員身份運行此腳本")
            return False
        else:
            print(f"錯誤: {e}")
            return False
    except Exception as e:
        print(f"錯誤: {e}")
        # 嘗試恢復備份
        if backup_path.exists():
            try:
                print(f"嘗試恢復備份...")
                shutil.move(str(backup_path), str(source))
            except:
                print(f"⚠️  無法恢復備份，請手動檢查: {backup_path}")
        return False


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="將 C 碟目錄改為指向雲端的符號連結"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="模擬模式，不實際執行",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="執行實際操作（需要明確指定）",
    )
    parser.add_argument(
        "--source",
        type=str,
        default=str(C_SOURCE),
        help=f"源目錄（預設: {C_SOURCE}）",
    )
    parser.add_argument(
        "--target",
        type=str,
        default=str(CLOUD_TARGET),
        help=f"雲端目標目錄（預設: {CLOUD_TARGET}）",
    )
    
    args = parser.parse_args()
    
    source = Path(args.source)
    target = Path(args.target)
    
    print("=" * 70)
    print("將 C 碟目錄改為指向雲端的符號連結")
    print("=" * 70)
    print()
    print(f"源目錄 (C 碟): {source}")
    print(f"雲端目標: {target}")
    print(f"模式: {'模擬模式' if args.dry_run else '實際執行'}")
    print()
    
    # 檢查目錄
    if not source.exists():
        print(f"錯誤: 源目錄不存在: {source}", file=sys.stderr)
        return 1
    
    if not target.exists():
        print(f"錯誤: 雲端目標目錄不存在: {target}", file=sys.stderr)
        print(f"請確認 Google Drive 已同步", file=sys.stderr)
        return 1
    
    # 檢查大小（確認是同步的）
    try:
        def get_size(p):
            return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
        source_size = get_size(source)
        target_size = get_size(target)
        size_diff = abs(source_size - target_size)
        size_diff_percent = (size_diff / max(source_size, target_size) * 100) if max(source_size, target_size) > 0 else 0
        
        print(f"目錄大小:")
        print(f"  C 碟: {source_size / (1024**3):.2f} GB")
        print(f"  雲端: {target_size / (1024**3):.2f} GB")
        print(f"  差異: {size_diff_percent:.2f}%")
        print()
        
        if size_diff_percent > 5:
            print("⚠️  警告: C 碟和雲端目錄大小差異較大")
            print("   這可能表示內容不完全同步")
            print("   建議先同步後再執行此操作")
            print()
    except Exception as e:
        print(f"⚠️  無法比較目錄大小: {e}")
        print()
    
    if args.dry_run:
        print("這是模擬模式，不會實際執行。")
        print("使用 --execute 來執行實際操作。")
        create_symlink_to_cloud(source, target, dry_run=True)
        return 0
    
    if not args.execute:
        print("錯誤: 需要明確指定 --execute 來執行實際操作", file=sys.stderr)
        print("這是為了安全考慮，避免意外修改目錄結構", file=sys.stderr)
        return 1
    
    # 確認
    try:
        print("警告: 此操作將：")
        print("  1. 備份現有的 C 碟目錄")
        print("  2. 刪除 C 碟目錄")
        print("  3. 創建指向雲端的符號連結")
        print()
        confirm = input("是否繼續？(yes/N): ").strip().lower()
        if confirm != "yes":
            print("已取消")
            return 0
    except KeyboardInterrupt:
        print("\n已取消")
        return 0
    
    # 執行
    print()
    success = create_symlink_to_cloud(source, target, dry_run=False)
    
    if success:
        print()
        print("=" * 70)
        print("✓ 操作完成")
        print("=" * 70)
        print()
        print("現在 C 碟目錄是指向雲端的符號連結")
        print("檔案實際存儲在雲端，節省了 C 碟空間")
        return 0
    else:
        print()
        print("=" * 70)
        print("✗ 操作失敗")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
