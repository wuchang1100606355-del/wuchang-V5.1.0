#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_setup_google_tasks.py

自動設定 Google Tasks API

功能：
- 檢查現有設定
- 引導完成 OAuth 憑證設定
- 自動處理授權流程
- 驗證設定是否成功
"""

import sys
import json
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


def check_dependencies(auto_install: bool = False):
    """檢查必要的套件"""
    print("【步驟 1：檢查依賴套件】")
    
    required_packages = {
        "google-auth": "google-auth",
        "google-auth-oauthlib": "google-auth-oauthlib",
        "google-auth-httplib2": "google-auth-httplib2",
        "google-api-python-client": "google-api-python-client",
    }
    
    missing_packages = []
    
    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name.replace("-", "_"))
            print(f"  ✓ {package_name} 已安裝")
        except ImportError:
            print(f"  ✗ {package_name} 未安裝")
            missing_packages.append(package_name)
    
    if missing_packages:
        print()
        print("  需要安裝以下套件：")
        print(f"    pip install {' '.join(missing_packages)}")
        print()
        
        if auto_install:
            install = 'y'
        else:
            try:
                install = input("是否現在安裝？(y/N): ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\n⚠️  非互動模式，跳過安裝")
                print("請手動執行: pip install " + " ".join(missing_packages))
                return False
        
        if install == 'y':
            import subprocess
            try:
                print("正在安裝套件...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install"] + missing_packages,
                    check=False,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print("✓ 套件安裝完成")
                    return True
                else:
                    print(f"✗ 安裝失敗:")
                    print(result.stderr)
                    return False
            except Exception as e:
                print(f"✗ 安裝失敗: {e}")
                return False
        else:
            return False
    
    print()
    return True


def check_credentials():
    """檢查 OAuth 憑證檔案"""
    print("【步驟 2：檢查 OAuth 憑證】")
    
    credentials_file = BASE_DIR / "google_credentials.json"
    
    if credentials_file.exists():
        try:
            creds = json.loads(credentials_file.read_text(encoding="utf-8"))
            if creds.get("installed") or creds.get("web"):
                print(f"  ✓ 找到憑證檔案: {credentials_file}")
                print(f"    類型: {'桌面應用程式' if creds.get('installed') else '網頁應用程式'}")
                return True
            else:
                print(f"  ⚠️  憑證檔案格式不正確")
                return False
        except Exception as e:
            print(f"  ✗ 讀取憑證檔案失敗: {e}")
            return False
    else:
        print(f"  ✗ 未找到憑證檔案: {credentials_file}")
        return False


def guide_credential_setup(auto_mode: bool = False):
    """引導用戶完成憑證設定"""
    print()
    print("=" * 70)
    print("OAuth 憑證設定指南")
    print("=" * 70)
    print()
    print("請按照以下步驟操作：")
    print()
    
    credentials_file = BASE_DIR / "google_credentials.json"
    
    # 步驟 1: 開啟 Google Cloud Console
    print("1. 開啟 Google Cloud Console")
    print("   網址: https://console.cloud.google.com/")
    print()
    
    if auto_mode:
        try:
            webbrowser.open("https://console.cloud.google.com/")
            print("✓ 已自動開啟瀏覽器")
        except:
            print("⚠️  無法自動開啟瀏覽器，請手動訪問")
    else:
        try:
            open_browser = input("是否現在開啟 Google Cloud Console？(Y/n): ").strip().lower()
            if open_browser != 'n':
                try:
                    webbrowser.open("https://console.cloud.google.com/")
                    print("✓ 已開啟瀏覽器")
                except:
                    print("⚠️  無法自動開啟瀏覽器，請手動訪問")
        except (EOFError, KeyboardInterrupt):
            print("⚠️  非互動模式，請手動開啟瀏覽器")
    
    print()
    print("2. 建立或選擇專案")
    print("   - 點擊頂部專案選擇器")
    print("   - 建立新專案或選擇現有專案")
    print()
    
    if not auto_mode:
        try:
            input("完成後按 Enter 繼續...")
        except (EOFError, KeyboardInterrupt):
            pass
    else:
        import time
        print("⏳ 等待 5 秒後繼續...")
        time.sleep(5)
    print()
    
    # 步驟 3: 啟用 API
    print("3. 啟用 Google Tasks API")
    print("   - 前往「API 和服務」→「程式庫」")
    print("   - 搜尋「Google Tasks API」")
    print("   - 點擊「啟用」")
    print()
    
    if auto_mode:
        try:
            webbrowser.open("https://console.cloud.google.com/apis/library/tasks.googleapis.com")
            print("✓ 已自動開啟 API 程式庫頁面")
        except:
            print("⚠️  無法自動開啟瀏覽器")
    else:
        try:
            open_api = input("是否現在開啟 API 程式庫？(Y/n): ").strip().lower()
            if open_api != 'n':
                try:
                    webbrowser.open("https://console.cloud.google.com/apis/library/tasks.googleapis.com")
                    print("✓ 已開啟瀏覽器")
                except:
                    print("⚠️  無法自動開啟瀏覽器")
        except (EOFError, KeyboardInterrupt):
            pass
    
    print()
    if not auto_mode:
        try:
            input("完成後按 Enter 繼續...")
        except (EOFError, KeyboardInterrupt):
            pass
    else:
        import time
        print("⏳ 等待 5 秒後繼續...")
        time.sleep(5)
    print()
    
    # 步驟 4: 建立憑證
    print("4. 建立 OAuth 2.0 憑證")
    print("   - 前往「API 和服務」→「憑證」")
    print("   - 點擊「建立憑證」→「OAuth 用戶端 ID」")
    print("   - 如果首次使用，需要先設定 OAuth 同意畫面")
    print("   - 應用程式類型選擇「桌面應用程式」")
    print("   - 名稱可以自訂（例如：Wuchang Tasks Client）")
    print("   - 點擊「建立」")
    print()
    
    if auto_mode:
        try:
            webbrowser.open("https://console.cloud.google.com/apis/credentials")
            print("✓ 已自動開啟憑證頁面")
        except:
            print("⚠️  無法自動開啟瀏覽器")
    else:
        try:
            open_credentials = input("是否現在開啟憑證頁面？(Y/n): ").strip().lower()
            if open_credentials != 'n':
                try:
                    webbrowser.open("https://console.cloud.google.com/apis/credentials")
                    print("✓ 已開啟瀏覽器")
                except:
                    print("⚠️  無法自動開啟瀏覽器")
        except (EOFError, KeyboardInterrupt):
            pass
    
    print()
    if not auto_mode:
        try:
            input("完成後按 Enter 繼續...")
        except (EOFError, KeyboardInterrupt):
            pass
    else:
        import time
        print("⏳ 等待 5 秒後繼續...")
        time.sleep(5)
    print()
    
    # 步驟 5-6: 下載和儲存
    print("5. 下載憑證")
    print("   - 在憑證列表中，找到剛建立的 OAuth 用戶端 ID")
    print("   - 點擊下載圖示（⬇️）或點擊憑證名稱")
    print("   - 下載 JSON 檔案")
    print()
    
    print("6. 儲存憑證檔案")
    print(f"   - 將下載的 JSON 檔案重新命名為: google_credentials.json")
    print(f"   - 放置在專案根目錄: {BASE_DIR}")
    print()
    
    if auto_mode:
        print("⏳ 等待您完成憑證下載和放置...")
        print("   將每 3 秒檢查一次憑證檔案是否存在")
        print()
        
        import time
        max_wait = 300  # 最多等待 5 分鐘
        waited = 0
        while waited < max_wait:
            if credentials_file.exists():
                print("✓ 檢測到憑證檔案")
                return True
            time.sleep(3)
            waited += 3
            if waited % 15 == 0:
                print(f"   已等待 {waited} 秒...")
        
        print("⚠️  等待超時，未檢測到憑證檔案")
        return False
    else:
        try:
            input("完成後按 Enter 繼續...")
        except (EOFError, KeyboardInterrupt):
            pass
        print()
        
        # 檢查是否已放置檔案
        if credentials_file.exists():
            print("✓ 檢測到憑證檔案")
            return True
        else:
            print("⚠️  尚未檢測到憑證檔案")
            try:
                manual_path = input("如果檔案在其他位置，請輸入完整路徑（或按 Enter 跳過）: ").strip()
                if manual_path:
                    try:
                        src = Path(manual_path)
                        if src.exists():
                            import shutil
                            shutil.copy2(src, credentials_file)
                            print(f"✓ 已複製憑證檔案到: {credentials_file}")
                            return True
                        else:
                            print(f"✗ 檔案不存在: {manual_path}")
                    except Exception as e:
                        print(f"✗ 複製失敗: {e}")
            except (EOFError, KeyboardInterrupt):
                pass
            
            return False


def test_authorization():
    """測試授權"""
    print()
    print("【步驟 3：測試授權】")
    
    try:
        from google_tasks_integration import get_google_tasks_integration
        
        print("  正在初始化 Google Tasks 整合...")
        integration = get_google_tasks_integration()
        
        print("  正在獲取任務列表...")
        task_lists = integration.list_task_lists()
        
        if task_lists:
            print(f"  ✓ 授權成功！找到 {len(task_lists)} 個任務列表")
            for task_list in task_lists[:5]:  # 只顯示前 5 個
                print(f"    - {task_list.title} (ID: {task_list.id})")
            if len(task_lists) > 5:
                print(f"    ... 還有 {len(task_lists) - 5} 個任務列表")
            return True
        else:
            print("  ⚠️  授權成功，但沒有找到任務列表")
            return True
            
    except FileNotFoundError as e:
        print(f"  ✗ 憑證檔案問題: {e}")
        return False
    except Exception as e:
        print(f"  ✗ 授權失敗: {e}")
        return False


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Google Tasks API 自動設定")
    parser.add_argument("--auto", "--yes", "-y", action="store_true", dest="auto", help="全自動模式（自動安裝套件）")
    parser.add_argument("--skip-install", action="store_true", help="跳過套件安裝步驟")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Google Tasks API 自動設定")
    if args.auto:
        print("（全自動模式）")
    print("=" * 70)
    print()
    
    # 步驟 1: 檢查依賴
    if not args.skip_install:
        if not check_dependencies(auto_install=args.auto):
            if args.auto:
                print()
                print("⚠️  自動安裝失敗，請手動執行:")
                print("   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
                return 1
            else:
                print()
                print("✗ 依賴套件未安裝，請先安裝後再執行")
                return 1
    
    # 步驟 2: 檢查憑證
    has_credentials = check_credentials()
    
    if not has_credentials:
        print()
        print("需要設定 OAuth 憑證")
        if guide_credential_setup(auto_mode=args.auto):
            print()
            print("✓ 憑證檔案已準備好")
        else:
            print()
            print("✗ 憑證設定未完成")
            print()
            print("請手動完成以下步驟：")
            print("1. 從 Google Cloud Console 下載 OAuth 憑證")
            print(f"2. 儲存為: {BASE_DIR / 'google_credentials.json'}")
            if args.auto:
                print("3. 重新執行此腳本（或等待自動檢測）")
            else:
                print("3. 重新執行此腳本")
            return 1
    
    # 步驟 3: 測試授權
    if test_authorization():
        print()
        print("=" * 70)
        print("【設定完成】")
        print("=" * 70)
        print()
        print("✓ Google Tasks API 已成功設定")
        print()
        print("現在可以使用以下工具：")
        print("  - python get_jules_task_direct.py <task_url>")
        print("  - python upload_diff_to_jules.py --auto-upload")
        print("  - python sync_from_google_task.py <task_url> <target_file>")
        print()
        return 0
    else:
        print()
        print("=" * 70)
        print("【設定未完成】")
        print("=" * 70)
        print()
        print("請檢查：")
        print("1. 憑證檔案是否正確")
        print("2. Google Tasks API 是否已啟用")
        print("3. OAuth 同意畫面是否已設定")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
