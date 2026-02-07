#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_download_and_setup_credentials.py

自動開啟下載頁面並監控憑證檔案下載，然後自動設定

功能：
- 自動開啟 Google Cloud Console 憑證頁面
- 監控下載資料夾，等待憑證檔案下載
- 自動複製並設定憑證檔案
- 自動執行後續授權流程
"""

import sys
import json
import time
import shutil
import webbrowser
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
CLIENT_ID = "581281764864-4eg0icu55pkmbcirheflhp7fgt7gk499.apps.googleusercontent.com"
PROJECT_ID = "wuchang-sbir-project"
CONSOLE_URL = f"https://console.cloud.google.com/apis/credentials?project={PROJECT_ID}"


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def open_console_page():
    """開啟 Google Cloud Console 憑證頁面"""
    log("正在開啟 Google Cloud Console 憑證頁面...", "INFO")
    try:
        webbrowser.open(CONSOLE_URL)
        log("已開啟瀏覽器", "OK")
        return True
    except Exception as e:
        log(f"開啟瀏覽器失敗: {e}", "ERROR")
        print()
        print("請手動開啟以下網址：")
        print(CONSOLE_URL)
        return False


def find_downloaded_credentials(max_wait: int = 300) -> Optional[Path]:
    """監控下載資料夾，等待憑證檔案下載"""
    log("開始監控下載資料夾...", "INFO")
    print()
    print("請在瀏覽器中：")
    print("  1. 找到 OAuth 用戶端 ID（客戶端 ID 開頭: 581281764864）")
    print("  2. 點擊下載按鈕（⬇️）")
    print("  3. 等待下載完成")
    print()
    
    # 多個可能的下載位置
    download_paths = [
        Path.home() / "Downloads",
        Path.home() / "下載",
        BASE_DIR,
    ]
    
    # 記錄初始檔案列表（用於檢測新檔案）
    initial_files = {}
    for download_path in download_paths:
        if download_path.exists():
            for pattern in ["client_secret_*.json", "*credentials*.json", "*google*.json"]:
                for file_path in download_path.glob(pattern):
                    if file_path.is_file():
                        initial_files[file_path] = file_path.stat().st_mtime
    
    log(f"已記錄 {len(initial_files)} 個現有檔案", "INFO")
    print()
    print("等待新檔案下載...")
    print(f"（最多等待 {max_wait} 秒，按 Ctrl+C 可提前結束）")
    print()
    
    start_time = time.time()
    check_interval = 2  # 每 2 秒檢查一次
    
    while time.time() - start_time < max_wait:
        try:
            # 檢查所有下載位置
            for download_path in download_paths:
                if not download_path.exists():
                    continue
                
                # 檢查多種模式
                patterns = [
                    f"client_secret_*{CLIENT_ID.split('-')[0]}*.json",
                    "client_secret_*.json",
                    "*credentials*.json",
                    "*google*.json",
                ]
                
                for pattern in patterns:
                    for file_path in download_path.glob(pattern):
                        if file_path.is_file():
                            # 檢查是否是新檔案或已修改的檔案
                            current_mtime = file_path.stat().st_mtime
                            if file_path not in initial_files or current_mtime > initial_files.get(file_path, 0):
                                # 驗證檔案內容
                                try:
                                    test_data = json.loads(file_path.read_text(encoding="utf-8"))
                                    if "installed" in test_data or "web" in test_data:
                                        log(f"找到憑證檔案: {file_path}", "OK")
                                        return file_path
                                except:
                                    pass
            
            # 顯示等待進度
            elapsed = int(time.time() - start_time)
            if elapsed % 10 == 0 and elapsed > 0:
                print(f"  已等待 {elapsed} 秒...")
            
            time.sleep(check_interval)
            
        except KeyboardInterrupt:
            log("用戶中斷等待", "WARN")
            return None
    
    log(f"等待超時（{max_wait} 秒）", "WARN")
    return None


def setup_credentials_file(source_file: Path) -> bool:
    """設定憑證檔案"""
    log(f"正在設定憑證檔案: {source_file.name}", "INFO")
    
    try:
        # 複製到目標位置
        shutil.copy2(source_file, CREDENTIALS_FILE)
        log(f"憑證檔案已設定: {CREDENTIALS_FILE}", "OK")
        
        # 驗證檔案
        try:
            cred_data = json.loads(CREDENTIALS_FILE.read_text(encoding="utf-8"))
            if "installed" in cred_data or "web" in cred_data:
                log("憑證檔案格式驗證通過", "OK")
                return True
            else:
                log("憑證檔案格式可能不正確", "WARN")
                return False
        except Exception as e:
            log(f"驗證憑證檔案時發生錯誤: {e}", "ERROR")
            return False
            
    except Exception as e:
        log(f"設定憑證檔案時發生錯誤: {e}", "ERROR")
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
    print("自動下載並設定憑證（全自動流程）")
    print("=" * 70)
    print()
    
    # 步驟 1: 開啟瀏覽器
    if not open_console_page():
        print("請手動開啟瀏覽器並下載憑證檔案")
        return 1
    
    time.sleep(2)  # 等待瀏覽器開啟
    
    # 步驟 2: 監控下載
    downloaded_file = find_downloaded_credentials(max_wait=300)
    
    if not downloaded_file:
        print()
        print("=" * 70)
        print("【未檢測到憑證檔案下載】")
        print("=" * 70)
        print()
        print("可能原因：")
        print("  1. 尚未下載憑證檔案")
        print("  2. 下載到其他位置")
        print("  3. 檔案名稱不符合預期")
        print()
        print("解決方案：")
        print("  1. 手動下載憑證檔案")
        print("  2. 將檔案複製到專案目錄")
        print("  3. 重新命名為: google_credentials.json")
        print("  4. 執行: python little_j_full_auto_credentials_setup.py")
        print()
        return 1
    
    # 步驟 3: 設定憑證檔案
    if not setup_credentials_file(downloaded_file):
        print()
        print("=" * 70)
        print("【憑證檔案設定失敗】")
        print("=" * 70)
        print()
        return 1
    
    # 步驟 4: 執行授權流程
    if execute_authorization():
        print()
        print("=" * 70)
        print("【完成】")
        print("=" * 70)
        print()
        log("憑證設定和授權已完成", "OK")
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
        log("憑證檔案已設定，但授權流程有問題", "WARN")
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
