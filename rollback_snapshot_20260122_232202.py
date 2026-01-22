#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rollback_snapshot_20260122_232202.py

回滾到快照: snapshot_20260122_232202

建立時間: 2026-01-22T23:22:02.500191
目的: 雲端資料推送後回滾點
"""

import sys
import json
import shutil
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
SNAPSHOT_DIR = BASE_DIR / "snapshots" / "snapshot_20260122_232202"

def rollback():
    """執行回滾"""
    print("=" * 70)
    print("回滾到快照: snapshot_20260122_232202")
    print("=" * 70)
    print()
    
    if not SNAPSHOT_DIR.exists():
        print(f"✗ 快照目錄不存在: {SNAPSHOT_DIR}")
        return False
    
    # 讀取元數據
    metadata_file = SNAPSHOT_DIR / "metadata.json"
    if metadata_file.exists():
        metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
        print("快照資訊：")
        print(f"  建立時間: {metadata.get('created_at', 'N/A')}")
        print(f"  目的: {metadata.get('purpose', 'N/A')}")
        print(f"  檔案數量: {metadata.get('file_count', 0)}")
        print()
    
    # 確認回滾
    print("⚠️  警告：此操作將覆蓋現有檔案！")
    print("按 Ctrl+C 取消，或按 Enter 繼續...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n已取消回滾")
        return False
    
    # 還原檔案
    restored = 0
    failed = 0
    
    print()
    print("正在還原檔案...")
    print()
    
    for file_path in SNAPSHOT_DIR.rglob("*"):
        if file_path.is_file() and file_path.name not in ["metadata.json", "environment_variables.json"]:
            try:
                rel_path = file_path.relative_to(SNAPSHOT_DIR)
                dest = BASE_DIR / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest)
                print(f"  ✓ 已還原: {rel_path}")
                restored += 1
            except Exception as e:
                print(f"  ✗ 還原失敗 {file_path.name}: {e}")
                failed += 1
    
    print()
    print("=" * 70)
    print("回滾結果")
    print("=" * 70)
    print(f"已還原: {restored} 個檔案")
    if failed > 0:
        print(f"失敗: {failed} 個檔案")
    print()
    
    if failed == 0:
        print("✓ 回滾完成")
    else:
        print("⚠️  回滾完成，但有部分檔案還原失敗")
    
    print()
    print("=" * 70)
    
    return failed == 0

if __name__ == "__main__":
    success = rollback()
    sys.exit(0 if success else 1)
