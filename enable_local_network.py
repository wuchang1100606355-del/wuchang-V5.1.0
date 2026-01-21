#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enable_local_network.py

啟用區域網路功能

功能：
- 檢查區域網路連接
- 啟用網路發現
- 啟用檔案和印表機共用
- 設定網路設定檔為私人
- 確保電腦可在區域網路中互相看見
"""

import sys
import subprocess
import platform
import socket

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass


def get_local_network_info():
    """獲取區域網路資訊"""
    print("【區域網路資訊】")
    
    try:
        # 獲取本機 IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        print(f"  本機 IP: {local_ip}")
        
        # 獲取子網路
        import ipaddress
        try:
            # 嘗試從 ipconfig 獲取子網路遮罩
            result = subprocess.run(
                ["ipconfig"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # 解析子網路
            lines = result.stdout.split('\n')
            for i, line in enumerate(lines):
                if local_ip in line and i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if "子網路" in next_line or "Subnet" in next_line:
                        print(f"  {next_line.strip()}")
        except:
            pass
        
        return local_ip
    except Exception as e:
        print(f"  ✗ 無法獲取網路資訊: {e}")
        return None


def enable_network_discovery():
    """啟用網路發現"""
    print("【啟用網路發現】")
    
    if platform.system() != "Windows":
        print("  此功能僅適用於 Windows")
        return False
    
    script = """
    # 啟用網路發現（所有設定檔）
    Set-NetFirewallRule -DisplayGroup "Network Discovery" -Enabled True -Profile Domain,Private,Public -ErrorAction SilentlyContinue
    
    # 啟用檔案和印表機共用
    Set-NetFirewallRule -DisplayGroup "File and Printer Sharing" -Enabled True -Profile Domain,Private,Public -ErrorAction SilentlyContinue
    
    # 設定所有連接為私人網路
    Get-NetConnectionProfile | Set-NetConnectionProfile -NetworkCategory Private -ErrorAction SilentlyContinue
    
    Write-Host "網路發現和檔案共用已啟用"
    """
    
    try:
        result = subprocess.run(
            ["powershell", "-Command", script],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=30
        )
        
        if result.returncode == 0:
            print("  ✓ 網路發現已啟用")
            print(result.stdout)
            return True
        else:
            print("  ⚠️  啟用過程有警告")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"  ✗ 啟用失敗: {e}")
        return False


def check_network_discovery_status():
    """檢查網路發現狀態"""
    print("【檢查網路發現狀態】")
    
    if platform.system() != "Windows":
        return
    
    script = """
    # 檢查網路發現規則
    $discovery = Get-NetFirewallRule -DisplayGroup "Network Discovery" | Where-Object {$_.Enabled -eq $true} | Measure-Object
    Write-Host "已啟用的網路發現規則: $($discovery.Count)"
    
    # 檢查檔案和印表機共用規則
    $sharing = Get-NetFirewallRule -DisplayGroup "File and Printer Sharing" | Where-Object {$_.Enabled -eq $true} | Measure-Object
    Write-Host "已啟用的檔案共用規則: $($sharing.Count)"
    
    # 檢查網路設定檔
    Write-Host "`n網路設定檔:"
    Get-NetConnectionProfile | Select-Object Name, NetworkCategory, InterfaceAlias | Format-Table
    """
    
    try:
        result = subprocess.run(
            ["powershell", "-Command", script],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=30
        )
        print(result.stdout)
    except Exception as e:
        print(f"  ✗ 檢查失敗: {e}")


def scan_local_network():
    """掃描區域網路上的電腦"""
    print("【掃描區域網路上的電腦】")
    
    try:
        # 掃描工作群組
        result = subprocess.run(
            ["net", "view"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=10
        )
        
        if result.returncode == 0:
            print("  工作群組電腦:")
            lines = result.stdout.split('\n')
            found_computers = False
            for line in lines:
                if '\\' in line and not line.strip().startswith('伺服器'):
                    print(f"    {line.strip()}")
                    found_computers = True
            if not found_computers:
                print("    未找到其他電腦")
        else:
            print("  ⚠️  掃描結果:")
            print(result.stderr)
    except Exception as e:
        print(f"  ✗ 掃描失敗: {e}")
    print()


def test_smb_sharing():
    """測試 SMB 共用服務"""
    print("【檢查 SMB 共用服務】")
    
    if platform.system() != "Windows":
        return
    
    script = """
    $smb = Get-Service -Name LanmanServer -ErrorAction SilentlyContinue
    if ($smb) {
        if ($smb.Status -eq 'Running') {
            Write-Host "  SMB 服務運行中"
        } else {
            Write-Host "  SMB 服務未運行，正在啟動..."
            Start-Service -Name LanmanServer
            Write-Host "  SMB 服務已啟動"
        }
    } else {
        Write-Host "  SMB 服務未找到"
    }
    """
    
    try:
        result = subprocess.run(
            ["powershell", "-Command", script],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=30
        )
        print(result.stdout)
    except Exception as e:
        print(f"  ✗ 檢查失敗: {e}")
    print()


def main():
    """主函數"""
    print("=" * 70)
    print("啟用區域網路功能")
    print("確保電腦可在區域網路中互相看見")
    print("=" * 70)
    print()
    
    if platform.system() != "Windows":
        print("此腳本僅適用於 Windows 系統")
        return
    
    # 獲取區域網路資訊
    local_ip = get_local_network_info()
    print()
    
    # 檢查當前狀態
    check_network_discovery_status()
    print()
    
    # 啟用網路發現
    enable_network_discovery()
    print()
    
    # 檢查 SMB 服務
    test_smb_sharing()
    
    # 再次檢查狀態
    print("【啟用後的狀態】")
    check_network_discovery_status()
    print()
    
    # 掃描區域網路
    scan_local_network()
    
    print("=" * 70)
    print("【完成】")
    print("區域網路功能已啟用")
    print()
    print("【下一步】")
    print("1. 確認兩台電腦都在同一個區域網路中")
    print("2. 確認兩台電腦的網路設定檔都是「私人」")
    print("3. 確認兩台電腦都啟用了網路發現")
    print("4. 嘗試訪問共享路徑:")
    print("   \\\\HOME-COMMPUT\\wuchang V5.1.0")
    print("   \\\\10.8.0.1\\wuchang (VPN 網段)")
    print("=" * 70)


if __name__ == "__main__":
    main()
