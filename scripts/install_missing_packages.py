#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
install_missing_packages.py

安裝缺失的 Python 套件

功能：
- 檢查並安裝 Flask
- 檢查並安裝 google-auth
- 驗證安裝結果
"""

import sys
import subprocess
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

MISSING_PACKAGES = ["Flask", "google-auth"]


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌",
        "STEP": "📋"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")


def check_package_installed(package_name: str) -> bool:
    """檢查套件是否已安裝"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception as e:
        log(f"檢查 {package_name} 時發生錯誤: {e}", "WARN")
        return False


def install_package(package_name: str) -> bool:
    """安裝套件"""
    try:
        log(f"正在安裝 {package_name}...", "STEP")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            log(f"✓ {package_name} 安裝成功", "OK")
            return True
        else:
            log(f"✗ {package_name} 安裝失敗: {result.stderr}", "ERROR")
            return False
    except Exception as e:
        log(f"✗ 安裝 {package_name} 時發生錯誤: {e}", "ERROR")
        return False


def main():
    """主程式"""
    print("=" * 100)
    print("安裝缺失的 Python 套件")
    print("=" * 100)
    print()
    
    log(f"Python 版本: {sys.version}", "INFO")
    log(f"Python 執行檔: {sys.executable}", "INFO")
    print()
    
    # 檢查並安裝套件
    results = {}
    for package in MISSING_PACKAGES:
        if check_package_installed(package):
            log(f"{package} 已安裝", "OK")
            results[package] = True
        else:
            log(f"{package} 未安裝", "WARN")
            results[package] = install_package(package)
        print()
    
    # 顯示結果摘要
    print("=" * 100)
    print("安裝結果摘要")
    print("=" * 100)
    print()
    
    all_ok = True
    for package, installed in results.items():
        if installed:
            log(f"{package}: 已安裝", "OK")
        else:
            log(f"{package}: 安裝失敗", "ERROR")
            all_ok = False
    
    print()
    if all_ok:
        log("所有套件已成功安裝！", "OK")
        return 0
    else:
        log("部分套件安裝失敗，請檢查錯誤訊息", "ERROR")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n程式已中斷")
        sys.exit(0)
    except Exception as e:
        log(f"發生未預期的錯誤: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)
