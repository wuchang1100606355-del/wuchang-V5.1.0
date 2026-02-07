#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""檢查本機實際路徑"""

import sys
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

current_dir = Path.cwd()
print(f"當前工作目錄: {current_dir}")
print()

# 檢查相對路徑
rel_path = current_dir / "wuchang_os" / "addons"
print(f"相對路徑 ./wuchang_os/addons 解析為: {rel_path}")
print(f"存在: {rel_path.exists()}")
if rel_path.exists():
    file_count = sum(1 for _ in rel_path.rglob("*") if _.is_file())
    print(f"檔案數: {file_count:,} 個")
print()

# 檢查可能的其他位置
possible_paths = [
    Path(r"C:\wuchang V5.1.0\wuchang-V5.1.0\wuchang_os\addons"),
    Path(r"C:\wuchang V5.1.0\wuchang_os\addons"),
    current_dir.parent / "wuchang_os" / "addons",
    current_dir / "wuchang_os" / "addons",
]

print("檢查其他可能的位置:")
for p in possible_paths:
    exists = p.exists()
    status = "✓" if exists else "✗"
    print(f"{status} {p}")
    if exists:
        try:
            file_count = sum(1 for _ in p.rglob("*") if _.is_file())
            print(f"   檔案數: {file_count:,} 個")
        except:
            pass
    print()
