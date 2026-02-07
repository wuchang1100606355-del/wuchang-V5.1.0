#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_env_vars.py

五常系統環境變數統一設定工具

功能：
- 統一管理所有系統環境變數
- 支援當前會話和永久設定
- 驗證環境變數有效性
- 生成環境變數配置文件
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent

# 所有環境變數定義
ENV_VARS_DEF = {
    "WUCHANG_HEALTH_URL": {
        "description": "伺服器健康檢查 URL",
        "example": "https://wuchang.life/health",
        "required_for": ["safe_sync_push", "check_server_connection", "file_compare_sync"],
    },
    "WUCHANG_COPY_TO": {
        "description": "伺服器接收資料夾路徑（SMB/掛載磁碟）",
        "example": "\\\\SERVER\\share\\wuchang",
        "required_for": ["safe_sync_push", "file_compare_sync", "smart_sync"],
    },
    "WUCHANG_HUB_URL": {
        "description": "Little J Hub 服務器 URL",
        "example": "https://hub.wuchang.life",
        "required_for": ["hub_connection", "local_control_center"],
    },
    "WUCHANG_HUB_TOKEN": {
        "description": "Little J Hub 認證 Token",
        "example": "your_token_here",
        "required_for": ["hub_connection"],
        "sensitive": True,
    },
    "WUCHANG_SYSTEM_DB_DIR": {
        "description": "系統資料庫目錄",
        "example": "C:\\wuchang\\db",
        "required_for": [],
    },
    "WUCHANG_WORKSPACE_OUTDIR": {
        "description": "工作空間輸出目錄",
        "example": "C:\\wuchang\\output",
        "required_for": [],
    },
    "WUCHANG_PII_OUTDIR": {
        "description": "個資輸出目錄",
        "example": "C:\\wuchang\\pii",
        "required_for": ["pii_storage"],
    },
    "WUCHANG_PII_ENABLED": {
        "description": "是否啟用個資處理功能",
        "example": "true",
        "required_for": ["pii_storage"],
        "type": "boolean",
    },
    "WUCHANG_PII_STORAGE_DEVICE": {
        "description": "個資儲存裝置 ID",
        "example": "usb_001",
        "required_for": ["pii_storage"],
    },
}


def get_env_status() -> Dict[str, Any]:
    """獲取環境變數狀態"""
    status = {
        "timestamp": __import__("time").strftime("%Y-%m-%dT%H:%M:%S%z"),
        "variables": {},
    }
    
    for var_name, var_def in ENV_VARS_DEF.items():
        value = os.getenv(var_name, "")
        status["variables"][var_name] = {
            "name": var_name,
            "description": var_def["description"],
            "example": var_def.get("example", ""),
            "set": bool(value),
            "value": "***" if var_def.get("sensitive") else value,
            "required_for": var_def.get("required_for", []),
        }
    
    return status


def print_env_status(status: Dict[str, Any]) -> None:
    """列印環境變數狀態"""
    # 設定 UTF-8 編碼輸出
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except:
            pass
    
    print("=" * 70)
    print("五常系統環境變數狀態")
    print("=" * 70)
    print(f"檢查時間: {status['timestamp']}\n")
    
    # 按狀態分組
    set_vars = []
    unset_vars = []
    
    for var_name, var_info in status["variables"].items():
        if var_info["set"]:
            set_vars.append(var_info)
        else:
            unset_vars.append(var_info)
    
    # 已設定的變數
    if set_vars:
        print("【已設定】")
        for var in set_vars:
            value_display = var["value"]
            print(f"  [OK] {var['name']}")
            print(f"      說明: {var['description']}")
            if not var.get("sensitive"):
                print(f"      值: {value_display}")
            print()
    
    # 未設定的變數
    if unset_vars:
        print("【未設定】")
        for var in unset_vars:
            print(f"  [X] {var['name']}")
            print(f"      說明: {var['description']}")
            print(f"      範例: {var['example']}")
            if var.get("required_for"):
                print(f"      用途: {', '.join(var['required_for'])}")
            print()
    
    print("=" * 70)


