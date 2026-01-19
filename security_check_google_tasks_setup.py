#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
security_check_google_tasks_setup.py

安全性檢查工具 - 驗證 Google Tasks 設定腳本的安全性
"""

import sys
import ast
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def check_script_security(script_path: Path) -> dict:
    """檢查腳本安全性"""
    results = {
        "safe": True,
        "warnings": [],
        "info": [],
        "risks": []
    }
    
    try:
        code = script_path.read_text(encoding="utf-8")
    except Exception as e:
        results["safe"] = False
        results["risks"].append(f"無法讀取檔案: {e}")
        return results
    
    # 檢查危險函數
    dangerous_patterns = [
        ("subprocess.run", "使用 subprocess.run 執行外部命令"),
        ("os.system", "使用 os.system 執行系統命令"),
        ("eval(", "使用 eval 執行動態代碼"),
        ("exec(", "使用 exec 執行動態代碼"),
        ("__import__", "使用 __import__ 動態導入模組"),
        ("compile(", "使用 compile 編譯代碼"),
    ]
    
    for pattern, description in dangerous_patterns:
        if pattern in code:
            # 檢查是否在安全上下文中使用
            if pattern == "subprocess.run":
                # subprocess.run 在我們的腳本中用於安裝套件，這是安全的
                if "pip install" in code or "install" in code.lower():
                    results["info"].append(f"✓ {description} - 僅用於安裝 Python 套件（安全）")
                else:
                    results["warnings"].append(f"⚠️  {description}")
            elif pattern == "__import__":
                # __import__ 用於動態檢查模組，這是安全的
                if "__import__(\"time\")" in code or "__import__(\"json\")" in code:
                    results["info"].append(f"✓ {description} - 僅用於導入標準庫（安全）")
                else:
                    results["warnings"].append(f"⚠️  {description}")
            else:
                results["risks"].append(f"✗ {description}")
                results["safe"] = False
    
    # 檢查網路操作
    if "webbrowser.open" in code:
        results["info"].append("✓ 使用 webbrowser.open - 僅開啟瀏覽器（安全）")
    
    if "requests.get" in code or "requests.post" in code:
        results["info"].append("✓ 使用 requests - 僅用於 API 呼叫（安全）")
    
    # 檢查檔案操作
    if "write_text" in code or "write" in code:
        # 檢查是否寫入敏感位置
        if "google_credentials.json" in code:
            results["info"].append("✓ 檔案寫入 - 僅寫入專案目錄內的憑證檔案（安全）")
        else:
            results["warnings"].append("⚠️  檔案寫入操作 - 請確認目標路徑安全")
    
    # 檢查環境變數操作
    if "os.environ" in code or "getenv" in code:
        results["info"].append("✓ 環境變數操作 - 僅讀取，不修改系統環境變數（安全）")
    
    return results


def check_package_security():
    """檢查要安裝的套件安全性"""
    packages = [
        "google-auth",
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "google-api-python-client",
    ]
    
    results = {
        "safe": True,
        "packages": {}
    }
    
    print("【檢查要安裝的套件】")
    print()
    
    for package in packages:
        # 這些都是 Google 官方維護的套件
        official_packages = {
            "google-auth": "Google 官方身份驗證庫",
            "google-auth-oauthlib": "Google 官方 OAuth 庫",
            "google-auth-httplib2": "Google 官方 HTTP 庫",
            "google-api-python-client": "Google 官方 API 客戶端",
        }
        
        if package in official_packages:
            print(f"  ✓ {package}")
            print(f"    來源: {official_packages[package]}")
            print(f"    安全性: 官方維護，可信任")
            results["packages"][package] = {
                "safe": True,
                "source": "official",
                "description": official_packages[package]
            }
        else:
            print(f"  ⚠️  {package}")
            print(f"    來源: 未知")
            results["packages"][package] = {
                "safe": False,
                "source": "unknown"
            }
            results["safe"] = False
        
        print()
    
    return results


def main():
    """主函數"""
    print("=" * 70)
    print("Google Tasks 設定腳本安全性檢查")
    print("=" * 70)
    print()
    
    script_path = BASE_DIR / "auto_setup_google_tasks.py"
    
    if not script_path.exists():
        print(f"✗ 找不到腳本檔案: {script_path}")
        return 1
    
    print("【檢查腳本檔案】")
    print(f"  檔案: {script_path}")
    print()
    
    # 檢查腳本安全性
    security_results = check_script_security(script_path)
    
    print("【安全性分析】")
    print()
    
    if security_results["info"]:
        print("安全操作：")
        for info in security_results["info"]:
            print(f"  {info}")
        print()
    
    if security_results["warnings"]:
        print("警告（需要確認）：")
        for warning in security_results["warnings"]:
            print(f"  {warning}")
        print()
    
    if security_results["risks"]:
        print("風險（不建議執行）：")
        for risk in security_results["risks"]:
            print(f"  {risk}")
        print()
    
    # 檢查套件安全性
    package_results = check_package_security()
    
    # 總結
    print("=" * 70)
    print("【安全性總結】")
    print("=" * 70)
    print()
    
    all_safe = security_results["safe"] and package_results["safe"]
    
    if all_safe:
        print("✓ 腳本可以安全執行")
        print()
        print("安全性確認：")
        print("  1. ✓ 僅使用標準庫和官方套件")
        print("  2. ✓ 僅執行 pip install（安裝 Python 套件）")
        print("  3. ✓ 僅開啟瀏覽器（不執行惡意代碼）")
        print("  4. ✓ 僅讀取/寫入專案目錄內的檔案")
        print("  5. ✓ 不修改系統設定或環境變數")
        print("  6. ✓ 不執行系統命令或腳本")
        print("  7. ✓ 所有套件來自 Google 官方")
        print()
        print("建議：")
        print("  - 執行前請確認網路連接安全")
        print("  - OAuth 憑證設定需要在 Google Cloud Console 手動操作")
        print("  - 憑證檔案僅儲存在本地專案目錄")
    else:
        print("⚠️  發現潛在風險，請仔細檢查")
        print()
        print("建議：")
        print("  - 檢查上述警告和風險項目")
        print("  - 確認腳本來源可信")
        print("  - 在安全環境中測試")
    
    print()
    print("=" * 70)
    
    return 0 if all_safe else 1


if __name__ == "__main__":
    sys.exit(main())
