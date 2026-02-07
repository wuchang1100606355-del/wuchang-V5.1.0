#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
install_browser_automation.py

安裝瀏覽器自動化工具

功能：
- 檢查並安裝 Selenium 或 Playwright
- 下載瀏覽器驅動程式
- 配置環境
"""

import sys
import subprocess

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

def check_and_install_selenium():
    """檢查並安裝 Selenium"""
    print("【檢查 Selenium】")
    print()
    
    try:
        import selenium
        print("  ✓ Selenium 已安裝")
        print(f"    版本: {selenium.__version__}")
        return True
    except ImportError:
        print("  ✗ Selenium 未安裝")
        print()
        print("  正在安裝 Selenium...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "selenium", "webdriver-manager"],
                check=True,
                capture_output=True,
                text=True
            )
            print("  ✓ Selenium 安裝成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Selenium 安裝失敗: {e}")
            return False


def check_and_install_playwright():
    """檢查並安裝 Playwright"""
    print()
    print("【檢查 Playwright】")
    print()
    
    try:
        import playwright
        print("  ✓ Playwright 已安裝")
        return True
    except ImportError:
        print("  ✗ Playwright 未安裝")
        print()
        print("  正在安裝 Playwright...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "playwright"],
                check=True,
                capture_output=True,
                text=True
            )
            print("  ✓ Playwright 安裝成功")
            print()
            print("  正在安裝瀏覽器...")
            subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                check=True,
                capture_output=True,
                text=True
            )
            print("  ✓ 瀏覽器安裝成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Playwright 安裝失敗: {e}")
            return False


def main():
    """主函數"""
    print("=" * 70)
    print("瀏覽器自動化工具安裝")
    print("=" * 70)
    print()
    
    # 優先使用 Playwright（更現代、更穩定）
    if check_and_install_playwright():
        print()
        print("=" * 70)
        print("【完成】")
        print("=" * 70)
        print()
        print("✓ Playwright 已安裝並配置完成")
        print()
        print("現在可以使用：")
        print("  python auto_download_credentials_with_browser.py")
        print()
        return 0
    
    # 備選：使用 Selenium
    if check_and_install_selenium():
        print()
        print("=" * 70)
        print("【完成】")
        print("=" * 70)
        print()
        print("✓ Selenium 已安裝")
        print()
        print("現在可以使用：")
        print("  python auto_download_credentials_with_browser.py")
        print()
        return 0
    
    print()
    print("=" * 70)
    print("【安裝失敗】")
    print("=" * 70)
    print()
    print("無法安裝瀏覽器自動化工具")
    print("請手動安裝：")
    print("  pip install playwright")
    print("  playwright install chromium")
    print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
