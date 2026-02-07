#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_download_credentials_with_browser.py

使用 AI 控制瀏覽器自動下載憑證

功能：
- 自動開啟 Google Cloud Console
- 自動登入（如果需要）
- 自動導航到憑證頁面
- 自動下載憑證檔案
- 自動設定憑證檔案
- 自動執行授權流程
"""

import sys
import json
import time
import shutil
from pathlib import Path
from typing import Optional

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
CREDENTIALS_FILE = BASE_DIR / "google_credentials.json"
TOKEN_FILE = BASE_DIR / "google_token.json"
CLIENT_ID = "581281764864-2a3285kidmm2rj7jmrl9ve7cqfvid32d.apps.googleusercontent.com"
PROJECT_ID = "wuchang-sbir-project"
CONSOLE_URL = f"https://console.cloud.google.com/apis/credentials?project={PROJECT_ID}"


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def check_browser_automation():
    """檢查瀏覽器自動化工具"""
    log("檢查瀏覽器自動化工具", "INFO")
    
    # 優先使用 Playwright
    try:
        from playwright.sync_api import sync_playwright
        log("Playwright 可用", "OK")
        return "playwright"
    except ImportError:
        pass
    
    # 備選：使用 Selenium
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        log("Selenium 可用", "OK")
        return "selenium"
    except ImportError:
        pass
    
    log("未找到瀏覽器自動化工具", "ERROR")
    return None


def download_with_playwright() -> bool:
    """使用 Playwright 下載憑證"""
    from playwright.sync_api import sync_playwright
    
    log("使用 Playwright 控制瀏覽器", "INFO")
    
    with sync_playwright() as p:
        # 啟動瀏覽器（顯示視窗，方便用戶操作）
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            accept_downloads=True,
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        
        try:
            # 導航到憑證頁面
            log(f"正在開啟: {CONSOLE_URL}", "INFO")
            page.goto(CONSOLE_URL, wait_until="networkidle", timeout=60000)
            
            log("等待頁面載入...", "INFO")
            time.sleep(3)
            
            # 等待用戶登入（如果需要）
            log("請在瀏覽器中完成登入（如果需要）", "INFO")
            log("登入完成後，腳本將繼續...", "INFO")
            
            # 等待頁面完全載入
            try:
                page.wait_for_selector("text=憑證", timeout=30000)
            except:
                log("未找到憑證標籤，繼續執行...", "WARN")
            
            # 尋找 OAuth 用戶端 ID
            log(f"正在尋找 OAuth 用戶端 ID: {CLIENT_ID[:20]}...", "INFO")
            
            # 嘗試點擊下載按鈕
            download_clicked = False
            try:
                # 多種可能的選擇器
                selectors = [
                    f"text={CLIENT_ID[:20]}",
                    f"text=581281764864",
                    "button:has-text('下載')",
                    "button[aria-label*='下載']",
                    "button[aria-label*='Download']",
                    ".download-button",
                ]
                
                for selector in selectors:
                    try:
                        element = page.wait_for_selector(selector, timeout=5000)
                        if element:
                            # 找到對應的憑證行，點擊下載
                            row = element.locator("xpath=ancestor::tr")
                            download_btn = row.locator("button:has-text('下載'), button[aria-label*='下載'], button[aria-label*='Download']")
                            if download_btn.count() > 0:
                                download_btn.first.click()
                                download_clicked = True
                                log("已點擊下載按鈕", "OK")
                                break
                    except:
                        continue
            except Exception as e:
                log(f"自動點擊下載失敗: {e}", "WARN")
                log("請手動點擊下載按鈕", "INFO")
            
            # 監控下載（兩種方式：Playwright 下載事件或監控下載資料夾）
            log("等待檔案下載...", "INFO")
            download_path = None
            
            # 記錄初始下載資料夾狀態
            downloads_dir = Path.home() / "Downloads"
            initial_files = set()
            if downloads_dir.exists():
                initial_files = {f for f in downloads_dir.glob("*.json") if f.is_file()}
            
            # 嘗試監聽下載事件（60秒超時）
            download_detected = False
            try:
                with page.expect_download(timeout=60000) as download_info:
                    if not download_clicked:
                        log("請手動點擊下載按鈕（在瀏覽器中）", "INFO")
                        log("腳本將等待下載完成...", "INFO")
                    
                    download = download_info.value
                    download_path = download.path()
                    log(f"檔案已下載: {download_path}", "OK")
                    
                    # 儲存檔案
                    target_path = BASE_DIR / download.suggested_filename()
                    download.save_as(str(target_path))
                    log(f"檔案已儲存: {target_path}", "OK")
                    
                    download_detected = True
            except Exception as e:
                log(f"未檢測到 Playwright 下載事件: {e}", "WARN")
                log("改為監控下載資料夾...", "INFO")
            
            # 如果 Playwright 下載事件未觸發，監控下載資料夾
            if not download_detected:
                log("請在瀏覽器中手動點擊下載按鈕", "INFO")
                log("腳本將監控下載資料夾，等待檔案出現...", "INFO")
                
                # 監控下載資料夾（最多 120 秒）
                for i in range(120):
                    time.sleep(1)
                    
                    # 檢查下載資料夾中的新檔案
                    if downloads_dir.exists():
                        current_files = {f for f in downloads_dir.glob("*.json") if f.is_file()}
                        new_files = current_files - initial_files
                        
                        if new_files:
                            # 找到最新的檔案
                            latest_file = max(new_files, key=lambda p: p.stat().st_mtime)
                            
                            # 驗證檔案內容
                            try:
                                test_data = json.loads(latest_file.read_text(encoding="utf-8"))
                                if "installed" in test_data or "web" in test_data:
                                    download_path = latest_file
                                    log(f"在下載資料夾中找到憑證檔案: {latest_file.name}", "OK")
                                    break
                            except:
                                pass
                    
                    if i % 10 == 0 and i > 0:
                        print(f"  等待中... ({i}/120 秒)")
            
            # 處理下載的檔案
            if download_path:
                if isinstance(download_path, Path):
                    # 從下載資料夾複製
                    shutil.copy2(download_path, CREDENTIALS_FILE)
                else:
                    # Playwright 下載的檔案已在目標位置
                    pass
                
                log(f"憑證檔案已設定: {CREDENTIALS_FILE}", "OK")
                browser.close()
                return True
            else:
                log("未檢測到憑證檔案下載", "WARN")
                browser.close()
                return False
            
        except Exception as e:
            log(f"瀏覽器操作失敗: {e}", "ERROR")
            log("請手動下載憑證檔案", "WARN")
            browser.close()
            return False


def download_with_selenium() -> bool:
    """使用 Selenium 下載憑證"""
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    
    log("使用 Selenium 控制瀏覽器", "INFO")
    
    # 設定 Chrome 選項
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": str(BASE_DIR),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
    })
    
    # 啟動瀏覽器
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # 導航到憑證頁面
        log(f"正在開啟: {CONSOLE_URL}", "INFO")
        driver.get(CONSOLE_URL)
        
        log("等待頁面載入...", "INFO")
        time.sleep(5)
        
        # 等待用戶登入
        log("請在瀏覽器中完成登入（如果需要）", "INFO")
        time.sleep(10)
        
        # 尋找並點擊下載按鈕
        log(f"正在尋找 OAuth 用戶端 ID: {CLIENT_ID[:20]}...", "INFO")
        
        try:
            # 等待憑證列表載入
            wait = WebDriverWait(driver, 30)
            
            # 尋找包含客戶端 ID 的元素
            client_id_element = wait.until(
                EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{CLIENT_ID[:20]}')]"))
            )
            
            # 找到對應的下載按鈕
            row = client_id_element.find_element(By.XPATH, "./ancestor::tr")
            download_btn = row.find_element(By.XPATH, ".//button[contains(@aria-label, '下載') or contains(@aria-label, 'Download')]")
            download_btn.click()
            
            log("已點擊下載按鈕", "OK")
            
            # 等待下載完成
            log("等待檔案下載...", "INFO")
            time.sleep(10)
            
            # 檢查下載的檔案
            downloaded_files = list(BASE_DIR.glob("client_secret_*.json"))
            if downloaded_files:
                latest_file = max(downloaded_files, key=lambda p: p.stat().st_mtime)
                shutil.copy2(latest_file, CREDENTIALS_FILE)
                log(f"憑證檔案已設定: {CREDENTIALS_FILE}", "OK")
                driver.quit()
                return True
            else:
                log("未找到下載的檔案", "WARN")
                driver.quit()
                return False
                
        except Exception as e:
            log(f"自動下載失敗: {e}", "WARN")
            log("請手動點擊下載按鈕", "INFO")
            log("下載完成後，腳本將自動處理檔案", "INFO")
            
            # 等待用戶手動下載
            time.sleep(30)
            
            # 檢查下載的檔案
            downloaded_files = list(BASE_DIR.glob("client_secret_*.json"))
            if downloaded_files:
                latest_file = max(downloaded_files, key=lambda p: p.stat().st_mtime)
                shutil.copy2(latest_file, CREDENTIALS_FILE)
                log(f"憑證檔案已設定: {CREDENTIALS_FILE}", "OK")
                driver.quit()
                return True
            
            driver.quit()
            return False
            
    except Exception as e:
        log(f"瀏覽器操作失敗: {e}", "ERROR")
        driver.quit()
        return False


def execute_authorization():
    """執行授權流程"""
    log("開始執行 OAuth 授權流程", "INFO")
    
    if not CREDENTIALS_FILE.exists():
        log("憑證檔案不存在，無法執行授權", "ERROR")
        return False
    
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "complete_authorization_and_setup.py"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300
        )
        
        log("授權腳本執行完成", "INFO")
        
        if TOKEN_FILE.exists():
            log("OAuth token 已生成", "OK")
            return True
        else:
            log("OAuth token 未生成", "WARN")
            return False
            
    except Exception as e:
        log(f"執行授權流程時發生錯誤: {e}", "ERROR")
        return False


def main():
    """主函數"""
    print("=" * 70)
    print("AI 控制瀏覽器自動下載憑證")
    print("=" * 70)
    print()
    
    # 檢查瀏覽器自動化工具
    automation_tool = check_browser_automation()
    
    if not automation_tool:
        print()
        print("=" * 70)
        print("【需要安裝瀏覽器自動化工具】")
        print("=" * 70)
        print()
        print("正在自動安裝...")
        print()
        
        # 嘗試安裝
        import subprocess
        try:
            subprocess.run(
                [sys.executable, "install_browser_automation.py"],
                check=True
            )
            automation_tool = check_browser_automation()
        except:
            pass
        
        if not automation_tool:
            print()
            print("請執行以下命令安裝：")
            print("  python install_browser_automation.py")
            print()
            print("或手動安裝：")
            print("  pip install playwright")
            print("  playwright install chromium")
            print()
            return 1
    
    # 使用瀏覽器自動化下載
    if automation_tool == "playwright":
        success = download_with_playwright()
    elif automation_tool == "selenium":
        success = download_with_selenium()
    else:
        log("未知的自動化工具", "ERROR")
        return 1
    
    if not success:
        print()
        print("=" * 70)
        print("【下載失敗】")
        print("=" * 70)
        print()
        print("請手動下載憑證檔案，然後執行：")
        print("  python little_j_full_auto_credentials_setup.py")
        print()
        return 1
    
    # 執行授權流程
    if execute_authorization():
        print()
        print("=" * 70)
        print("【完成】")
        print("=" * 70)
        print()
        log("憑證下載和授權已完成", "OK")
        print()
        print("現在可以使用：")
        print("  - python get_jules_task_direct.py <task_url>")
        print("  - python upload_diff_to_jules.py --auto-upload")
        print("  - python sync_from_google_task.py <task_url> <target_file>")
        print()
        return 0
    else:
        print()
        print("=" * 70)
        print("【部分完成】")
        print("=" * 70)
        print()
        log("憑證檔案已下載，但授權流程有問題", "WARN")
        print("可以手動執行：")
        print("  python complete_authorization_and_setup.py")
        print()
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        print("已中斷")
        sys.exit(1)
