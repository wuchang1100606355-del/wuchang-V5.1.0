#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_archive_to_cloud.py

自動歸檔到雲端歷史資料庫
- 監控特定目錄，自動歸檔新檔案
- 整合到備份、健康報告等流程
"""

import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

# 設定 UTF-8 編碼輸出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    from cloud_history_database import (
        archive_backup_path,
        archive_health_report,
        archive_deployment_log,
        get_cloud_drive_path
    )
except ImportError:
    print("⚠️  無法匯入 cloud_history_database，請確認模組已安裝")
    sys.exit(1)


def auto_archive_new_files():
    """自動歸檔新檔案到雲端歷史資料庫"""
    BASE_DIR = Path(__file__).resolve().parent
    
    # 檢查雲端硬碟
    cloud_root = get_cloud_drive_path()
    if not cloud_root:
        print("⚠️  無法找到雲端硬碟路徑")
        return False
    
    archived_count = 0
    
    # 歸檔健康報告
    health_report_dir = BASE_DIR / "健康報告"
    if health_report_dir.exists():
        for report_file in health_report_dir.glob("*.md"):
            # 檢查是否已歸檔（檢查雲端是否有對應的路徑檔案）
            cloud_path_file = cloud_root / "系統歷史資料庫" / "健康報告" / "異常報告" / f"{report_file.name}.path.json"
            if not cloud_path_file.exists():
                try:
                    if archive_health_report(report_file):
                        archived_count += 1
                        print(f"✅ 已歸檔: {report_file.name}")
                except Exception as e:
                    print(f"❌ 歸檔失敗 {report_file.name}: {e}")
    
    # 歸檔備份
    backup_dirs = [BASE_DIR / "backups", BASE_DIR / "snapshots"]
    for backup_dir in backup_dirs:
        if backup_dir.exists():
            for backup_file in backup_dir.rglob("*"):
                if backup_file.is_file() and not backup_file.suffix == ".path.json":
                    # 檢查是否已歸檔
                    cloud_path_file = cloud_root / "系統歷史資料庫" / "備份" / "完整備份" / f"{backup_file.name}.path.json"
                    if not cloud_path_file.exists():
                        try:
                            if archive_backup_path(backup_file, description="自動歸檔"):
                                archived_count += 1
                                print(f"✅ 已歸檔: {backup_file.name}")
                        except Exception as e:
                            print(f"❌ 歸檔失敗 {backup_file.name}: {e}")
    
    return archived_count > 0


if __name__ == "__main__":
    print("=" * 60)
    print("自動歸檔到雲端歷史資料庫")
    print("=" * 60)
    
    if auto_archive_new_files():
        print(f"\n✅ 自動歸檔完成")
    else:
        print(f"\nℹ️  沒有新檔案需要歸檔")
