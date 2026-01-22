#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
upload_files_to_cloud.py

將檔案上傳至雲端空間（Google Drive）

功能：
- 上傳指定檔案或目錄到 Google Drive
- 支援多檔案上傳
- 顯示上傳進度
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

from cloud_sync_config import ensure_wuchang_cloud_path, get_sync_directories

BASE_DIR = Path(__file__).resolve().parent
# 使用統一配置獲取五常雲端空間路徑
GDRIVE_BACKUP = ensure_wuchang_cloud_path()


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


def upload_file_or_directory(src: Path, dst_base: Path, category: str = "files"):
    """上傳檔案或目錄到雲端"""
    if not src.exists():
        log(f"來源不存在: {src}", "ERROR")
        return False
    
    # 建立目標目錄
    dst_dir = dst_base / category
    dst_dir.mkdir(parents=True, exist_ok=True)
    
    # 建立時間戳記
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        if src.is_dir():
            # 上傳目錄
            dst = dst_dir / f"{src.name}_{timestamp}"
            shutil.copytree(src, dst, dirs_exist_ok=True)
            log(f"已上傳目錄: {src.name} -> {dst}", "OK")
        else:
            # 上傳檔案
            dst = dst_dir / f"{src.stem}_{timestamp}{src.suffix}"
            shutil.copy2(src, dst)
            log(f"已上傳檔案: {src.name} -> {dst.name}", "OK")
        
        return True
    except Exception as e:
        log(f"上傳失敗: {e}", "ERROR")
        return False


def upload_recent_files(dst_base: Path, file_patterns=None, max_files=10):
    """上傳最近的檔案"""
    if file_patterns is None:
        file_patterns = ["*.md", "*.py", "*.json", "*.yml", "*.yaml"]
    
    log("搜尋最近的檔案...", "PROGRESS")
    
    uploaded = []
    for pattern in file_patterns:
        files = list(BASE_DIR.glob(pattern))
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        for f in files[:max_files]:
            if f.is_file() and f.name not in [u.name for u in uploaded]:
                if upload_file_or_directory(f, dst_base, "recent_files"):
                    uploaded.append(f)
    
    return uploaded


def upload_reports(dst_base: Path):
    """上傳報告檔案"""
    log("上傳報告檔案...", "PROGRESS")
    
    report_patterns = ["*_REPORT.md", "*_SUMMARY.md", "*_VERIFICATION*.md", "*_STATUS.md"]
    reports = []
    
    for pattern in report_patterns:
        for f in BASE_DIR.glob(pattern):
            if f.is_file():
                if upload_file_or_directory(f, dst_base, "reports"):
                    reports.append(f)
    
    return reports


def upload_scripts(dst_base: Path):
    """上傳腳本檔案"""
    log("上傳腳本檔案...", "PROGRESS")
    
    scripts = []
    for f in BASE_DIR.glob("*.py"):
        if f.is_file() and f.name not in ["__init__.py"]:
            if upload_file_or_directory(f, dst_base, "scripts"):
                scripts.append(f)
    
    return scripts


def main():
    """主函數"""
    print("=" * 70)
    print("上傳檔案至五常雲端空間（單向寫入）")
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
    
    # 上傳選項
    print("請選擇要上傳的內容：")
    print("  1. 上傳最近的檔案（報告、腳本等）")
    print("  2. 上傳所有報告檔案")
    print("  3. 上傳所有腳本檔案")
    print("  4. 上傳指定檔案或目錄")
    print("  5. 全部上傳")
    print()
    
    try:
        choice = input("請選擇 (1-5): ").strip()
        
        uploaded_files = []
        
        if choice == "1":
            uploaded_files = upload_recent_files(GDRIVE_BACKUP)
        elif choice == "2":
            uploaded_files = upload_reports(GDRIVE_BACKUP)
        elif choice == "3":
            uploaded_files = upload_scripts(GDRIVE_BACKUP)
        elif choice == "4":
            file_path = input("請輸入檔案或目錄路徑: ").strip()
            src = Path(file_path)
            if upload_file_or_directory(src, GDRIVE_BACKUP):
                uploaded_files = [src]
        elif choice == "5":
            uploaded_files.extend(upload_reports(GDRIVE_BACKUP))
            uploaded_files.extend(upload_scripts(GDRIVE_BACKUP))
            uploaded_files.extend(upload_recent_files(GDRIVE_BACKUP))
        else:
            log("無效的選擇", "ERROR")
            return 1
        
        # 顯示上傳結果
        print()
        print("=" * 70)
        print("【上傳結果】")
        print("=" * 70)
        print()
        
        if uploaded_files:
            log(f"成功上傳 {len(uploaded_files)} 個檔案", "OK")
            print()
            print("上傳的檔案：")
            for f in uploaded_files[:20]:
                print(f"  ✓ {f.name}")
            if len(uploaded_files) > 20:
                print(f"  ... 還有 {len(uploaded_files) - 20} 個檔案")
        else:
            log("沒有檔案被上傳", "WARN")
        
        print()
        log(f"檔案已上傳至: {GDRIVE_BACKUP}", "OK")
        
        return 0
    
    except KeyboardInterrupt:
        print()
        log("已取消", "INFO")
        return 1
    except Exception as e:
        log(f"執行時發生錯誤: {e}", "ERROR")
        return 1


if __name__ == "__main__":
    sys.exit(main())
