#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""檢查 J 碟情況"""

import sys
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

j_drive = Path("J:\\")
print(f"J 碟存在: {j_drive.exists()}")

if j_drive.exists():
    print("\nJ 碟根目錄下的目錄（前10個）:")
    dirs = [d for d in j_drive.iterdir() if d.is_dir()]
    for d in dirs[:10]:
        print(f"  {d}")
    
    print("\n搜尋包含 'wuchang' 的目錄:")
    wuchang_dirs = []
    try:
        for item in j_drive.rglob("*wuchang*"):
            if item.is_dir():
                wuchang_dirs.append(item)
                if len(wuchang_dirs) >= 10:
                    break
    except Exception as e:
        print(f"  搜尋錯誤: {e}")
    
    for d in wuchang_dirs:
        print(f"  {d}")
    
    # 檢查預期的遷移目標
    expected = Path(r"J:\wuchang V5.1.0\wuchang-V5.1.0")
    print(f"\n預期遷移目標: {expected}")
    print(f"  存在: {expected.exists()}")
    if expected.exists():
        print(f"  是符號連結: {expected.is_symlink()}")
        if expected.is_symlink():
            try:
                print(f"  指向: {expected.readlink()}")
            except:
                print("  無法讀取連結目標")
