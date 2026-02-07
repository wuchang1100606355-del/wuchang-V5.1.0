#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enable_network_discovery.py

啟用網路發現和檔案共用

功能：
- 檢查網路設定檔
- 啟用網路發現
- 啟用檔案和印表機共用
- 檢查防火牆設定
- 確保電腦可在區網中互相看見
"""

import sys
import subprocess
import platform

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass


def run_powershell_command(script: str) -> tuple[bool, str]:
    """執行 PowerShell 命令"""
    try:
        result = subprocess.run(
            ["powershell", "-Command", script],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=30
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def check_network_profile():
    """檢查網路設定檔"""
    print("【檢查網路設定檔】")
    
    script = """
    Get-NetConnectionProfile | Select-Object Name, NetworkCategory, InterfaceAlias | Format-List
    """
    
    success, output = run_powershell_command(script)
    if success:
        print(output)
    else:
        print(f"✗ 檢查失敗: {output}")
    print()


def enable_network_discovery():
    """啟用網路發現"""
    print("【啟用網路發現】")
    
    script = """
    # 啟用網路發現（所有設定檔）
    Set-NetFirewallRule -DisplayGroup "Network Discovery" -Enabled True -Profile Domain,Private,Public
    
    # 啟用檔案和印表機共用
    Set-NetFirewallRule -DisplayGroup "File and Printer Sharing" -Enabled True -Profile Domain,Private,Public
    
    # 設定網路設定檔為 Private（私人）
    Get-NetConnectionProfile | Set-NetConnectionProfile -NetworkCategory Private
    
    Write-Host "網路發現和檔案共用已啟用"
    """
    
    success, output = run_powershell_command(script)
    if success:
        print("✓ 網路發現已啟用")
        print(output)
    else:
        print(f"⚠️  啟用過程有警告: {output}")
    print()


def check_network_discovery_status():
    """檢查網路發現狀態"""
    print("【檢查網路發現狀態】")
    
    script = """
    # 檢查網路發現規則
    Get-NetFirewallRule -DisplayGroup "Network Discovery" | Where-Object {$_.Enabled -eq $true} | Select-Object DisplayName, Enabled, Profile | Format-Table
    
    # 檢查檔案和印表機共用規則
    Get-NetFirewallRule -DisplayGroup "File and Printer Sharing" | Where-Object {$_.Enabled -eq $true} | Select-Object DisplayName, Enabled, Profile | Format-Table
    
    # 檢查網路設定檔
    Get-NetConnectionProfile | Select-Object Name, NetworkCategory | Format-Table
    """
    
    success, output = run_powershell_command(script)
    if success:
        print(output)
    else:
        print(f"✗ 檢查失敗: {output}")
    print()


def enable_smb_sharing():
    """啟用 SMB 共用"""
    print("【啟用 SMB 共用】")
    
    script = """
    # 啟用 SMB 1.0（如果需要）
    Enable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -NoRestart -ErrorAction SilentlyContinue
    
    # 檢查 SMB 服務狀態
    $smb = Get-Service -Name LanmanServer -ErrorAction SilentlyContinue
    if ($smb) {
        if ($smb.Status -ne 'Running') {
            Start-Service -Name LanmanServer
            Write-Host "SMB 服務已啟動"
        } else {
            Write-Host "SMB 服務運行中"
        }
    } else {
        Write-Host "SMB 服務未找到"
    }
    """
    
    success, output = run_powershell_command(script)
    if success:
        print("✓ SMB 共用設定完成")
        print(output)
    else:
        print(f"⚠️  設定過程有警告: {output}")
    print()


def scan_network_computers():
    """掃描網路上的電腦"""
    print("【掃描網路上的電腦】")
    
    script = """
    # 掃描工作群組中的電腦
    Write-Host "工作群組電腦:"
    net view /domain 2>&1 | Select-Object -First 20
    
    Write-Host "`n本機網路電腦:"
    net view 2>&1 | Select-Object -First 20
    """
    
    success, output = run_powershell_command(script)
    if success:
        print(output)
    else:
        print(f"⚠️  掃描結果: {output}")
    print()


def test_network_connectivity(target: str = "HOME-COMMPUT"):
    """測試網路連接"""
    print(f"【測試網路連接: {target}】")
    
    try:
        result = subprocess.run(
            ["ping", "-n", "2", target],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✓ {target} 可達")
            print(result.stdout)
        else:
            print(f"✗ {target} 不可達")
            print(result.stderr)
    except Exception as e:
        print(f"✗ 測試失敗: {e}")
    print()


def main():
    """主函數"""
    if platform.system() != "Windows":
        print("此腳本僅適用於 Windows 系統")
        return
    
    print("=" * 70)
    print("啟用網路發現和檔案共用")
    print("確保電腦可在區網中互相看見")
    print("=" * 70)
    print()
    
    # 檢查當前狀態
    check_network_profile()
    check_network_discovery_status()
    
    # 啟用網路發現
    enable_network_discovery()
    
    # 啟用 SMB 共用
    enable_smb_sharing()
    
    # 再次檢查狀態
    print("【啟用後的狀態】")
    check_network_discovery_status()
    
    # 測試連接
    test_network_connectivity("HOME-COMMPUT")
    
    # 掃描網路電腦
    scan_network_computers()
    
    print("=" * 70)
    print("【完成】")
    print("網路發現和檔案共用已啟用")
    print()
    print("【下一步】")
    print("1. 確認兩台電腦都在同一個網路中")
    print("2. 確認網路設定檔都是「私人」")
    print("3. 嘗試訪問共享路徑:")
    print("   \\\\HOME-COMMPUT\\wuchang V5.1.0")
    print("=" * 70)


if __name__ == "__main__":
    main()
