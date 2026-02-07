#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查遷移狀態：確認 C 碟和 J 碟的檔案情況
"""

import sys
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

C_SOURCE = Path(r"C:\wuchang V5.1.0\wuchang-V5.1.0")
J_TARGET = Path(r"J:\wuchang V5.1.0\wuchang-V5.1.0")

def get_dir_size(path: Path) -> int:
    """計算目錄總大小"""
    if not path.exists():
        return 0
    total = 0
    try:
        for item in path.rglob("*"):
            if item.is_file():
                try:
                    total += item.stat().st_size
                except:
                    pass
    except:
        pass
    return total

def count_files(path: Path) -> int:
    """計算檔案數量"""
    if not path.exists():
        return 0
    count = 0
    try:
        for item in path.rglob("*"):
            if item.is_file():
                count += 1
    except:
        pass
    return count

def check_symlinks(path: Path) -> list:
    """檢查符號連結"""
    symlinks = []
    if not path.exists():
        return symlinks
    try:
        for item in path.iterdir():
            if item.is_symlink():
                try:
                    target = item.readlink()
                    symlinks.append({
                        "name": item.name,
                        "target": str(target),
                        "target_exists": target.exists()
                    })
                except:
                    symlinks.append({
                        "name": item.name,
                        "target": "無法讀取",
                        "target_exists": False
                    })
    except:
        pass
    return symlinks

print("=" * 70)
print("遷移狀態檢查")
print("=" * 70)
print()

# 檢查目錄是否存在
print("目錄存在性：")
print(f"  C 碟: {C_SOURCE} - {'存在' if C_SOURCE.exists() else '不存在'}")
print(f"  J 碟: {J_TARGET} - {'存在' if J_TARGET.exists() else '不存在'}")
print()

# 檢查大小
if C_SOURCE.exists() and J_TARGET.exists():
    print("目錄大小：")
    c_size = get_dir_size(C_SOURCE)
    j_size = get_dir_size(J_TARGET)
    print(f"  C 碟: {c_size / (1024**3):.2f} GB ({c_size:,} bytes)")
    print(f"  J 碟: {j_size / (1024**3):.2f} GB ({j_size:,} bytes)")
    print(f"  差異: {(c_size - j_size) / (1024**3):.2f} GB")
    print()
    
    # 檢查檔案數量
    print("檔案數量：")
    c_count = count_files(C_SOURCE)
    j_count = count_files(J_TARGET)
    print(f"  C 碟: {c_count:,} 個檔案")
    print(f"  J 碟: {j_count:,} 個檔案")
    print(f"  差異: {c_count - j_count:,} 個檔案")
    print()
    
    # 檢查符號連結
    print("符號連結檢查：")
    c_symlinks = check_symlinks(C_SOURCE)
    if c_symlinks:
        print(f"  C 碟發現 {len(c_symlinks)} 個符號連結：")
        for sl in c_symlinks[:10]:  # 只顯示前10個
            status = "✓" if sl["target_exists"] else "✗"
            print(f"    {status} {sl['name']} -> {sl['target']}")
        if len(c_symlinks) > 10:
            print(f"    ... 還有 {len(c_symlinks) - 10} 個符號連結")
    else:
        print("  C 碟沒有發現符號連結")
    print()
    
    # 檢查常見的遷移目錄
    print("遷移目錄檢查：")
    migrate_dirs = ["local_storage", "data", "uploads", "backups", "logs", "cache", "temp"]
    for dir_name in migrate_dirs:
        c_dir = C_SOURCE / dir_name
        j_dir = J_TARGET / dir_name
        c_exists = c_dir.exists()
        j_exists = j_dir.exists()
        c_is_symlink = c_dir.is_symlink() if c_exists else False
        
        if c_exists or j_exists:
            status = []
            if c_exists:
                if c_is_symlink:
                    status.append("C:符號連結")
                else:
                    status.append("C:實體檔案")
            if j_exists:
                status.append("J:存在")
            print(f"  {dir_name}: {' | '.join(status)}")
    print()

# 結論
print("=" * 70)
print("結論")
print("=" * 70)
if C_SOURCE.exists() and J_TARGET.exists():
    c_size = get_dir_size(C_SOURCE)
    j_size = get_dir_size(J_TARGET)
    size_diff = abs(c_size - j_size)
    size_diff_percent = (size_diff / max(c_size, j_size) * 100) if max(c_size, j_size) > 0 else 0
    
    if size_diff_percent < 1:  # 差異小於1%
        print("⚠️  警告：C 碟和 J 碟大小幾乎相同！")
        print("   這表示遷移可能沒有正確執行，或者刪除操作失敗。")
        print()
        print("可能的原因：")
        print("  1. 遷移腳本沒有執行（只是複製了檔案）")
        print("  2. 遷移腳本執行了，但刪除 C 碟原始檔案的操作失敗")
        print("  3. 符號連結創建失敗，導致原始檔案還在")
        print()
        print("建議：")
        print("  1. 檢查是否有符號連結（上方已顯示）")
        print("  2. 如果沒有符號連結，可能需要重新執行遷移")
        print("  3. 如果有符號連結但檔案還在，可能是刪除權限問題")
    else:
        print("✓ C 碟和 J 碟大小有差異，遷移可能已部分執行")
else:
    print("⚠️  無法比較：C 碟或 J 碟不存在")
