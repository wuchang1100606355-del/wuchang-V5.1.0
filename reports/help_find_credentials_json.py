#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
help_find_credentials_json.py

協助找到和下載 OAuth 憑證 JSON 檔案

功能：
- 檢查常見的下載位置
- 提供下載指引
- 協助複製檔案到正確位置
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


def search_downloads_folder():
    """搜尋常見的下載資料夾"""
    print("【步驟 1：搜尋下載資料夾】")
    print()
    
    import os
    import platform
    
    download_paths = []
    
    # Windows 常見下載位置
    if platform.system() == "Windows":
        user_profile = os.getenv("USERPROFILE", "")
        if user_profile:
            download_paths.extend([
                Path(user_profile) / "Downloads",
                Path(user_profile) / "下載",
                Path(user_profile) / "Desktop",
                Path(user_profile) / "桌面",
            ])
    
    # 搜尋 JSON 檔案
    found_files = []
    
    for download_path in download_paths:
        if download_path.exists():
            print(f"  檢查: {download_path}")
            
            # 搜尋可能的檔案名稱
            patterns = [
                "client_secret*.json",
                "*credentials*.json",
                "*oauth*.json",
                "*.json",
            ]
            
            for pattern in patterns:
                for json_file in download_path.glob(pattern):
                    try:
                        # 嘗試讀取並驗證是否為 OAuth 憑證
                        content = json.loads(json_file.read_text(encoding="utf-8"))
                        if "installed" in content or "web" in content:
                            if "client_id" in (content.get("installed", {}) or content.get("web", {})):
                                found_files.append({
                                    "path": json_file,
                                    "size": json_file.stat().st_size,
                                    "modified": json_file.stat().st_mtime,
                                })
                                print(f"    ✓ 找到可能的憑證檔案: {json_file.name}")
                    except:
                        pass
    
    print()
    
    if found_files:
        print(f"  找到 {len(found_files)} 個可能的憑證檔案：")
        for i, file_info in enumerate(found_files, 1):
            print(f"    {i}. {file_info['path'].name}")
            print(f"       路徑: {file_info['path']}")
            print(f"       大小: {file_info['size']} bytes")
        print()
        return found_files
    else:
        print("  ✗ 未在下載資料夾中找到憑證檔案")
        print()
        return []


def provide_download_guide():
    """提供下載指引"""
    print("【步驟 2：下載指引】")
    print()
    
    print("如果找不到 JSON 檔案，請按照以下步驟重新下載：")
    print()
    
    print("1. 前往 Google Cloud Console 憑證頁面")
    print("   網址: https://console.cloud.google.com/apis/credentials")
    print()
    
    print("2. 在憑證列表中，找到您建立的 OAuth 用戶端 ID")
    print("   名稱應該是：「五常系統 Google Tasks 整合」或類似")
    print()
    
    print("3. 點擊憑證名稱進入詳情頁面")
    print("   或點擊右側的下載圖示（⬇️）")
    print()
    
    print("4. 下載 JSON 檔案")
    print("   檔案名稱可能是：")
    print("   - client_secret_XXXXXX.json")
    print("   - 或類似的名稱")
    print()
    
    print("5. 確認下載位置")
    print("   通常會下載到：")
    print("   - C:\\Users\\您的使用者名稱\\Downloads")
    print("   - 或瀏覽器設定的下載資料夾")
    print()
    
    # 嘗試開啟瀏覽器
    try:
        import webbrowser
        open_browser = input("是否現在開啟 Google Cloud Console 憑證頁面？(Y/n): ").strip().lower()
        if open_browser != 'n':
            webbrowser.open("https://console.cloud.google.com/apis/credentials")
            print("✓ 已開啟瀏覽器")
    except:
        pass
    
    print()


