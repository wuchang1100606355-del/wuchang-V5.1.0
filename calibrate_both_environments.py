#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
calibrate_both_environments.py

兩方環境校準

功能：
- 檢查本地和伺服器端環境變數
- 比對兩方配置
- 校準環境變數
- 確保兩方環境一致
"""

import sys
import json
import os
import requests
from pathlib import Path
from typing import Dict, Any, List

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def get_local_environment() -> Dict[str, str]:
    """獲取本地環境變數"""
    import platform
    
    env_vars = {}
    
    # 從系統環境變數讀取（Windows 和 Unix 都支援）
    env_keys = [
        "WUCHANG_HEALTH_URL",
        "WUCHANG_COPY_TO",
        "WUCHANG_HUB_URL",
        "WUCHANG_HUB_TOKEN",
        "WUCHANG_SYSTEM_DB_DIR",
        "WUCHANG_WORKSPACE_OUTDIR",
        "WUCHANG_PII_ENABLED",
        "WUCHANG_DEV_MODE",
        "WUCHANG_VPN_CONFIG_PATH",
    ]
    
    for key in env_keys:
        value = os.getenv(key, "")
        if not value and platform.system() == "Windows":
            # Windows 下嘗試從註冊表讀取用戶環境變數
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key_handle:
                    try:
                        value, _ = winreg.QueryValueEx(key_handle, key)
                    except FileNotFoundError:
                        pass
            except:
                pass
        if value:
            env_vars[key] = value
    
    # 從 network_interconnection_config.json 讀取
    config_file = BASE_DIR / "network_interconnection_config.json"
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text(encoding="utf-8"))
            if config.get("health_url") and not env_vars.get("WUCHANG_HEALTH_URL"):
                env_vars["WUCHANG_HEALTH_URL"] = config["health_url"]
            if config.get("server_share") and not env_vars.get("WUCHANG_COPY_TO"):
                env_vars["WUCHANG_COPY_TO"] = config["server_share"]
            if config.get("hub_url") and not env_vars.get("WUCHANG_HUB_URL"):
                env_vars["WUCHANG_HUB_URL"] = config["hub_url"]
            if config.get("hub_token") and not env_vars.get("WUCHANG_HUB_TOKEN"):
                env_vars["WUCHANG_HUB_TOKEN"] = config["hub_token"]
        except:
            pass
    
    return env_vars


def get_server_environment(health_url: str = None) -> Dict[str, str]:
    """獲取伺服器端環境變數"""
    if not health_url:
        health_url = os.getenv("WUCHANG_HEALTH_URL", "")
    
    if not health_url:
        return {}
    
    server_env = {}
    
    # 嘗試多種方式獲取伺服器端環境變數
    base_url = health_url.replace('/health', '').rstrip('/')
    
    # 方式 1: 通過 /api/deployment/status
    try:
        response = requests.get(
            f"{base_url}/api/deployment/status",
            timeout=5,
            verify=False  # 暫時忽略 SSL 驗證
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                env_status = data.get("status", {}).get("environment", {})
                if isinstance(env_status, dict):
                    server_env.update(env_status.get("values", {}))
    except:
        pass
    
    # 方式 2: 通過 /api/workspace/alignment
    try:
        response = requests.get(
            f"{base_url}/api/workspace/alignment",
            timeout=5,
            verify=False
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                alignment = data.get("alignment", {})
                if isinstance(alignment, dict):
                    # 從對齊資訊中提取環境變數
                    for key, value in alignment.items():
                        if key.startswith("WUCHANG_") and value:
                            server_env[key] = value
    except:
        pass
    
    # 方式 3: 嘗試從伺服器端配置檔案讀取（如果可訪問）
    copy_to = os.getenv("WUCHANG_COPY_TO", "")
    if copy_to:
        try:
            server_config_path = Path(copy_to) / "network_interconnection_config.json"
            if server_config_path.exists():
                config = json.loads(server_config_path.read_text(encoding="utf-8"))
                if config.get("health_url") and not server_env.get("WUCHANG_HEALTH_URL"):
                    server_env["WUCHANG_HEALTH_URL"] = config["health_url"]
                if config.get("server_share") and not server_env.get("WUCHANG_COPY_TO"):
                    server_env["WUCHANG_COPY_TO"] = config["server_share"]
                if config.get("hub_url") and not server_env.get("WUCHANG_HUB_URL"):
                    server_env["WUCHANG_HUB_URL"] = config["hub_url"]
        except:
            pass
    
    return server_env


def compare_environments(local_env: Dict[str, str], server_env: Dict[str, str]) -> Dict[str, Any]:
    """比對兩方環境變數"""
    comparison = {
        "local_only": {},
        "server_only": {},
        "different": {},
        "same": {},
        "missing_critical": []
    }
    
    all_keys = set(local_env.keys()) | set(server_env.keys())
    critical_vars = ["WUCHANG_HEALTH_URL", "WUCHANG_COPY_TO"]
    
    for key in all_keys:
        local_val = local_env.get(key, "")
        server_val = server_env.get(key, "")
        
        if not local_val and not server_val:
            continue
        
        if local_val and not server_val:
            comparison["local_only"][key] = local_val
        elif server_val and not local_val:
            comparison["server_only"][key] = server_val
        elif local_val != server_val:
            comparison["different"][key] = {
                "local": local_val,
                "server": server_val
            }
        else:
            comparison["same"][key] = local_val
    
    # 檢查關鍵變數
    for var in critical_vars:
        if not local_env.get(var) and not server_env.get(var):
            comparison["missing_critical"].append(var)
    
    return comparison


def calibrate_environment(comparison: Dict[str, Any], target: str = "local") -> List[str]:
    """校準環境變數"""
    suggestions = []
    
    if target == "local":
        # 以伺服器端為準，更新本地
        for key, value in comparison.get("server_only", {}).items():
            suggestions.append(f"設定本地 {key} = {value}")
        
        for key, diff in comparison.get("different", {}).items():
            suggestions.append(f"更新本地 {key} = {diff['server']} (目前: {diff['local']})")
    else:
        # 以本地為準，更新伺服器端
        for key, value in comparison.get("local_only", {}).items():
            suggestions.append(f"設定伺服器端 {key} = {value}")
        
        for key, diff in comparison.get("different", {}).items():
            suggestions.append(f"更新伺服器端 {key} = {diff['local']} (目前: {diff['server']})")
    
    return suggestions


def apply_local_calibration(comparison: Dict[str, Any], dry_run: bool = False) -> bool:
    """應用本地環境校準"""
    print("【應用本地環境校準】")
    
    if dry_run:
        print("  [模擬模式] 將執行以下操作：")
        suggestions = calibrate_environment(comparison, target="local")
        for suggestion in suggestions:
            print(f"    - {suggestion}")
        return True
    
    # 實際應用（需要權限）
    print("  ⚠️  實際應用需要手動設定環境變數")
    print("  建議使用 setup_env_vars.py 或手動設定")
    return False


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="兩方環境校準")
    parser.add_argument("--target", choices=["local", "server", "both"], default="both", help="校準目標")
    parser.add_argument("--dry-run", action="store_true", help="模擬執行")
    parser.add_argument("--apply", action="store_true", help="實際應用校準")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("兩方環境校準")
    print("=" * 70)
    print()
    
    # 獲取本地環境
    print("【步驟 1：檢查本地環境】")
    local_env = get_local_environment()
    print(f"  找到 {len(local_env)} 個環境變數")
    for key, value in local_env.items():
        display_value = "***" if "TOKEN" in key or "SECRET" in key else value
        print(f"    {key} = {display_value}")
    print()
    
    # 獲取伺服器端環境
    print("【步驟 2：檢查伺服器端環境】")
    health_url = local_env.get("WUCHANG_HEALTH_URL", "")
    server_env = get_server_environment(health_url)
    
    if server_env:
        print(f"  找到 {len(server_env)} 個環境變數")
        for key, value in server_env.items():
            display_value = "***" if "TOKEN" in key or "SECRET" in key else value
            print(f"    {key} = {display_value}")
    else:
        print("  ⚠️  無法獲取伺服器端環境變數")
        print("  可能原因：")
        print("    1. 伺服器端服務未運行")
        print("    2. 健康檢查 URL 未設定或不可訪問")
        print("    3. API 端點不可用")
    print()
    
    # 比對環境
    print("【步驟 3：比對兩方環境】")
    comparison = compare_environments(local_env, server_env)
    
    print(f"  相同的變數: {len(comparison['same'])} 個")
    print(f"  僅本地有: {len(comparison['local_only'])} 個")
    print(f"  僅伺服器有: {len(comparison['server_only'])} 個")
    print(f"  不同的變數: {len(comparison['different'])} 個")
    
    if comparison["missing_critical"]:
        print(f"  ⚠️  缺少關鍵變數: {', '.join(comparison['missing_critical'])}")
    print()
    
    # 顯示差異詳情
    if comparison["different"]:
        print("【環境變數差異】")
        for key, diff in comparison["different"].items():
            print(f"  {key}:")
            print(f"    本地: {diff['local']}")
            print(f"    伺服器: {diff['server']}")
        print()
    
    if comparison["local_only"]:
        print("【僅本地有的變數】")
        for key, value in comparison["local_only"].items():
            display_value = "***" if "TOKEN" in key or "SECRET" in key else value
            print(f"  {key} = {display_value}")
        print()
    
    if comparison["server_only"]:
        print("【僅伺服器有的變數】")
        for key, value in comparison["server_only"].items():
            display_value = "***" if "TOKEN" in key or "SECRET" in key else value
            print(f"  {key} = {display_value}")
        print()
    
    # 生成校準建議
    print("【步驟 4：校準建議】")
    
    if args.target in ("local", "both"):
        local_suggestions = calibrate_environment(comparison, target="local")
        if local_suggestions:
            print("  本地校準建議：")
            for suggestion in local_suggestions:
                print(f"    - {suggestion}")
        else:
            print("  ✓ 本地環境無需校準")
        print()
    
    if args.target in ("server", "both"):
        server_suggestions = calibrate_environment(comparison, target="server")
        if server_suggestions:
            print("  伺服器端校準建議：")
            for suggestion in server_suggestions:
                print(f"    - {suggestion}")
        else:
            print("  ✓ 伺服器端環境無需校準")
        print()
    
    # 應用校準
    if args.apply:
        if args.target in ("local", "both"):
            apply_local_calibration(comparison, dry_run=args.dry_run)
    
    # 生成校準腳本
    print("【步驟 5：生成校準腳本】")
    calibration_script = BASE_DIR / "apply_environment_calibration.ps1"
    
    script_content = ["# 環境校準腳本（自動生成）", ""]
    
    if comparison.get("server_only") or comparison.get("different"):
        script_content.append("# 本地環境校準（以伺服器端為準）")
        for key, value in comparison.get("server_only", {}).items():
            # 轉義 PowerShell 特殊字元
            escaped_value = value.replace('"', '`"').replace('$', '`$')
            script_content.append(f'[System.Environment]::SetEnvironmentVariable("{key}", "{escaped_value}", "User")')
        for key, diff in comparison.get("different", {}).items():
            server_value = diff.get("server", "")
            escaped_value = server_value.replace('"', '`"').replace('$', '`$')
            script_content.append(f'[System.Environment]::SetEnvironmentVariable("{key}", "{escaped_value}", "User")')
        script_content.append("")
    
    if comparison.get("local_only") or comparison.get("different"):
        script_content.append("# 伺服器端環境校準建議（需要手動執行）")
        for key, value in comparison.get("local_only", {}).items():
            script_content.append(f"# 設定伺服器端 {key} = {value}")
        for key, diff in comparison.get("different", {}).items():
            script_content.append(f"# 設定伺服器端 {key} = {diff['local']}")
        script_content.append("")
    
    if len(script_content) > 2:
        calibration_script.write_text("\n".join(script_content), encoding="utf-8")
        print(f"  ✓ 已生成校準腳本: {calibration_script}")
        print("  執行方式: .\\apply_environment_calibration.ps1")
    else:
        print("  ✓ 無需生成校準腳本（環境已一致）")
    print()
    
    # 生成報告
    report = {
        "timestamp": __import__("time").strftime("%Y-%m-%dT%H:%M:%S%z"),
        "local_environment": local_env,
        "server_environment": server_env,
        "comparison": comparison,
        "calibration_suggestions": {
            "local": calibrate_environment(comparison, target="local"),
            "server": calibrate_environment(comparison, target="server")
        }
    }
    
    report_file = BASE_DIR / "environment_calibration_report.json"
    report_file.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    print("=" * 70)
    print("【完成】")
    print(f"環境校準報告已儲存到: {report_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