def generate_env_file(format: str = "ps1") -> str:
    """生成環境變數設定檔案內容"""
    if format == "ps1":
        lines = [
            "# 五常系統環境變數設定檔",
            "# 使用方式: .\\env_vars.ps1",
            "# 或: Get-Content env_vars.ps1 | Invoke-Expression",
            "",
        ]
        
        for var_name, var_def in ENV_VARS_DEF.items():
            example = var_def.get("example", "")
            description = var_def["description"]
            lines.append(f"# {description}")
            if example:
                lines.append(f"# $env:{var_name} = \"{example}\"")
            else:
                lines.append(f"# $env:{var_name} = \"\"")
            lines.append("")
        
        return "\n".join(lines)
    
    elif format == "bat":
        lines = [
            "@echo off",
            "REM 五常系統環境變數設定檔",
            "REM 使用方式: call env_vars.bat",
            "",
        ]
        
        for var_name, var_def in ENV_VARS_DEF.items():
            example = var_def.get("example", "")
            description = var_def["description"]
            lines.append(f"REM {description}")
            if example:
                lines.append(f"REM set {var_name}={example}")
            else:
                lines.append(f"REM set {var_name}=")
            lines.append("")
        
        return "\n".join(lines)
    
    elif format == "json":
        config = {
            "description": "五常系統環境變數配置",
            "variables": {
                name: {
                    "description": defn["description"],
                    "example": defn.get("example", ""),
                    "value": "",  # 使用者填入
                }
                for name, defn in ENV_VARS_DEF.items()
            },
        }
        return json.dumps(config, ensure_ascii=False, indent=2)
    
    else:
        raise ValueError(f"不支援的格式: {format}")


def set_env_var(var_name: str, value: str, persistent: bool = False) -> bool:
    """設定環境變數"""
    if var_name not in ENV_VARS_DEF:
        print(f"[錯誤] 未知的環境變數: {var_name}", file=sys.stderr)
        return False
    
    # 當前會話
    os.environ[var_name] = value
    
    # 永久設定（Windows）
    if persistent:
        if sys.platform == "win32":
            try:
                import winreg
                
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    "Environment",
                    0,
                    winreg.KEY_SET_VALUE,
                )
                winreg.SetValueEx(key, var_name, 0, winreg.REG_EXPAND_SZ, value)
                winreg.CloseKey(key)
                print(f"[OK] 永久設定: {var_name}")
                return True
            except Exception as e:
                print(f"[錯誤] 無法設定永久環境變數: {e}", file=sys.stderr)
                print("[提示] 請以管理員權限執行", file=sys.stderr)
                return False
        else:
            print("[警告] 非 Windows 系統，不支援永久設定", file=sys.stderr)
            return False
    
    return True


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="五常系統環境變數統一設定工具")
    parser.add_argument(
        "action",
        choices=["status", "generate", "set"],
        help="操作：status(查看狀態), generate(生成設定檔), set(設定變數)",
    )
    parser.add_argument(
        "--var",
        type=str,
        help="變數名稱（用於 set 操作）",
    )
    parser.add_argument(
        "--value",
        type=str,
        help="變數值（用於 set 操作）",
    )
    parser.add_argument(
        "--persistent",
        action="store_true",
        help="永久設定（寫入系統環境變數，僅 Windows）",
    )
    parser.add_argument(
        "--format",
        choices=["ps1", "bat", "json"],
        default="ps1",
        help="生成設定檔格式（用於 generate 操作）",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="輸出檔案路徑（用於 generate 操作）",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式輸出（用於 status 操作）",
    )
    
    args = parser.parse_args()
    
    if args.action == "status":
        status = get_env_status()
        if args.json:
            print(json.dumps(status, ensure_ascii=False, indent=2))
        else:
            print_env_status(status)
    
    elif args.action == "generate":
        content = generate_env_file(args.format)
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(content, encoding="utf-8")
            print(f"[OK] 已生成設定檔: {output_path}")
        else:
            print(content)
    
    elif args.action == "set":
        if not args.var or not args.value:
            print("[錯誤] --var 和 --value 參數為必填", file=sys.stderr)
            return 1
        
        success = set_env_var(args.var, args.value, args.persistent)
        if success:
            if args.persistent:
                print("[提示] 永久設定需要重新啟動終端機或重新登入才能生效")
            else:
                print(f"[OK] 已設定當前會話環境變數: {args.var}")
            return 0
        else:
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
