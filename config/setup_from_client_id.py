#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_from_client_id.py

根據客戶端 ID 尋找並設定憑證檔案

功能：
- 根據客戶端 ID 搜尋憑證檔案
- 驗證檔案內容包含該客戶端 ID
- 自動複製並設定
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
CLIENT_ID = "581281764864-4eg0icu55pkmbcirheflhp7fgt7gk499.apps.googleusercontent.com"


def search_by_content():
    """根據內容搜尋包含客戶端 ID 的檔案"""
    print("【根據客戶端 ID 搜尋憑證檔案】")
    print(f"  客戶端 ID: {CLIENT_ID[:30]}...")
    print()
    
    search_paths = []
    
    if os.name == 'nt':  # Windows
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
    
    search_paths.append(BASE_DIR)
    search_paths.append(BASE_DIR.parent)
    
    found_files = []
    
    for search_path in search_paths:
        if not search_path.exists():
            continue
        
        print(f"  搜尋: {search_path}")
        
        # 搜尋所有 JSON 檔案
        for json_file in search_path.glob("*.json"):
            try:
                content = json_file.read_text(encoding="utf-8")
                data = json.loads(content)
                
                # 檢查是否包含客戶端 ID
                client_id_found = False
                
                if "installed" in data:
                    if data["installed"].get("client_id") == CLIENT_ID:
                        client_id_found = True
                elif "web" in data:
                    if data["web"].get("client_id") == CLIENT_ID:
                        client_id_found = True
                
                if client_id_found:
                    found_files.append(json_file)
                    print(f"    ✓ 找到: {json_file.name}")
            except:
                pass
    
    print()
    
    return found_files


def verify_and_setup(source_file: Path):
    """驗證並設定憑證檔案"""
    print(f"【驗證並設定憑證檔案】")
    print(f"  來源: {source_file}")
    print()
    
    try:
        content = json.loads(source_file.read_text(encoding="utf-8"))
        
        # 驗證客戶端 ID
        client_id_found = False
        if "installed" in content:
            if content["installed"].get("client_id") == CLIENT_ID:
                client_id_found = True
                print("  ✓ 客戶端 ID 匹配（桌面應用程式）")
                print(f"    專案 ID: {content['installed'].get('project_id', 'N/A')}")
        elif "web" in content:
            if content["web"].get("client_id") == CLIENT_ID:
                client_id_found = True
                print("  ✓ 客戶端 ID 匹配（網頁應用程式）")
                print(f"    專案 ID: {content['web'].get('project_id', 'N/A')}")
        
        if not client_id_found:
            print("  ✗ 客戶端 ID 不匹配")
            return False
        
        # 複製檔案
        if TARGET_FILE.exists():
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
        print(f"  ✗ 處理失敗: {e}")
        return False


def main():
    """主函數"""
    print("=" * 70)
    print("根據客戶端 ID 尋找並設定憑證檔案")
    print("=" * 70)
    print()
    
    # 如果目標檔案已存在且包含正確的客戶端 ID
    if TARGET_FILE.exists():
        try:
            content = json.loads(TARGET_FILE.read_text(encoding="utf-8"))
            client_id_found = False
            
            if "installed" in content:
                if content["installed"].get("client_id") == CLIENT_ID:
                    client_id_found = True
            elif "web" in content:
                if content["web"].get("client_id") == CLIENT_ID:
                    client_id_found = True
            
            if client_id_found:
                print("✓ 憑證檔案已存在且客戶端 ID 匹配")
                print(f"  位置: {TARGET_FILE}")
                print()
                print("可以直接執行授權：")
                print("  python complete_authorization_and_setup.py")
                return 0
        except:
            pass
    
    # 搜尋檔案
    found_files = search_by_content()
    
    if not found_files:
        print("✗ 未找到包含該客戶端 ID 的憑證檔案")
        print()
        print("請確認：")
        print("  1. 憑證檔案已下載到電腦")
        print("  2. 檔案是有效的 JSON 格式")
        print(f"  3. 檔案包含客戶端 ID: {CLIENT_ID[:30]}...")
        print()
        print("如果檔案在其他位置，請提供完整路徑：")
        print("  python setup_credentials_file.py \"完整路徑\\檔案名稱.json\"")
        return 1
    
    # 使用第一個找到的檔案
    if len(found_files) > 1:
        print(f"找到 {len(found_files)} 個匹配的檔案，使用第一個：")
        for i, f in enumerate(found_files[:5], 1):
            print(f"  {i}. {f}")
        print()
    
    source_file = found_files[0]
    
    # 驗證並設定
    if verify_and_setup(source_file):
        print("=" * 70)
        print("【完成】")
        print("=" * 70)
        print()
        print("✓ 憑證檔案已設定")
        print(f"  位置: {TARGET_FILE}")
        print(f"  客戶端 ID: {CLIENT_ID[:30]}...")
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
