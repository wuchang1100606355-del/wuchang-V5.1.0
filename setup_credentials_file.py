#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_credentials_file.py

設定 OAuth 憑證檔案

功能：
- 從下載資料夾找到憑證檔案
- 驗證檔案格式
- 複製到專案目錄並重新命名
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
TARGET_FILE = BASE_DIR / "google_credentials.json"


def find_credentials_file(filename: str):
    """尋找憑證檔案"""
    print("【步驟 1：尋找憑證檔案】")
    print(f"  檔案名稱: {filename}")
    print()
    
    import os
    
    # 常見的下載位置
    search_paths = []
    
    if os.name == 'nt':  # Windows
        user_profile = os.getenv("USERPROFILE", "")
        if user_profile:
            search_paths.extend([
                Path(user_profile) / "Downloads",
                Path(user_profile) / "下載",
                Path(user_profile) / "Desktop",
                Path(user_profile) / "桌面",
                Path(user_profile) / "Documents",
                Path(user_profile) / "文件",
            ])
    
    # 也在當前目錄搜尋
    search_paths.append(BASE_DIR)
    
    found_files = []
    
    for search_path in search_paths:
        if not search_path.exists():
            continue
        
        # 精確匹配
        exact_match = search_path / filename
        if exact_match.exists():
            found_files.append(exact_match)
            print(f"  ✓ 找到: {exact_match}")
            continue
        
        # 模糊匹配（不區分大小寫）
        for file_path in search_path.glob("*.json"):
            if filename.lower() in file_path.name.lower():
                found_files.append(file_path)
                print(f"  ✓ 找到類似檔案: {file_path}")
    
    print()
    
    if not found_files:
        print("  ✗ 未找到檔案")
        print()
        print("  請確認檔案位置，或提供完整路徑")
        return None
    
    if len(found_files) == 1:
        return found_files[0]
    else:
        print(f"  找到 {len(found_files)} 個可能的檔案：")
        for i, file_path in enumerate(found_files, 1):
            print(f"    {i}. {file_path}")
        print()
        
        try:
            choice = int(input("  請選擇檔案編號 (1-{}): ".format(len(found_files))))
            if 1 <= choice <= len(found_files):
                return found_files[choice - 1]
            else:
                print("  ✗ 無效的選擇")
                return None
        except (ValueError, KeyboardInterrupt, EOFError):
            # 非互動模式，返回第一個
            print("  非互動模式，使用第一個找到的檔案")
            return found_files[0]


def verify_credentials_file(file_path: Path):
    """驗證憑證檔案格式"""
    print("【步驟 2：驗證憑證檔案】")
    print(f"  檔案: {file_path}")
    print()
    
    try:
        content = json.loads(file_path.read_text(encoding="utf-8"))
        
        if "installed" in content:
            client_info = content["installed"]
            print("  ✓ 憑證檔案格式正確（桌面應用程式）")
            print(f"    客戶端 ID: {client_info.get('client_id', 'N/A')[:30]}...")
            print(f"    專案 ID: {client_info.get('project_id', 'N/A')}")
            print(f"    認證 URI: {client_info.get('auth_uri', 'N/A')}")
            return True
        elif "web" in content:
            client_info = content["web"]
            print("  ✓ 憑證檔案格式正確（網頁應用程式）")
            print(f"    客戶端 ID: {client_info.get('client_id', 'N/A')[:30]}...")
            print(f"    專案 ID: {client_info.get('project_id', 'N/A')}")
            return True
        else:
            print("  ✗ 憑證檔案格式不正確")
            print("    缺少 'installed' 或 'web' 欄位")
            print()
            print("  檔案內容預覽：")
            print(f"    {list(content.keys())[:5]}")
            return False
            
    except json.JSONDecodeError as e:
        print(f"  ✗ JSON 格式錯誤: {e}")
        return False
    except Exception as e:
        print(f"  ✗ 讀取檔案失敗: {e}")
        return False


def copy_credentials_file(source_file: Path):
    """複製憑證檔案到專案目錄"""
    print()
    print("【步驟 3：複製憑證檔案】")
    print()
    
    if TARGET_FILE.exists():
        print(f"  ⚠️  目標檔案已存在: {TARGET_FILE}")
        print()
        
        # 備份現有檔案
        backup_file = BASE_DIR / f"google_credentials.json.backup_{int(__import__('time').time())}"
        try:
            shutil.copy2(TARGET_FILE, backup_file)
            print(f"  ✓ 已備份現有檔案到: {backup_file.name}")
        except Exception as e:
            print(f"  ⚠️  備份失敗: {e}")
        
        print()
        
        try:
            overwrite = input("  是否覆蓋現有檔案？(y/N): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            overwrite = 'y'  # 非互動模式，預設覆蓋
        
        if overwrite != 'y':
            print("  已取消")
            return False
    
    try:
        shutil.copy2(source_file, TARGET_FILE)
        print(f"  ✓ 已複製: {source_file.name} → {TARGET_FILE.name}")
        print(f"  ✓ 目標位置: {TARGET_FILE}")
        return True
    except Exception as e:
        print(f"  ✗ 複製失敗: {e}")
        return False


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="設定 OAuth 憑證檔案")
    parser.add_argument("filename", nargs="?", default="client_secret_581281764864-4eg0icu55pkmbcirheflhp7fgt7gk499.apps.googleusercontent.com.json", help="憑證檔案名稱或完整路徑")
    parser.add_argument("--auto", action="store_true", help="自動模式（不詢問）")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("設定 OAuth 憑證檔案")
    print("=" * 70)
    print()
    
    # 步驟 1: 尋找檔案
    source_file = None
    
    # 如果提供的是完整路徑
    if Path(args.filename).is_absolute() or "/" in args.filename or "\\" in args.filename:
        source_file = Path(args.filename)
        if not source_file.exists():
            print(f"✗ 檔案不存在: {source_file}")
            return 1
    else:
        source_file = find_credentials_file(args.filename)
        if not source_file:
            print()
            print("請提供檔案的完整路徑：")
            print("  python setup_credentials_file.py \"完整路徑\\檔案名稱.json\"")
            return 1
    
    # 步驟 2: 驗證檔案
    if not verify_credentials_file(source_file):
        print()
        print("✗ 憑證檔案驗證失敗")
        return 1
    
    # 步驟 3: 複製檔案
    if args.auto:
        # 自動模式，直接覆蓋
        if TARGET_FILE.exists():
            backup_file = BASE_DIR / f"google_credentials.json.backup_{int(__import__('time').time())}"
            try:
                shutil.copy2(TARGET_FILE, backup_file)
            except:
                pass
    
    if not copy_credentials_file(source_file):
        return 1
    
    # 最終驗證
    print()
    print("【步驟 4：最終驗證】")
    if verify_credentials_file(TARGET_FILE):
        print()
        print("=" * 70)
        print("【完成】")
        print("=" * 70)
        print()
        print("✓ 憑證檔案已成功設定")
        print(f"  位置: {TARGET_FILE}")
        print()
        print("現在可以繼續執行安裝：")
        print("  python auto_setup_google_tasks.py --auto")
        print()
        print("=" * 70)
        return 0
    else:
        print()
        print("✗ 最終驗證失敗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
