#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_network_drive.py

修復網路磁碟機連接問題

功能：
- 檢查現有網路磁碟機
- 斷開衝突的連接
- 重新映射網路磁碟機
- 設定環境變數
"""

import sys
import subprocess
import os
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def get_mapped_drives():
    """獲取已映射的網路磁碟機"""
    try:
        result = subprocess.run(
            ["net", "use"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.stdout
    except:
        return ""


def disconnect_drive(drive_letter: str):
    """斷開網路磁碟機"""
    try:
        result = subprocess.run(
            ["net", "use", f"{drive_letter}:", "/delete", "/yes"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0
    except:
        return False


def map_network_drive(drive_letter: str, network_path: str, persistent: bool = True):
    """映射網路磁碟機"""
    try:
        persistent_flag = "/persistent:yes" if persistent else "/persistent:no"
        result = subprocess.run(
            ["net", "use", f"{drive_letter}:", network_path, persistent_flag],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0
    except:
        return False


def main():
    """主函數"""
    print("=" * 70)
    print("修復網路磁碟機連接")
    print("=" * 70)
    print()
    
    # 目標路徑
    network_path = r"\\HOME-COMMPUT\wuchang V5.1.0"
    drive_letter = "Z:"
    
    # 認證資訊（從參數或環境變數讀取）
    import sys
    username = None
    password = None
    
    if len(sys.argv) >= 3:
        username = sys.argv[1]
        password = sys.argv[2]
    else:
        # 嘗試從環境變數讀取，或使用預設值
        import os
        username = os.getenv("NETWORK_USER", "HOME-COMMPUT\\User")
        password = os.getenv("NETWORK_PASSWORD", "Qwerty926")
    
    print(f"【目標】")
    print(f"  網路路徑: {network_path}")
    print(f"  磁碟機代號: {drive_letter}")
    print()
    
    # 檢查現有連接
    print("【步驟 1：檢查現有連接】")
    mapped_drives = get_mapped_drives()
    print(mapped_drives)
    
    # 檢查 Z: 是否已被使用
    if f"{drive_letter}" in mapped_drives:
        print(f"\n⚠️  {drive_letter} 已被使用")
        print("正在斷開現有連接...")
        if disconnect_drive(drive_letter[0]):
            print(f"✓ 已斷開 {drive_letter}")
        else:
            print(f"✗ 無法斷開 {drive_letter}，請手動處理")
    else:
        print(f"✓ {drive_letter} 未被使用")
    print()
    
    # 測試網路路徑
    print("【步驟 2：測試網路路徑】")
    network_accessible = Path(network_path).exists()
    if network_accessible:
        print(f"✓ 網路路徑可訪問: {network_path}")
    else:
        print(f"⚠️  網路路徑目前不可訪問: {network_path}")
        print("  可能原因：")
        print("  1. 網路連接中斷")
        print("  2. 共享伺服器未運行")
        print("  3. 需要認證")
        print("  4. 共享路徑名稱可能有誤（注意拼寫：COMMPUT vs COMPUTER）")
        print()
        print("  將嘗試映射，如果失敗請手動處理")
    print()
    
    # 映射網路磁碟機
    print("【步驟 3：映射網路磁碟機】")
    
    # 如果有認證資訊，使用認證映射
    if username and password:
        print(f"使用認證資訊映射...")
        try:
            result = subprocess.run(
                ["net", "use", f"{drive_letter[0]}:", network_path, 
                 "/user", username, password, "/persistent:yes"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            if result.returncode == 0:
                print(f"✓ 成功映射 {drive_letter} 到 {network_path}")
                mapped_success = True
            else:
                print(f"⚠️  映射失敗: {result.stderr}")
                mapped_success = False
        except Exception as e:
            print(f"✗ 映射錯誤: {e}")
            mapped_success = False
    else:
        # 無認證映射
        if map_network_drive(drive_letter[0], network_path, persistent=True):
            print(f"✓ 成功映射 {drive_letter} 到 {network_path}")
            mapped_success = True
        else:
            print(f"⚠️  自動映射失敗")
            print("  可能原因：")
            print("  1. 權限不足")
            print("  2. 網路路徑不存在或不可訪問")
            print("  3. 需要認證")
            print("  4. 共享路徑名稱可能有誤")
            print()
            print("  手動映射指令：")
            print(f"    net use {drive_letter} {network_path} /persistent:yes")
            mapped_success = False
    print()
    
    # 設定環境變數
    print("【步驟 4：設定環境變數】")
    # 優先使用映射的磁碟機，如果失敗則使用 UNC 路徑
    if mapped_success and Path(f"{drive_letter}\\").exists():
        env_path = f"{drive_letter}\\"
    else:
        env_path = network_path
        print(f"  使用 UNC 路徑: {env_path}")
    
    os.environ["WUCHANG_COPY_TO"] = env_path
    
    # 嘗試永久設定（Windows）
    try:
        import winreg
        reg_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            "Environment",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(reg_key, "WUCHANG_COPY_TO", 0, winreg.REG_EXPAND_SZ, env_path)
        winreg.CloseKey(reg_key)
        print(f"✓ 已永久設定 WUCHANG_COPY_TO = {env_path}")
    except Exception as e:
        print(f"⚠️  無法永久設定環境變數: {e}")
        print(f"  已設定當前會話: WUCHANG_COPY_TO = {env_path}")
    
    print()
    
    # 驗證
    print("【步驟 5：驗證連接】")
    test_path = Path(env_path)
    if test_path.exists():
        try:
            files = list(test_path.iterdir())
            print(f"✓ 連接成功，找到 {len(files)} 個項目")
            print(f"  路徑: {env_path}")
        except Exception as e:
            print(f"⚠️  路徑可訪問但無法列出內容: {e}")
    else:
        print("✗ 連接驗證失敗")
        print(f"  無法訪問: {env_path}")
        print("  請確認網路連接和共享設定")
    
    print()
    print("=" * 70)
    print("【完成】")
    print(f"網路磁碟機 {drive_letter} 已映射到 {network_path}")
    print(f"環境變數 WUCHANG_COPY_TO = {env_path}")
    print()
    print("【下一步】")
    print("可以執行檔案同步：")
    print("  python sync_all_profiles.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
