#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_upload_reports_to_cloud.py

自動上傳報告檔案至雲端空間

功能：
- 自動上傳最近的報告檔案
- 自動上傳檢查腳本
- 顯示上傳結果
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

BASE_DIR = Path(__file__).resolve().parent

# 使用統一的雲端同步配置（單向：本機 -> 雲端）
try:
    from cloud_sync_config import ensure_wuchang_cloud_path, get_sync_directories
    GDRIVE_BACKUP = ensure_wuchang_cloud_path()
    sync_dirs = get_sync_directories()
except ImportError:
    # 回退到舊配置
    GDRIVE_BACKUP = Path(r"J:\共用雲端硬碟\五常雲端空間")
    sync_dirs = {
        "reports": GDRIVE_BACKUP / "reports",
        "scripts": GDRIVE_BACKUP / "scripts",
    }


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌",
        "PROGRESS": "🔄"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")


def upload_file(src: Path, dst_dir: Path, category: str = "reports"):
    """上傳檔案到雲端"""
    if not src.exists() or not src.is_file():
        return False
    
    # 建立目標目錄
    target_dir = dst_dir / category
    target_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 直接複製檔案（不帶時間戳，覆蓋舊版本）
        dst = target_dir / src.name
        shutil.copy2(src, dst)
        log(f"已上傳: {src.name}", "OK")
        return True
    except Exception as e:
        log(f"上傳 {src.name} 失敗: {e}", "ERROR")
        return False


def main():
    """主函數"""
    print("=" * 70)
    print("自動上傳報告檔案至五常雲端空間（單向寫入）")
    print("=" * 70)
    print()
    
    # 檢查 Google Drive 路徑
    if not GDRIVE_BACKUP or not GDRIVE_BACKUP.exists():
        log(f"五常雲端空間路徑不存在: {GDRIVE_BACKUP}", "ERROR")
        log("請確認 Google Drive 已同步，或設定 WUCHANG_CLOUD_PATH 環境變數", "WARN")
        return 1
    
    log(f"雲端空間路徑: {GDRIVE_BACKUP}", "OK")
    log("注意: 本系統為單向同步（本機 -> 雲端），僅同步到五常雲端空間", "INFO")
    print()
    
    # 要上傳的報告檔案
    report_files = [
        "POS_MENU_CHECK_REPORT.md",
        "POS_SYSTEMS_REPORT.md",
        "POS_SYSTEMS_SUMMARY.md",
        "POS_NAME_UPDATE_REPORT.md",
        "MODULE_INSTALLATION_REPORT.md",
        "MODULE_INSTALLATION_SUMMARY.md",
        "MODULE_INSTALLATION_COMPLETE.md",
        "ODOO_MODULES_STATUS.md",
        "DOCUMENT_MEETING_SYSTEM_VERIFICATION_REPORT.md",
        "CONTAINER_DIAGNOSIS_REPORT.md",
        "CONTAINER_FIX_SUMMARY.md",
        "RECOMMENDED_TASKS_EXECUTION_REPORT.md",
        "DEPLOYMENT_STATUS.md",
    ]
    
    # 要上傳的檢查腳本
    script_files = [
        "check_pos_menu.py",
        "check_pos_systems.py",
        "check_module_installation.py",
        "verify_document_meeting_system.py",
        "check_deployment.py",
    ]
    
    uploaded = []
    failed = []
    
    # 上傳報告檔案
    log("上傳報告檔案...", "PROGRESS")
    for filename in report_files:
        file_path = BASE_DIR / filename
        if file_path.exists():
            if upload_file(file_path, GDRIVE_BACKUP, "reports"):
                uploaded.append(file_path)
            else:
                failed.append(file_path)
        else:
            log(f"檔案不存在: {filename}", "WARN")
    
    print()
    
    # 上傳檢查腳本
    log("上傳檢查腳本...", "PROGRESS")
    for filename in script_files:
        file_path = BASE_DIR / filename
        if file_path.exists():
            if upload_file(file_path, GDRIVE_BACKUP, "scripts"):
                uploaded.append(file_path)
            else:
                failed.append(file_path)
        else:
            log(f"檔案不存在: {filename}", "WARN")
    
    # 顯示結果
    print()
    print("=" * 70)
    print("【上傳結果】")
    print("=" * 70)
    print()
    
    if uploaded:
        log(f"成功上傳 {len(uploaded)} 個檔案", "OK")
        print()
        print("上傳的檔案：")
        for f in uploaded:
            print(f"  ✓ {f.name}")
    
    if failed:
        log(f"上傳失敗 {len(failed)} 個檔案", "WARN")
        for f in failed:
            print(f"  ✗ {f.name}")
    
    print()
    log(f"檔案已上傳至: {GDRIVE_BACKUP}", "OK")
    print(f"  報告: {GDRIVE_BACKUP / 'reports'}")
    print(f"  腳本: {GDRIVE_BACKUP / 'scripts'}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
