#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
find_and_setup_credentials_now.py

立即尋找並設定憑證檔案

功能：
- 廣泛搜尋憑證檔案
- 自動複製並重新命名
- 驗證檔案格式
"""

import sys
import json
import shutil
import os
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
TARGET_FILE = BASE_DIR / "google_credentials.json"
CREDENTIAL_PATTERNS = [
    "client_secret_581281764864-4eg0icu55pkmbcirheflhp7fgt7gk499.apps.googleusercontent.com.json",
    "client_secret_581281764864*.json",
    "*client_secret*.json",
    "*credentials*.json",
]


def search_extensively():
    """廣泛搜尋憑證檔案"""
    print("【廣泛搜尋憑證檔案】")
    print()
    
    search_paths = []
    
    # Windows 常見位置
    if os.name == 'nt':
        user_profile = os.getenv("USERPROFILE", "")
        if user_profile:
            base_path = Path(user_profile)
            search_paths.extend([
                base_path / "Downloads",
                base_path / "下載",
                base_path / "Desktop",
                base_path / "桌面",
                base_path / "Documents",
                base_path / "文件",
                base_path / "OneDrive" / "Downloads",
                base_path / "OneDrive" / "下載",
            ])
    
    # 當前目錄
    search_paths.append(BASE_DIR)
    
    # 父目錄
    search_paths.append(BASE_DIR.parent)
    
    found_files = []
    
    for search_path in search_paths:
        if not search_path.exists():
            continue
        
        print(f"  搜尋: {search_path}")
        
        # 搜尋各種模式
        for pattern in CREDENTIAL_PATTERNS:
            try:
                if "*" in pattern:
                    for file_path in search_path.glob(pattern):
                        if file_path.is_file():
                            found_files.append(file_path)
                            print(f"    ✓ 找到: {file_path.name}")
                else:
                    file_path = search_path / pattern
                    if file_path.exists():
                        found_files.append(file_path)
                        print(f"    ✓ 找到: {file_path.name}")
            except:
                pass
    
    print()
    
    if found_files:
        # 去重
        unique_files = []
        seen = set()
        for f in found_files:
            if f not in seen:
                unique_files.append(f)
                seen.add(f)
        
        return unique_files
    else:
        return []


def verify_and_copy(source_file: Path):
    """驗證並複製檔案"""
    print(f"【驗證並複製檔案】")
    print(f"  來源: {source_file}")
    print()
    
    # 驗證格式
    try:
        content = json.loads(source_file.read_text(encoding="utf-8"))
        if "installed" in content:
            print("  ✓ 檔案格式正確（桌面應用程式）")
            client_id = content["installed"].get("client_id", "")[:30]
            print(f"    客戶端 ID: {client_id}...")
        elif "web" in content:
            print("  ✓ 檔案格式正確（網頁應用程式）")
            client_id = content["web"].get("client_id", "")[:30]
            print(f"    客戶端 ID: {client_id}...")
        else:
            print("  ✗ 檔案格式不正確")
            return False
    except Exception as e:
        print(f"  ✗ 驗證失敗: {e}")
        return False
    
    # 複製檔案
    try:
        if TARGET_FILE.exists():
            # 備份
            backup = BASE_DIR / f"google_credentials.json.backup_{int(__import__('time').time())}"
            try:
                shutil.copy2(TARGET_FILE, backup)
                print(f"  ✓ 已備份現有檔案")
            except:
                pass
        
        shutil.copy2(source_file, TARGET_FILE)
        print(f"  ✓ 已複製到: {TARGET_FILE}")
        print()
        return True
    except Exception as e:
        print(f"  ✗ 複製失敗: {e}")
        return False


def main():
    """主函數"""
    print("=" * 70)
    print("立即尋找並設定憑證檔案")
    print("=" * 70)
    print()
    
    # 如果目標檔案已存在且正確
    if TARGET_FILE.exists():
        try:
            content = json.loads(TARGET_FILE.read_text(encoding="utf-8"))
            if "installed" in content or "web" in content:
                print("✓ 憑證檔案已存在且格式正確")
                print(f"  位置: {TARGET_FILE}")
                print()
                print("可以直接執行授權：")
                print("  python complete_authorization_and_setup.py")
                return 0
        except:
            pass
    
    # 廣泛搜尋
    found_files = search_extensively()
    
    if not found_files:
        print("✗ 未找到憑證檔案")
        print()
        print("請確認：")
        print("  1. 檔案已下載到電腦")
        print("  2. 檔案名稱包含: client_secret_581281764864")
        print()
        print("如果檔案在其他位置，請提供完整路徑：")
        print("  python setup_credentials_file.py \"完整路徑\\檔案名稱.json\"")
        return 1
    
    # 如果找到多個，選擇第一個
    if len(found_files) > 1:
        print(f"找到 {len(found_files)} 個可能的檔案，使用第一個：")
        for i, f in enumerate(found_files[:5], 1):
            print(f"  {i}. {f}")
        print()
    
    source_file = found_files[0]
    
    # 驗證並複製
    if verify_and_copy(source_file):
        print("=" * 70)
        print("【完成】")
        print("=" * 70)
        print()
        print("✓ 憑證檔案已設定")
        print(f"  位置: {TARGET_FILE}")
        print()
        print("現在可以執行完整授權：")
        print("  python complete_authorization_and_setup.py")
        print()
        return 0
    else:
        print("=" * 70)
        print("【失敗】")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
