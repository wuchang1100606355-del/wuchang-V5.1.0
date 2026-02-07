#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
backup_to_gdrive.py

將本地儲存備份到 Google Drive

使用方式：
  python backup_to_gdrive.py
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

import sys
from pathlib import Path

# 使用統一的雲端同步配置
try:
    from cloud_sync_config import ensure_wuchang_cloud_path, get_sync_directories
    GDRIVE_BACKUP = ensure_wuchang_cloud_path()
    sync_dirs = get_sync_directories()
except ImportError:
    # 回退到舊配置
    GDRIVE_BACKUP = Path(r"J:\共用雲端硬碟\五常雲端空間")
    sync_dirs = {
        "database": GDRIVE_BACKUP / "database" / "backups",
        "uploads": GDRIVE_BACKUP / "uploads",
        "config": GDRIVE_BACKUP / "config",
    }

LOCAL_STORAGE = Path(r"C:\wuchang V5.1.0\wuchang-V5.1.0\local_storage")

def backup_directory(src: Path, dst: Path, name: str):
    """
    備份目錄（直接寫入雲端，本機不保留）
    
    注意：備份直接寫入雲端，不經過本機臨時目錄
    """
    if not src.exists():
        print(f"⚠️  來源不存在: {src}")
        return False
    
    dst.mkdir(parents=True, exist_ok=True)
    
    # 建立時間戳記備份（直接寫入雲端）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dst = dst / f"{name}_{timestamp}"
    
    try:
        # 直接從源檔案複製到雲端，不經過本機
        if src.is_dir():
            shutil.copytree(src, backup_dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, backup_dst)
        print(f"[OK] 已備份 {name} 到雲端: {backup_dst}")
        print(f"     注意: 備份僅存於雲端，本機不保留副本")
        return True
    except Exception as e:
        print(f"[ERROR] 備份 {name} 失敗: {e}")
        return False

def main():
    print("=" * 70)
    print("備份本地儲存到五常雲端空間（單向寫入）")
    print("=" * 70)
    print()
    
    if not GDRIVE_BACKUP:
        print("錯誤: 無法找到五常雲端空間路徑", file=sys.stderr)
        print("請確認 Google Drive 已同步，或設定 WUCHANG_CLOUD_PATH 環境變數", file=sys.stderr)
        return 1
    
    print(f"雲端空間路徑: {GDRIVE_BACKUP}")
    print("注意: 本系統為單向同步（本機 -> 雲端），僅同步到五常雲端空間")
    print("注意: 所有備份檔案直接寫入雲端，本機不保留副本")
    print()
    
    # 備份資料庫（單向：本機 -> 雲端）
    backup_directory(
        LOCAL_STORAGE / "database" / "backups",
        sync_dirs.get("database", GDRIVE_BACKUP / "database" / "backups"),
        "database_backups"
    )
    
    # 備份上傳檔案（單向：本機 -> 雲端）
    backup_directory(
        LOCAL_STORAGE / "uploads",
        sync_dirs.get("uploads", GDRIVE_BACKUP / "uploads"),
        "uploads"
    )
    
    # 備份配置檔案（單向：本機 -> 雲端）
    backup_directory(
        LOCAL_STORAGE / "config",
        sync_dirs.get("config", GDRIVE_BACKUP / "config"),
        "config"
    )
    
    print()
    print("備份完成！")

if __name__ == "__main__":
    main()
