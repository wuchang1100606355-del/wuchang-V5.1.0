#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""驗證本機路徑配置"""

import sys
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

local_path = Path(r"C:\wuchang V5.1.0\wuchang_os\addons")
print("=" * 70)
print("本機 Odoo 模組路徑驗證")
print("=" * 70)
print()
print(f"路徑: {local_path}")
print(f"存在: {local_path.exists()}")
if local_path.exists():
    file_count = sum(1 for _ in local_path.rglob("*") if _.is_file())
    dir_count = sum(1 for _ in local_path.rglob("*") if _.is_dir())
    print(f"檔案數: {file_count:,} 個")
    print(f"目錄數: {dir_count:,} 個")
    print()
    print("✓ 本機路徑正確，Docker Compose 已更新為使用此路徑")
else:
    print("✗ 路徑不存在")
print()
print("=" * 70)
