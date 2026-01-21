#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_network_share_issues.py

修復網路共享問題

根據 Microsoft 支援文件：
- https://learn.microsoft.com/zh-cn/answers/questions/3860772/network-share-issues
- https://learn.microsoft.com/en-us/answers/questions/1650278/smb-network-share-issue

功能：
- 檢查和啟用文件和打印機共享
- 檢查功能發現服務狀態
- 檢查和配置 SMB 版本（建議使用 SMB 2.0 或更高版本）
- 診斷網路共享連接問題
"""

import sys
import os
import subprocess
import platform
from pathlib import Path
from typing import Dict, Any, List

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def run_powershell(cmd: str, capture_output: bool = True) -> Dict[str, Any]:
    """執行 PowerShell 命令"""
    try:
        result = subprocess.run(
            ["powershell", "-Command", cmd],
            capture_output=capture_output,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30
        )
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout.strip() if capture_output else "",
            "stderr": result.stderr.strip() if capture_output else "",
        }
    except Exception as e:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
        }


def check_file_sharing() -> Dict[str, Any]:
    """檢查文件和打印機共享狀態"""
    print("【步驟 1：檢查文件和打印機共享】")
    
    # 檢查網路設定檔
    cmd = """
    $profiles = Get-NetConnectionProfile
    foreach ($profile in $profiles) {
        Write-Output "Profile: $($profile.Name), NetworkCategory: $($profile.NetworkCategory)"
        $netAdapter = Get-NetAdapter -InterfaceIndex $profile.InterfaceIndex
        Write-Output "  Adapter: $($netAdapter.Name)"
    }
    """
    
    result = run_powershell(cmd)
    
    # 檢查文件和打印機共享防火牆規則
    cmd2 = """
    $rules = Get-NetFirewallRule | Where-Object {
        $_.DisplayName -like "*文件和打印機共享*" -or
        $_.DisplayName -like "*File and Printer Sharing*"
    }
    foreach ($rule in $rules) {
        Write-Output "$($rule.DisplayName): $($rule.Enabled), Direction: $($rule.Direction)"
    }
    """
    
    result2 = run_powershell(cmd2)
    
    print(f"  網路設定檔: {'✓ 已檢查' if result['success'] else '✗ 檢查失敗'}")
    if result['success'] and result['stdout']:
        print("  設定檔資訊:")
        for line in result['stdout'].split('\n'):
            if line.strip():
                print(f"    {line}")
    
    print(f"  防火牆規則: {'✓ 已檢查' if result2['success'] else '✗ 檢查失敗'}")
    if result2['success'] and result2['stdout']:
        print("  規則狀態:")
        for line in result2['stdout'].split('\n'):
            if line.strip():
                print(f"    {line}")
    
    print()
    return {
        "profiles": result,
        "firewall_rules": result2,
    }


def check_function_discovery_services() -> Dict[str, Any]:
    """檢查功能發現服務"""
    print("【步驟 2：檢查功能發現服務】")
    
    services = [
        "FDResPub",  # 功能發現資源發布
        "FDHost",    # 功能發現提供程序主機
    ]
    
    results = {}
    
    for service in services:
        cmd = f"""
        $svc = Get-Service -Name "{service}" -ErrorAction SilentlyContinue
        if ($svc) {{
            Write-Output "$($svc.Name): Status=$($svc.Status), StartType=$($svc.StartType)"
        }} else {{
            Write-Output "{service}: Not Found"
        }}
        """
        
        result = run_powershell(cmd)
        results[service] = result
        
        if result['success']:
            output = result['stdout']
            if "Status=Running" in output and "StartType=Automatic" in output:
                print(f"  ✓ {service}: 運行中且設為自動啟動")
            elif "Status=Running" in output:
                print(f"  ⚠️  {service}: 運行中但未設為自動啟動")
            elif "Not Found" in output:
                print(f"  ✗ {service}: 未找到")
            else:
                print(f"  ⚠️  {service}: {output}")
        else:
            print(f"  ✗ {service}: 檢查失敗")
    
    print()
    return results


def check_smb_configuration() -> Dict[str, Any]:
    """檢查 SMB 配置"""
    print("【步驟 3：檢查 SMB 配置】")
    
    # 檢查 SMB 版本
    cmd = """
    $smb1 = (Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -ErrorAction SilentlyContinue)
    $smb2 = (Get-SmbServerConfiguration).EnableSMB2Protocol
    $smb3 = (Get-SmbServerConfiguration).EnableSMB3Protocol
    
    Write-Output "SMB1: $($smb1.State)"
    Write-Output "SMB2: $smb2"
    Write-Output "SMB3: $smb3"
    """
    
    result = run_powershell(cmd)
    
    if result['success']:
        output = result['stdout']
        print("  SMB 版本狀態:")
        for line in output.split('\n'):
            if line.strip():
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if key == "SMB1":
                    if "Enabled" in value or "已啟用" in value:
                        print(f"    ⚠️  SMB1: {value} (不建議使用，有安全風險)")
                    else:
                        print(f"    ✓ SMB1: {value} (已停用，符合安全建議)")
                elif key == "SMB2":
                    if value == "True":
                        print(f"    ✓ SMB2: 已啟用")
                    else:
                        print(f"    ✗ SMB2: 未啟用")
                elif key == "SMB3":
                    if value == "True":
                        print(f"    ✓ SMB3: 已啟用")
                    else:
                        print(f"    ⚠️  SMB3: 未啟用")
    else:
        print(f"  ✗ 檢查 SMB 配置失敗: {result['stderr']}")
    
    print()
    return result


def enable_file_sharing(dry_run: bool = False) -> bool:
    """啟用文件和打印機共享"""
    print("【步驟 4：啟用文件和打印機共享】")
    
    if dry_run:
        print("  [模擬模式] 將執行以下操作：")
        print("    1. 啟用所有網路設定檔的文件和打印機共享")
        print("    2. 啟用相關防火牆規則")
        return True
    
    # 啟用文件和打印機共享（所有設定檔）
    cmd = """
    $profiles = Get-NetConnectionProfile
    foreach ($profile in $profiles) {
        Set-NetConnectionProfile -InterfaceIndex $profile.InterfaceIndex -NetworkCategory Private
        Enable-NetFirewallRule -DisplayGroup "文件和打印機共享"
        Enable-NetFirewallRule -DisplayGroup "File and Printer Sharing"
    }
    Write-Output "File sharing enabled for all profiles"
    """
    
    result = run_powershell(cmd)
    
    if result['success']:
        print("  ✓ 文件和打印機共享已啟用")
    else:
        print(f"  ✗ 啟用失敗: {result['stderr']}")
    
    print()
    return result['success']


def enable_function_discovery_services(dry_run: bool = False) -> bool:
    """啟用功能發現服務"""
    print("【步驟 5：啟用功能發現服務】")
    
    services = [
        "FDResPub",  # 功能發現資源發布
        "FDHost",    # 功能發現提供程序主機
    ]
    
    if dry_run:
        print("  [模擬模式] 將執行以下操作：")
        for service in services:
            print(f"    1. 設定 {service} 為自動啟動")
            print(f"    2. 啟動 {service} 服務")
        return True
    
    success_count = 0
    
    for service in services:
        cmd = f"""
        $svc = Get-Service -Name "{service}" -ErrorAction SilentlyContinue
        if ($svc) {{
            Set-Service -Name "{service}" -StartupType Automatic
            Start-Service -Name "{service}"
            Write-Output "{service}: Enabled and Started"
        }} else {{
            Write-Output "{service}: Not Found"
        }}
        """
        
        result = run_powershell(cmd)
        
        if result['success'] and "Enabled and Started" in result['stdout']:
            print(f"  ✓ {service}: 已啟用並啟動")
            success_count += 1
        else:
            print(f"  ✗ {service}: 啟用失敗")
    
    print()
    return success_count == len(services)


def configure_smb_version(enable_smb2: bool = True, enable_smb3: bool = True, disable_smb1: bool = True, dry_run: bool = False) -> bool:
    """配置 SMB 版本"""
    print("【步驟 6：配置 SMB 版本】")
    
    if dry_run:
        print("  [模擬模式] 將執行以下操作：")
        if enable_smb2:
            print("    1. 啟用 SMB 2.0")
        if enable_smb3:
            print("    2. 啟用 SMB 3.0")
        if disable_smb1:
            print("    3. 停用 SMB 1.0（安全建議）")
        return True
    
    success = True
    
    # 啟用 SMB 2.0
    if enable_smb2:
        cmd = "Set-SmbServerConfiguration -EnableSMB2Protocol $true -Force"
        result = run_powershell(cmd)
        if result['success']:
            print("  ✓ SMB 2.0 已啟用")
        else:
            print(f"  ✗ 啟用 SMB 2.0 失敗: {result['stderr']}")
            success = False
    
    # 啟用 SMB 3.0
    if enable_smb3:
        cmd = "Set-SmbServerConfiguration -EnableSMB3Protocol $true -Force"
        result = run_powershell(cmd)
        if result['success']:
            print("  ✓ SMB 3.0 已啟用")
        else:
            print(f"  ✗ 啟用 SMB 3.0 失敗: {result['stderr']}")
            success = False
    
    # 停用 SMB 1.0（安全建議）
    if disable_smb1:
        cmd = """
        $feature = Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -ErrorAction SilentlyContinue
        if ($feature -and $feature.State -eq "Enabled") {
            Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -NoRestart
            Write-Output "SMB1 disabled"
        } else {
            Write-Output "SMB1 already disabled or not available"
        }
        """
        result = run_powershell(cmd)
        if result['success']:
            if "disabled" in result['stdout'].lower():
                print("  ✓ SMB 1.0 已停用（符合安全建議）")
            else:
                print("  ✓ SMB 1.0 已停用或不可用")
        else:
            print(f"  ⚠️  停用 SMB 1.0 時發生錯誤: {result['stderr']}")
            # 這不是致命錯誤，繼續
    
    print()
    return success


def test_network_share(share_path: str = None) -> Dict[str, Any]:
    """測試網路共享連接"""
    print("【步驟 7：測試網路共享連接】")
    
    if not share_path:
        share_path = os.getenv("WUCHANG_COPY_TO", "")
        if not share_path:
            print("  ⚠️  未指定共享路徑，跳過測試")
            print("  提示: 設定 WUCHANG_COPY_TO 環境變數或提供 --test-share 參數")
            print()
            return {"skipped": True}
    
    print(f"  測試共享路徑: {share_path}")
    
    # 測試連接
    cmd = f"""
    $share = "{share_path}"
    try {{
        $test = Test-Path -Path $share -ErrorAction Stop
        if ($test) {{
            $items = Get-ChildItem -Path $share -ErrorAction SilentlyContinue
            Write-Output "SUCCESS: Share accessible, Items: $($items.Count)"
        }} else {{
            Write-Output "FAILED: Share path not accessible"
        }}
    }} catch {{
        Write-Output "ERROR: $($_.Exception.Message)"
    }}
    """
    
    result = run_powershell(cmd)
    
    if result['success']:
        output = result['stdout']
        if "SUCCESS" in output:
            print(f"  ✓ 共享連接成功")
            print(f"    {output}")
        elif "FAILED" in output:
            print(f"  ✗ 共享連接失敗")
            print(f"    {output}")
        else:
            print(f"  ⚠️  測試結果: {output}")
    else:
        print(f"  ✗ 測試失敗: {result['stderr']}")
    
    print()
    return result


def main():
    """主函數"""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="修復網路共享問題")
    parser.add_argument("--dry-run", action="store_true", help="模擬執行，不實際修改")
    parser.add_argument("--test-share", default=None, help="測試指定的共享路徑")
    parser.add_argument("--enable-smb1", action="store_true", help="啟用 SMB 1.0（不建議，僅用於相容舊系統）")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("網路共享問題修復工具")
    print("=" * 70)
    print()
    print("參考文件：")
    print("  - https://learn.microsoft.com/zh-cn/answers/questions/3860772/network-share-issues")
    print("  - https://learn.microsoft.com/en-us/answers/questions/1650278/smb-network-share-issue")
    print()
    
    if args.dry_run:
        print("⚠️  模擬模式：不會實際修改系統設定")
        print()
    
    # 檢查當前狀態
    check_file_sharing()
    check_function_discovery_services()
    check_smb_configuration()
    
    # 執行修復
    if not args.dry_run:
        print("【開始修復】")
        print()
    
    enable_file_sharing(dry_run=args.dry_run)
    enable_function_discovery_services(dry_run=args.dry_run)
    configure_smb_version(
        enable_smb2=True,
        enable_smb3=True,
        disable_smb1=not args.enable_smb1,
        dry_run=args.dry_run
    )
    
    # 測試連接
    test_network_share(args.test_share)
    
    print("=" * 70)
    print("【完成】")
    print()
    print("修復建議：")
    print("  1. 確保兩端都使用 SMB 2.0 或更高版本")
    print("  2. 檢查防火牆規則是否允許文件和打印機共享")
    print("  3. 確保功能發現服務正在運行")
    print("  4. 如果仍有問題，檢查網路設定檔是否設為「私人」")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
