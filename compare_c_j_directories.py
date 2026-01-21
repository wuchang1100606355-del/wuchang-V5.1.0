#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""比較 C 碟和 J 碟（雲端）的目錄大小和內容"""

import sys
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

C_SOURCE = Path(r"C:\wuchang V5.1.0\wuchang-V5.1.0")
J_CLOUD = Path(r"J:\共用雲端硬碟\五常雲端空間\wuchang-V5.1.0")

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
    except Exception as e:
        print(f"  計算大小時出錯: {e}")
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
    except Exception as e:
        print(f"  計算檔案數時出錯: {e}")
    return count

print("=" * 70)
print("C 碟與 J 碟（雲端）目錄比較")
print("=" * 70)
print()

print(f"C 碟目錄: {C_SOURCE}")
print(f"  存在: {C_SOURCE.exists()}")
print(f"  是符號連結: {C_SOURCE.is_symlink() if C_SOURCE.exists() else False}")
if C_SOURCE.exists() and C_SOURCE.is_symlink():
    try:
        print(f"  指向: {C_SOURCE.readlink()}")
    except:
        print("  無法讀取連結目標")
print()

print(f"J 碟（雲端）目錄: {J_CLOUD}")
print(f"  存在: {J_CLOUD.exists()}")
print(f"  是符號連結: {J_CLOUD.is_symlink() if J_CLOUD.exists() else False}")
print()

if C_SOURCE.exists() and J_CLOUD.exists():
    print("正在計算大小和檔案數量（這可能需要一些時間）...")
    print()
    
    c_size = get_dir_size(C_SOURCE)
    j_size = get_dir_size(J_CLOUD)
    c_count = count_files(C_SOURCE)
    j_count = count_files(J_CLOUD)
    
    print("大小比較：")
    print(f"  C 碟: {c_size / (1024**3):.2f} GB ({c_size:,} bytes)")
    print(f"  J 碟: {j_size / (1024**3):.2f} GB ({j_size:,} bytes)")
    size_diff = abs(c_size - j_size)
    size_diff_percent = (size_diff / max(c_size, j_size) * 100) if max(c_size, j_size) > 0 else 0
    print(f"  差異: {size_diff / (1024**3):.2f} GB ({size_diff_percent:.2f}%)")
    print()
    
    print("檔案數量比較：")
    print(f"  C 碟: {c_count:,} 個檔案")
    print(f"  J 碟: {j_count:,} 個檔案")
    print(f"  差異: {abs(c_count - j_count):,} 個檔案")
    print()
    
    print("=" * 70)
    print("結論")
    print("=" * 70)
    if size_diff_percent < 1:
        print("⚠️  警告：C 碟和 J 碟（雲端）大小幾乎相同！")
        print()
        print("可能的原因：")
        print("  1. 這是雲端同步的結果（Google Drive 同步）")
        print("  2. 手動複製了整個目錄到雲端")
        print("  3. 遷移腳本沒有執行，或者執行時目標路徑配置錯誤")
        print()
        print("遷移腳本預期的目標路徑是：")
        print(f"  J:\\wuchang V5.1.0\\wuchang-V5.1.0")
        print()
        print("但實際的雲端目錄是：")
        print(f"  {J_CLOUD}")
        print()
        print("這表示：")
        print("  - 如果這是雲端同步，那麼 C 碟和 J 碟（雲端）內容相同是正常的")
        print("  - 如果要做遷移，需要確認目標路徑是否正確")
    else:
        print("✓ C 碟和 J 碟（雲端）大小有差異")
elif not C_SOURCE.exists():
    print("⚠️  C 碟目錄不存在")
elif not J_CLOUD.exists():
    print("⚠️  J 碟（雲端）目錄不存在")
