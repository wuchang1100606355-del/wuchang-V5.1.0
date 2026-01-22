#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
quick_setup_with_client_id.py

根據客戶端 ID 快速設定憑證

功能：
- 廣泛搜尋包含客戶端 ID 的 JSON 檔案
- 自動複製並設定
- 如果找不到，提供重新下載指引
"""

import sys
import json
import shutil
import os
import webbrowser
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
CLIENT_ID_SHORT = "581281764864"


def search_all_json_files():
    """搜尋所有可能包含客戶端 ID 的 JSON 檔案"""
    print("【廣泛搜尋憑證檔案】")
    print(f"  目標客戶端 ID: {CLIENT_ID[:40]}...")
    print()
    
    search_paths = []
    
    if os.name == 'nt':  # Windows
        user_profile = os.getenv("USERPROFILE", "")
        if user_profile:
            base_path = Path(user_profile)
            # 擴展搜尋範圍
            search_paths.extend([
                base_path / "Downloads",
                base_path / "下載",
                base_path / "Desktop",
                base_path / "桌面",
                base_path / "Documents",
                base_path / "文件",
                base_path / "OneDrive",
                base_path / "OneDrive" / "Downloads",
                base_path / "OneDrive" / "下載",
            ])
    
    # 當前目錄及子目錄
    search_paths.append(BASE_DIR)
    search_paths.append(BASE_DIR.parent)
    
    found_files = []
    checked_count = 0
    
    for search_path in search_paths:
        if not search_path.exists():
            continue
        
        print(f"  搜尋: {search_path}")
        
        # 搜尋所有 JSON 檔案（包括子目錄）
        try:
            for json_file in search_path.rglob("*.json"):
                checked_count += 1
                if checked_count % 50 == 0:
                    print(f"    已檢查 {checked_count} 個檔案...")
                
                try:
                    # 快速檢查檔案大小（太小的檔案可能不是憑證）
                    if json_file.stat().st_size < 100:
                        continue
                    
                    content = json_file.read_text(encoding="utf-8", errors="ignore")
                    
                    # 檢查是否包含客戶端 ID
                    if CLIENT_ID in content or CLIENT_ID_SHORT in content:
                        # 驗證 JSON 格式
                        try:
                            data = json.loads(content)
                            # 確認是 OAuth 憑證格式
                            if "installed" in data or "web" in data:
                                found_files.append(json_file)
                                print(f"    ✓ 找到: {json_file}")
                        except:
                            pass
                except:
                    pass
        except Exception as e:
            print(f"    ⚠️  搜尋時發生錯誤: {e}")
    
    print(f"  總共檢查了 {checked_count} 個 JSON 檔案")
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
        project_id = "N/A"
        
        if "installed" in content:
            if content["installed"].get("client_id") == CLIENT_ID:
                client_id_found = True
                project_id = content["installed"].get("project_id", "N/A")
                print("  ✓ 客戶端 ID 匹配（桌面應用程式）")
        elif "web" in content:
            if content["web"].get("client_id") == CLIENT_ID:
                client_id_found = True
                project_id = content["web"].get("project_id", "N/A")
                print("  ✓ 客戶端 ID 匹配（網頁應用程式）")
        
        if not client_id_found:
            print("  ⚠️  檔案包含客戶端 ID，但格式可能不完整")
            print("  將嘗試使用此檔案...")
        
        print(f"    專案 ID: {project_id}")
        
        # 複製檔案
        if TARGET_FILE.exists():
            backup = BASE_DIR / f"google_credentials.json.backup_{int(__import__('time').time())}"
            try:
                shutil.copy2(TARGET_FILE, backup)
                print(f"  ✓ 已備份現有檔案: {backup.name}")
            except:
                pass
        
        shutil.copy2(source_file, TARGET_FILE)
        print(f"  ✓ 已複製到: {TARGET_FILE}")
        print()
        return True
        
    except Exception as e:
        print(f"  ✗ 處理失敗: {e}")
        return False


def provide_download_guide():
    """提供下載指引"""
    print("【未找到憑證檔案，提供下載指引】")
    print()
    
    print("請按照以下步驟重新下載憑證檔案：")
    print()
    print("1. 前往 Google Cloud Console 憑證頁面")
    print("   網址: https://console.cloud.google.com/apis/credentials")
    print()
    
    print("2. 找到客戶端 ID 為以下內容的憑證：")
    print(f"   {CLIENT_ID}")
    print()
    
    print("3. 點擊下載圖示（⬇️）或進入詳情頁面下載")
    print()
    
    print("4. 下載後，檔案名稱應該是：")
    print(f"   client_secret_{CLIENT_ID_SHORT}-*.json")
    print()
    
    # 嘗試開啟瀏覽器
    try:
        open_browser = input("是否現在開啟 Google Cloud Console 憑證頁面？(Y/n): ").strip().lower()
        if open_browser != 'n':
            webbrowser.open("https://console.cloud.google.com/apis/credentials")
            print("✓ 已開啟瀏覽器")
    except (EOFError, KeyboardInterrupt):
        print("⚠️  非互動模式，請手動開啟瀏覽器")
    
    print()
    print("5. 下載完成後，重新執行此腳本：")
    print("   python quick_setup_with_client_id.py")
    print()


def main():
    """主函數"""
    print("=" * 70)
    print("根據客戶端 ID 快速設定憑證")
    print("=" * 70)
    print()
    print(f"客戶端 ID: {CLIENT_ID}")
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
    
    # 廣泛搜尋
    print("正在搜尋憑證檔案（這可能需要一些時間）...")
    print()
    found_files = search_all_json_files()
    
    if not found_files:
        print("✗ 未找到包含該客戶端 ID 的憑證檔案")
        print()
        provide_download_guide()
        return 1
    
    # 如果找到多個，使用第一個
    if len(found_files) > 1:
        print(f"找到 {len(found_files)} 個可能的檔案，使用第一個：")
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
        print(f"  客戶端 ID: {CLIENT_ID[:40]}...")
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
