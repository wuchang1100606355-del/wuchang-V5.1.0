#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_google_workspace_setup.py

檢查 Google Workspace 搜尋工具環境設定
"""

import sys
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")


def check_python_packages():
    """檢查 Python 套件"""
    print("=" * 70)
    print("【檢查 Python 套件】")
    print("=" * 70)
    print()
    
    required_packages = {
        "google.auth": "google-auth",
        "google_auth_oauthlib": "google-auth-oauthlib",
        "google.auth.transport.requests": "google-auth-httplib2",
        "googleapiclient": "google-api-python-client"
    }
    
    all_ok = True
    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
            log(f"{package_name} - 已安裝", "OK")
        except ImportError:
            log(f"{package_name} - 未安裝", "ERROR")
            all_ok = False
    
    print()
    return all_ok


def check_credentials_file():
    """檢查認證檔案"""
    print("=" * 70)
    print("【檢查認證檔案】")
    print("=" * 70)
    print()
    
    credentials_file = BASE_DIR / "google_credentials.json"
    token_file = BASE_DIR / "google_token.json"
    
    # 檢查憑證檔案
    if credentials_file.exists():
        log(f"憑證檔案存在: {credentials_file}", "OK")
        try:
            import json
            with open(credentials_file, 'r', encoding='utf-8') as f:
                creds = json.load(f)
                if "installed" in creds or "web" in creds:
                    log("憑證格式正確", "OK")
                    return True
                else:
                    log("憑證格式可能有問題", "WARN")
                    return False
        except Exception as e:
            log(f"讀取憑證檔案失敗: {e}", "ERROR")
            return False
    else:
        log(f"憑證檔案不存在: {credentials_file}", "ERROR")
        log("請從 Google Cloud Console 下載 OAuth 2.0 憑證", "WARN")
        return False
    
    print()


def check_token_file():
    """檢查 Token 檔案"""
    token_file = BASE_DIR / "google_token.json"
    
    if token_file.exists():
        log(f"Token 檔案存在: {token_file}", "OK")
        try:
            import json
            with open(token_file, 'r', encoding='utf-8') as f:
                token_data = json.load(f)
                if "token" in token_data or "access_token" in token_data:
                    log("Token 格式正確", "OK")
                    return True
                else:
                    log("Token 格式可能有問題", "WARN")
                    return False
        except Exception as e:
            log(f"讀取 Token 檔案失敗: {e}", "ERROR")
            return False
    else:
        log("Token 檔案不存在（首次使用時會自動建立）", "INFO")
        return True


def check_search_script():
    """檢查搜尋腳本"""
    print("=" * 70)
    print("【檢查搜尋腳本】")
    print("=" * 70)
    print()
    
    script_file = BASE_DIR / "scripts" / "search_google_workspace_files.py"
    
    if script_file.exists():
        log(f"搜尋腳本存在: {script_file}", "OK")
        return True
    else:
        log(f"搜尋腳本不存在: {script_file}", "ERROR")
        return False
    
    print()


def main():
    """主程式"""
    print("\n" + "=" * 70)
    print("Google Workspace 搜尋工具環境檢查")
    print("=" * 70)
    print()
    
    results = {
        "python_packages": False,
        "credentials": False,
        "token": False,
        "search_script": False
    }
    
    # 檢查 Python 套件
    results["python_packages"] = check_python_packages()
    
    # 檢查認證檔案
    results["credentials"] = check_credentials_file()
    
    # 檢查 Token 檔案
    results["token"] = check_token_file()
    
    # 檢查搜尋腳本
    results["search_script"] = check_search_script()
    
    # 總結
    print()
    print("=" * 70)
    print("【檢查總結】")
    print("=" * 70)
    print()
    
    all_ok = all(results.values())
    
    for name, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {name}: {'通過' if status else '失敗'}")
    
    print()
    
    if all_ok:
        log("所有檢查項目通過！可以開始使用搜尋工具", "OK")
        print("\n使用方式：")
        print("  python scripts/search_google_workspace_files.py")
    else:
        log("部分檢查項目失敗，請參考以下建議：", "WARN")
        print()
        
        if not results["python_packages"]:
            print("1. 安裝缺少的 Python 套件：")
            print("   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
            print()
        
        if not results["credentials"]:
            print("2. 建立 Google OAuth 2.0 憑證：")
            print("   - 前往 Google Cloud Console")
            print("   - 建立 OAuth 2.0 憑證（桌面應用程式）")
            print("   - 下載並儲存為 google_credentials.json")
            print("   - 詳細說明請參考：reports/GOOGLE_WORKSPACE_SEARCH_GUIDE.md")
            print()
        
        if not results["search_script"]:
            print("3. 確認搜尋腳本存在")
            print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程式已中斷")
        sys.exit(0)
    except Exception as e:
        log(f"發生錯誤: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)