def copy_to_project(found_files):
    """複製檔案到專案目錄"""
    print("【步驟 3：複製檔案到專案目錄】")
    print()
    
    target_file = BASE_DIR / "google_credentials.json"
    
    if target_file.exists():
        print(f"  ⚠️  目標檔案已存在: {target_file}")
        overwrite = input("是否覆蓋？(y/N): ").strip().lower()
        if overwrite != 'y':
            print("  已取消")
            return False
    
    if not found_files:
        print("  ✗ 沒有找到可用的憑證檔案")
        print()
        print("  請手動指定檔案路徑：")
        manual_path = input("  請輸入 JSON 檔案的完整路徑: ").strip().strip('"')
        
        if not manual_path:
            print("  ✗ 未提供路徑")
            return False
        
        try:
            src = Path(manual_path)
            if not src.exists():
                print(f"  ✗ 檔案不存在: {src}")
                return False
            
            # 驗證是否為有效的 OAuth 憑證
            try:
                content = json.loads(src.read_text(encoding="utf-8"))
                if "installed" not in content and "web" not in content:
                    print("  ⚠️  警告：檔案可能不是 OAuth 憑證")
                    confirm = input("  是否繼續？(y/N): ").strip().lower()
                    if confirm != 'y':
                        return False
            except json.JSONDecodeError:
                print("  ✗ 檔案不是有效的 JSON 格式")
                return False
            
            shutil.copy2(src, target_file)
            print(f"  ✓ 已複製到: {target_file}")
            return True
            
        except Exception as e:
            print(f"  ✗ 複製失敗: {e}")
            return False
    
    # 如果找到多個檔案，讓用戶選擇
    if len(found_files) > 1:
        print("  找到多個可能的憑證檔案，請選擇：")
        for i, file_info in enumerate(found_files, 1):
            print(f"    {i}. {file_info['path'].name} ({file_info['path']})")
        print()
        
        try:
            choice = int(input("  請輸入編號 (1-{}): ".format(len(found_files))))
            if 1 <= choice <= len(found_files):
                selected_file = found_files[choice - 1]["path"]
            else:
                print("  ✗ 無效的選擇")
                return False
        except (ValueError, KeyboardInterrupt):
            print("  ✗ 已取消")
            return False
    else:
        selected_file = found_files[0]["path"]
    
    try:
        shutil.copy2(selected_file, target_file)
        print(f"  ✓ 已複製: {selected_file.name} → {target_file}")
        return True
    except Exception as e:
        print(f"  ✗ 複製失敗: {e}")
        return False


def verify_credentials():
    """驗證憑證檔案"""
    print()
    print("【步驟 4：驗證憑證檔案】")
    print()
    
    credentials_file = BASE_DIR / "google_credentials.json"
    
    if not credentials_file.exists():
        print(f"  ✗ 憑證檔案不存在: {credentials_file}")
        return False
    
    try:
        content = json.loads(credentials_file.read_text(encoding="utf-8"))
        
        if "installed" in content:
            client_info = content["installed"]
            print("  ✓ 憑證檔案格式正確（桌面應用程式）")
            print(f"    客戶端 ID: {client_info.get('client_id', 'N/A')[:20]}...")
            print(f"    專案 ID: {client_info.get('project_id', 'N/A')}")
        elif "web" in content:
            client_info = content["web"]
            print("  ✓ 憑證檔案格式正確（網頁應用程式）")
            print(f"    客戶端 ID: {client_info.get('client_id', 'N/A')[:20]}...")
            print(f"    專案 ID: {client_info.get('project_id', 'N/A')}")
        else:
            print("  ✗ 憑證檔案格式不正確")
            print("    缺少 'installed' 或 'web' 欄位")
            return False
        
        print()
        print("  ✓ 憑證檔案驗證通過")
        return True
        
    except json.JSONDecodeError as e:
        print(f"  ✗ JSON 格式錯誤: {e}")
        return False
    except Exception as e:
        print(f"  ✗ 驗證失敗: {e}")
        return False


def main():
    """主函數"""
    print("=" * 70)
    print("協助找到 OAuth 憑證 JSON 檔案")
    print("=" * 70)
    print()
    
    # 步驟 1: 搜尋下載資料夾
    found_files = search_downloads_folder()
    
    # 步驟 2: 提供下載指引
    if not found_files:
        provide_download_guide()
    
    # 步驟 3: 複製檔案
    if found_files:
        copy_success = copy_to_project(found_files)
    else:
        print("【步驟 3：手動指定檔案】")
        print()
        copy_success = copy_to_project([])
    
    # 步驟 4: 驗證憑證
    if copy_success:
        verify_success = verify_credentials()
    else:
        verify_success = False
    
    # 總結
    print()
    print("=" * 70)
    print("【完成】")
    print("=" * 70)
    print()
    
    credentials_file = BASE_DIR / "google_credentials.json"
    
    if credentials_file.exists() and verify_success:
        print("✓ 憑證檔案已準備好")
        print(f"  位置: {credentials_file}")
        print()
        print("現在可以繼續執行安裝：")
        print("  python auto_setup_google_tasks.py --auto")
    else:
        print("✗ 憑證檔案未準備好")
        print()
        print("請按照上述指引下載憑證檔案，然後重新執行此腳本")
        print("或手動將憑證檔案複製到：")
        print(f"  {credentials_file}")
    
    print()
    print("=" * 70)
    
    return 0 if verify_success else 1


if __name__ == "__main__":
    sys.exit(main())
