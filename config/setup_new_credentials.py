#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_new_credentials.py

自動搜尋並設定新的憑證檔案

功能：
- 搜尋指定的憑證檔案
- 複製到專案目錄
- 重新命名為 google_credentials.json
- 執行授權流程
"""

import sys
import json
import shutil
import subprocess
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
CREDENTIALS_FILE = BASE_DIR / "google_credentials.json"
TOKEN_FILE = BASE_DIR / "google_token.json"
TARGET_FILENAME = "client_secret_581281764864-2a3285kidmm2rj7jmrl9ve7cqfvid32d.apps.googleusercontent.com.json"
NEW_CLIENT_ID = "581281764864-2a3285kidmm2rj7jmrl9ve7cqfvid32d.apps.googleusercontent.com"


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    print(f"[{level}] {message}")


def find_credentials_file():
    """搜尋憑證檔案"""
    log("開始搜尋憑證檔案...", "INFO")
    
    # 搜尋位置（更廣泛的範圍）
    search_paths = [
        Path.home() / "Downloads",
        Path.home() / "下載",
        Path.home() / "Desktop",
        Path.home() / "桌面",
        Path.home() / "Documents",
        Path.home() / "文件",
        BASE_DIR,
        Path("C:/Users") / Path.home().name / "Downloads",  # 絕對路徑
    ]
    
    # 搜尋模式（更寬鬆）
    patterns = [
        TARGET_FILENAME,
        "client_secret_581281764864-2a3285kidmm2rj7jmrl9ve7cqfvid32d*.json",
        "client_secret_*2a3285kidmm2rj7jmrl9ve7cqfvid32d*.json",
        "*2a3285kidmm2rj7jmrl9ve7cqfvid32d*.json",  # 更寬鬆的匹配
        "client_secret_*.json",  # 所有 client_secret 檔案
    ]
    
    found_files = []
    
    for search_path in search_paths:
        if not search_path.exists():
            continue
        
        log(f"搜尋: {search_path}", "INFO")
        
        for pattern in patterns:
            try:
                for file_path in search_path.glob(pattern):
                    if file_path.is_file():
                        # 驗證檔案內容
                        try:
                            test_data = json.loads(file_path.read_text(encoding="utf-8"))
                            if "installed" in test_data or "web" in test_data:
                                # 檢查是否包含新的客戶端 ID
                                file_str = file_path.read_text(encoding="utf-8")
                                if "2a3285kidmm2rj7jmrl9ve7cqfvid32d" in file_str:
                                    log(f"找到憑證檔案: {file_path}", "OK")
                                    return file_path
                                else:
                                    found_files.append(file_path)
                        except:
                            pass
            except Exception as e:
                log(f"搜尋 {search_path} 時發生錯誤: {e}", "WARN")
                continue
    
    # 如果找到其他憑證檔案，顯示它們
    if found_files:
        log(f"找到 {len(found_files)} 個其他憑證檔案，但不符合新的客戶端 ID", "WARN")
        for f in found_files[:3]:  # 只顯示前3個
            log(f"  - {f}", "INFO")
    
    log("未找到符合新客戶端 ID 的憑證檔案", "WARN")
    return None


def setup_credentials_file(source_file: Path):
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
                
                # 顯示客戶端 ID
                if "installed" in cred_data:
                    client_id = cred_data["installed"].get("client_id", "")
                elif "web" in cred_data:
                    client_id = cred_data["web"].get("client_id", "")
                else:
                    client_id = "未知"
                
                log(f"客戶端 ID: {client_id}", "INFO")
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
        result = subprocess.run(
            [sys.executable, "complete_authorization_and_setup.py"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
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
    print("自動設定新憑證檔案")
    print("=" * 70)
    print()
    print(f"目標檔案: {TARGET_FILENAME}")
    print(f"新客戶端 ID: {NEW_CLIENT_ID}")
    print()
    
    # 步驟 1: 搜尋憑證檔案
    source_file = find_credentials_file()
    
    if not source_file:
        print()
        print("=" * 70)
        print("【未找到憑證檔案】")
        print("=" * 70)
        print()
        print("請確認檔案已下載到以下位置之一：")
        print("  - 下載資料夾 (Downloads/下載)")
        print("  - 桌面 (Desktop/桌面)")
        print("  - 專案目錄")
        print()
        print(f"檔案名稱: {TARGET_FILENAME}")
        print()
        return 1
    
    # 步驟 2: 設定憑證檔案
    if not setup_credentials_file(source_file):
        print()
        print("=" * 70)
        print("【憑證檔案設定失敗】")
        print("=" * 70)
        print()
        return 1
    
    # 步驟 3: 執行授權流程
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
    sys.exit(main())
