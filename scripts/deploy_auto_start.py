#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deploy_auto_start.py

五常系統 - 推送更新並設定開機自動啟動

功能：
1. 向伺服器推送自動部署相關檔案
2. 在本機設定開機自動啟動

使用方式：
  python deploy_auto_start.py [--push-only] [--setup-only]
"""

from __future__ import annotations

import argparse
import io
import os
import subprocess
import sys
from pathlib import Path

# 設定 Windows 控制台編碼
if sys.platform == "win32":
    if sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if sys.stderr.encoding != "utf-8":
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent


def push_to_server() -> bool:
    """向伺服器推送自動部署相關檔案"""
    print("=" * 50)
    print("步驟 1: 向伺服器推送更新")
    print("=" * 50)
    print()

    # 檢查環境變數
    health_url = os.getenv("WUCHANG_HEALTH_URL")
    copy_to = os.getenv("WUCHANG_COPY_TO")

    if not health_url or not copy_to:
        print("[提示] 未設定伺服器推送環境變數")
        print("[提示] 如需推送，請設定以下環境變數：")
        print("  - WUCHANG_HEALTH_URL: 伺服器健康檢查 URL")
        print("  - WUCHANG_COPY_TO: 推送目標資料夾（SMB/掛載磁碟）")
        print()
        print("[範例]")
        print('  $env:WUCHANG_HEALTH_URL="https://wuchang.life/health"')
        print('  $env:WUCHANG_COPY_TO="\\\\SERVER\\share\\wuchang"')
        print()
        return False

    print(f"[資訊] 健康檢查 URL: {health_url}")
    print(f"[資訊] 推送目標: {copy_to}")
    print()

    # 要推送的檔案清單（自動部署相關）
    deploy_files = [
        "start_servers.bat",
        "server_auto_deploy.py",
        "setup_auto_start.ps1",
        "remove_auto_start.ps1",
        "SERVER_AUTO_DEPLOY.md",
    ]

    # 檢查檔案是否存在
    missing_files = [f for f in deploy_files if not (BASE_DIR / f).exists()]
    if missing_files:
        print(f"[錯誤] 找不到以下檔案: {', '.join(missing_files)}")
        return False

    # 使用 safe_sync_push.py 推送檔案
    try:
        print("[執行] 開始推送檔案...")
        cmd = [
            sys.executable,
            str(BASE_DIR / "safe_sync_push.py"),
            "--health-url", health_url,
            "--copy-to", copy_to,
            "--actor", "deploy_script",
            "--files",
        ] + deploy_files

        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        
        if result.returncode == 0:
            print("[成功] 檔案已成功推送到伺服器")
            print(result.stdout)
            return True
        else:
            print("[錯誤] 推送失敗")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"[錯誤] 推送時發生異常: {e}")
        return False


def setup_auto_start() -> bool:
    """在本機設定開機自動啟動"""
    print()
    print("=" * 50)
    print("步驟 2: 設定本機開機自動啟動")
    print("=" * 50)
    print()

    # 檢查 PowerShell 腳本是否存在
    setup_script = BASE_DIR / "setup_auto_start.ps1"
    if not setup_script.exists():
        print(f"[錯誤] 找不到設定腳本: {setup_script}")
        return False

    # 檢查是否以管理員身份執行
    is_admin = False
    if sys.platform == "win32":
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            pass

    if not is_admin:
        print("[提示] 需要以系統管理員身份執行才能設定開機自動啟動")
        print()
        print("[執行步驟]")
        print("  1. 右鍵點擊「開始」按鈕")
        print("  2. 選擇「Windows PowerShell (系統管理員)」或「終端機 (系統管理員)」")
        print("  3. 切換到專案目錄：")
        print(f"     cd \"{BASE_DIR}\"")
        print("  4. 執行設定腳本：")
        print(f"     .\\setup_auto_start.ps1")
        print()
        return False

    # 執行 PowerShell 腳本（使用 chcp 65001 設定 UTF-8）
    try:
        print("[執行] 執行開機自動啟動設定...")
        if sys.platform == "win32":
            # 使用 cmd 執行 PowerShell，並設定編碼
            cmd = [
                "cmd.exe",
                "/c",
                "chcp", "65001", ">nul", "&",
                "powershell.exe",
                "-ExecutionPolicy", "Bypass",
                "-NoProfile",
                "-Command",
                f"& {{[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; . '{setup_script}'}}"
            ]
        else:
            print("[提示] 非 Windows 系統，請手動設定開機自動啟動")
            return False

        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", shell=True)
        
        if result.returncode == 0:
            print("[成功] 開機自動啟動已設定")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print("[警告] 自動設定可能失敗，請手動執行")
            if result.stderr:
                print(result.stderr)
            print()
            print("[手動執行指令]")
            print(f"  powershell -ExecutionPolicy Bypass -File \"{setup_script}\"")
            return False

    except Exception as e:
        print(f"[錯誤] 設定時發生異常: {e}")
        print()
        print("[手動執行指令]")
        print(f"  powershell -ExecutionPolicy Bypass -File \"{setup_script}\"")
        return False


def main() -> None:
    ap = argparse.ArgumentParser(description="五常系統 - 推送更新並設定開機自動啟動")
    ap.add_argument("--push-only", action="store_true", help="僅執行推送，不設定開機自動啟動")
    ap.add_argument("--setup-only", action="store_true", help="僅設定開機自動啟動，不推送")
    args = ap.parse_args()

    success = True

    # 推送更新
    if not args.setup_only:
        if not push_to_server():
            success = False
            if args.push_only:
                sys.exit(1)

    # 設定開機自動啟動
    if not args.push_only:
        if not setup_auto_start():
            success = False

    print()
    print("=" * 50)
    if success:
        print("[成功] 所有操作完成")
    else:
        print("[警告] 部分操作未完成，請檢查上述訊息")
    print("=" * 50)


if __name__ == "__main__":
    main()
