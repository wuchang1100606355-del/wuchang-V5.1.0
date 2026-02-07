#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_credentials_from_console.py

從 Google Cloud Console 下載憑證的指引

根據您提供的截圖，協助完成憑證下載和設定
"""

import sys
import json
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
CLIENT_ID = "581281764864-2a3285kidmm2rj7jmrl9ve7cqfvid32d.apps.googleusercontent.com"
PROJECT_ID = "wuchang-sbir-project"


def provide_download_instructions():
    """提供下載指引"""
    print("=" * 70)
    print("從 Google Cloud Console 下載憑證檔案")
    print("=" * 70)
    print()
    print("根據您提供的截圖，以下是下載步驟：")
    print()
    print("【方式 1：從憑證列表頁面下載（推薦）】")
    print()
    print("1. 在當前頁面，點擊左側導航欄的「憑證」")
    print("   或前往：https://console.cloud.google.com/apis/credentials")
    print()
    print("2. 在憑證列表中，找到您的 OAuth 用戶端 ID：")
    print(f"   名稱: Wuchang-life")
    print(f"   客戶端 ID: {CLIENT_ID[:40]}...")
    print()
    print("3. 點擊該憑證右側的「下載圖示（⬇️）」")
    print("   這會下載完整的 OAuth 憑證 JSON 檔案")
    print()
    print("4. 下載的檔案名稱應該是：")
    print(f"   client_secret_{CLIENT_ID.split('-')[0]}-*.json")
    print()
    
    # 開啟瀏覽器
    try:
        open_browser = input("是否現在開啟憑證列表頁面？(Y/n): ").strip().lower()
        if open_browser != 'n':
            webbrowser.open(f"https://console.cloud.google.com/apis/credentials?project={PROJECT_ID}")
            print("✓ 已開啟瀏覽器")
    except (EOFError, KeyboardInterrupt):
        print("⚠️  非互動模式")
    
    print()
    print("【方式 2：如果找不到下載按鈕】")
    print()
    print("1. 在憑證列表中，點擊憑證名稱進入詳情頁面")
    print("2. 在詳情頁面中，尋找「下載 JSON」或類似的按鈕")
    print("3. 點擊下載")
    print()
    print("【下載後】")
    print()
    print("1. 檔案通常會下載到：")
    print("   C:\\Users\\您的使用者名稱\\Downloads")
    print()
    print("2. 將檔案複製到專案目錄並重新命名：")
    print(f"   目標: {TARGET_FILE}")
    print()
    print("3. 執行以下命令（如果檔案在下載資料夾）：")
    print('   Copy-Item "$env:USERPROFILE\\Downloads\\client_secret_*.json" "C:\\wuchang V5.1.0\\wuchang-V5.1.0\\google_credentials.json"')
    print()
    print("4. 或使用 Python 腳本：")
    print("   python setup_credentials_file.py \"完整路徑\\檔案名稱.json\"")
    print()


def check_downloaded_file():
    """檢查是否已下載檔案"""
    import os
    
    print("【檢查下載的檔案】")
    print()
    
    download_paths = []
    
    if os.name == 'nt':  # Windows
        user_profile = os.getenv("USERPROFILE", "")
        if user_profile:
            base_path = Path(user_profile)
            download_paths.extend([
                base_path / "Downloads",
                base_path / "下載",
            ])
    
    found_files = []
    
    for download_path in download_paths:
        if not download_path.exists():
            continue
        
        # 搜尋包含客戶端 ID 的檔案
        for json_file in download_path.glob("client_secret*.json"):
            try:
                content = json_file.read_text(encoding="utf-8", errors="ignore")
                if CLIENT_ID in content or "581281764864" in content:
                    found_files.append(json_file)
                    print(f"  ✓ 找到: {json_file.name}")
                    print(f"    位置: {json_file}")
            except:
                pass
    
    if found_files:
        print()
        print(f"找到 {len(found_files)} 個可能的憑證檔案")
        return found_files
    else:
        print("  ✗ 未在下載資料夾中找到憑證檔案")
        print()
        return []


def auto_setup_from_downloads():
    """自動從下載資料夾設定"""
    found_files = check_downloaded_file()
    
    if not found_files:
        return False
    
    # 使用最新的檔案
    latest_file = max(found_files, key=lambda p: p.stat().st_mtime)
    
    print(f"使用最新檔案: {latest_file.name}")
    print()
    
    # 驗證並複製
    try:
        import shutil
        content = json.loads(latest_file.read_text(encoding="utf-8"))
        
        if "installed" in content or "web" in content:
            if TARGET_FILE.exists():
                backup = BASE_DIR / f"google_credentials.json.backup_{int(__import__('time').time())}"
                try:
                    shutil.copy2(TARGET_FILE, backup)
                except:
                    pass
            
            shutil.copy2(latest_file, TARGET_FILE)
            print(f"✓ 已複製到: {TARGET_FILE}")
            return True
    except Exception as e:
        print(f"✗ 設定失敗: {e}")
        return False
    
    return False


def main():
    """主函數"""
    print("=" * 70)
    print("從 Google Cloud Console 下載憑證")
    print("=" * 70)
    print()
    print(f"專案: {PROJECT_ID}")
    print(f"客戶端 ID: {CLIENT_ID}")
    print()
    
    # 檢查是否已有檔案
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
    
    # 檢查下載資料夾
    if auto_setup_from_downloads():
        print()
        print("=" * 70)
        print("【完成】")
        print("=" * 70)
        print()
        print("✓ 憑證檔案已自動設定")
        print()
        print("現在可以執行完整授權：")
        print("  python complete_authorization_and_setup.py")
        return 0
    
    # 提供下載指引
    provide_download_instructions()
    
    print("=" * 70)
    print()
    print("下載完成後，可以：")
    print("  1. 重新執行此腳本自動設定")
    print("  2. 或手動複製檔案到專案目錄")
    print()
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
