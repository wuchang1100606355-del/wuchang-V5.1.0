#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rollback_snapshot_20260119_150234.py

回滾到快照: snapshot_20260119_150234

建立時間: 2026-01-19T15:02:34.611612
"""

import sys
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SNAPSHOT_DIR = BASE_DIR / "snapshots" / "snapshot_20260119_150234"

def rollback():
    """執行回滾"""
    print("=" * 70)
    print("回滾到快照: snapshot_20260119_150234")
    print("=" * 70)
    print()
    
    if not SNAPSHOT_DIR.exists():
        print(f"✗ 快照目錄不存在: {SNAPSHOT_DIR}")
        return False
    
    # 讀取元數據
    metadata_file = SNAPSHOT_DIR / "metadata.json"
    if metadata_file.exists():
        import json
        metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
        print("快照資訊：")
        print(f"  建立時間: {metadata.get('created_at', 'N/A')}")
        print(f"  目的: {metadata.get('purpose', 'N/A')}")
        print()
    
    # 還原檔案
    restored = 0
    failed = 0
    
    for file_path in SNAPSHOT_DIR.iterdir():
        if file_path.name in ["metadata.json", "environment_variables.json"]:
            continue
        
        try:
            dest = BASE_DIR / file_path.name
            shutil.copy2(file_path, dest)
            print(f"  ✓ 已還原: {file_path.name}")
            restored += 1
        except Exception as e:
            print(f"  ✗ 還原失敗 {file_path.name}: {e}")
            failed += 1
    
    print()
    print(f"已還原 {restored} 個檔案")
    if failed > 0:
        print(f"失敗 {failed} 個檔案")
    
    print()
    print("=" * 70)
    print("回滾完成")
    print("=" * 70)
    
    return failed == 0

if __name__ == "__main__":
    success = rollback()
    sys.exit(0 if success else 1)
