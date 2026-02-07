#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
admin_account_sensor.py

admin@wuchang.life 帳號權限感知模組

功能：
- 檢測 Windows 10 專業版系統帳號權限
- 驗證 admin@wuchang.life 作為超級管理員/最高權限者身份
- 監控 Google Workspace 相關資源狀態

合規聲明：
- 本系統除法律規範須依法揭露及政府公示資訊中公開揭露之外無可供識別之個資，應屬合規
- 本系統可究責之自然人不在隱私權保護規範內
- 本系統及AI程序設計之可究責自然人不在隱私權保護規範內
- 本模組僅讀取帳號權限狀態，不包含個人可識別資訊（法律規範須依法揭露、政府公示資訊中公開揭露、可究責之自然人除外）
- 詳見 COMPLIANCE_NO_PII.md
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

ADMIN_EMAIL = "admin@wuchang.life"


def check_windows_admin() -> Dict[str, Any]:
    """檢查 Windows 管理員權限"""
    if sys.platform != "win32":
        return {"is_windows": False, "is_admin": False, "error": "not_windows"}

    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        
        # 獲取當前用戶名
        username = os.getenv("USERNAME", "")
        userdomain = os.getenv("USERDOMAIN", "")
        full_username = f"{userdomain}\\{username}" if userdomain else username
        
        return {
            "is_windows": True,
            "is_admin": is_admin,
            "username": username,
            "userdomain": userdomain,
            "full_username": full_username,
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
        }
    except Exception as e:
        return {"is_windows": True, "is_admin": False, "error": str(e)}


def check_google_drive_sync() -> Dict[str, Any]:
    """檢查 Google Drive 同步狀態"""
    result = {
        "configured": False,
        "paths": {},
        "sync_status": "unknown",
    }

    # 檢查環境變數
    system_db_dir = os.getenv("WUCHANG_SYSTEM_DB_DIR", "").strip()
    workspace_outdir = os.getenv("WUCHANG_WORKSPACE_OUTDIR", "").strip()
    pii_outdir = os.getenv("WUCHANG_PII_OUTDIR", "").strip()
    exchange_dir = os.getenv("WUCHANG_WORKSPACE_EXCHANGE_DIR", "").strip()

    if system_db_dir:
        result["configured"] = True
        result["paths"]["system_db_dir"] = system_db_dir
        result["paths"]["exists"] = Path(system_db_dir).exists()

    if workspace_outdir:
        result["paths"]["workspace_outdir"] = workspace_outdir
        result["paths"]["workspace_outdir_exists"] = Path(workspace_outdir).exists()

    if pii_outdir:
        result["paths"]["pii_outdir"] = pii_outdir
        result["paths"]["pii_outdir_exists"] = Path(pii_outdir).exists()

    if exchange_dir:
        result["paths"]["exchange_dir"] = exchange_dir
        result["paths"]["exchange_dir_exists"] = Path(exchange_dir).exists()

    # 檢查 Google Drive 進程（Windows）
    if sys.platform == "win32":
        try:
            result["processes"] = {}
            # 檢查 Google Drive 進程
            processes_to_check = [
                "GoogleDriveFS.exe",
                "googledrivesync.exe",
                "GoogleDrive.exe",
            ]
            for proc_name in processes_to_check:
                try:
                    output = subprocess.run(
                        ["tasklist", "/FI", f"IMAGENAME eq {proc_name}"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    running = proc_name.lower() in output.stdout.lower()
                    result["processes"][proc_name] = running
                except Exception:
                    result["processes"][proc_name] = False

            # 判斷同步狀態
            any_running = any(result["processes"].values())
            result["sync_status"] = "running" if any_running else "stopped"
        except Exception as e:
            result["sync_status"] = "error"
            result["error"] = str(e)

    return result


def check_google_workspace_account() -> Dict[str, Any]:
    """檢查 Google Workspace 帳號狀態（admin@wuchang.life）"""
    result = {
        "admin_email": ADMIN_EMAIL,
        "workspace_configured": False,
        "nonprofit_status": "unknown",
    }

    # 檢查環境變數中的配置
    system_db_dir = os.getenv("WUCHANG_SYSTEM_DB_DIR", "").strip()
    if system_db_dir:
        result["workspace_configured"] = True
        result["system_db_path"] = system_db_dir

    # 檢查關鍵配置檔案
    if system_db_dir:
        config_dir = Path(system_db_dir) / "config"
        accounts_path = config_dir / "accounts_policy.json"
        matching_path = config_dir / "workspace_matching.json"

        result["config_files"] = {
            "accounts_policy": {
                "path": str(accounts_path),
                "exists": accounts_path.exists(),
            },
            "workspace_matching": {
                "path": str(matching_path),
                "exists": matching_path.exists(),
            },
        }

    # 根據文件，協會已完成 Google for Nonprofits 驗證
    result["nonprofit_status"] = "verified"
    result["nonprofit_benefits"] = [
        "Google Workspace for Nonprofits",
        "Google Ad Grants",
        "Google Maps Platform 公益方案",
    ]

    return result


def check_billing_access() -> Dict[str, Any]:
    """檢查帳單存取權限（理論上 admin@wuchang.life 應有最高權限）"""
    result = {
        "admin_email": ADMIN_EMAIL,
        "billing_access": "unknown",
        "note": "帳單資訊需透過 Google Workspace Admin Console 或 Google Cloud Console 存取",
    }

    # 檢查是否有相關環境變數或配置
    system_db_dir = os.getenv("WUCHANG_SYSTEM_DB_DIR", "").strip()
    if system_db_dir:
        # 檢查是否有帳單相關檔案（如果有的話）
        billing_dir = Path(system_db_dir) / "billing"
        if billing_dir.exists():
            result["billing_dir_exists"] = True
            result["billing_dir"] = str(billing_dir)
        else:
            result["billing_dir_exists"] = False

    # 根據 admin@wuchang.life 作為所有權人身份，應有最高權限
    result["expected_permissions"] = [
        "Google Workspace Admin Console 完整存取",
        "Google Cloud Console 帳單查看",
        "Google for Nonprofits 帳號管理",
        "所有資源的所有權人權限",
    ]

    return result


def get_admin_account_status() -> Dict[str, Any]:
    """獲取完整的 admin@wuchang.life 帳號狀態"""
    return {
        "admin_email": ADMIN_EMAIL,
        "role": "超級管理員/最高權限者/所有權人",
        "windows": check_windows_admin(),
        "google_drive": check_google_drive_sync(),
        "google_workspace": check_google_workspace_account(),
        "billing": check_billing_access(),
    }
