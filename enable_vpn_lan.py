#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enable_vpn_lan.py

啟用 VPN 區網功能

功能：
- 檢查 VPN 連接狀態
- 啟用 VPN 網段內的網路發現
- 配置 VPN 區網設定
- 確保 VPN 網段內電腦可互相看見
"""

import sys
import subprocess
import platform
import socket
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def get_vpn_ip():
    """獲取 VPN IP 地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.8.0.1", 80))
        ip = s.getsockname()[0]
        s.close()
        if ip.startswith("10.8.0."):
            return ip
    except:
        pass
    return None


def check_vpn_connection():
    """檢查 VPN 連接狀態"""
    print("【檢查 VPN 連接狀態】")
    
    vpn_ip = get_vpn_ip()
    if vpn_ip:
        print(f"  ✓ VPN 已連接")
        print(f"  VPN IP: {vpn_ip}")
        print(f"  VPN 網段: 10.8.0.0/24")
    else:
        print("  ✗ VPN 未連接")
        print("  請先建立 VPN 連接")
        return False
    
    print()
    return True


def enable_vpn_network_discovery():
    """啟用 VPN 網段內的網路發現"""
    print("【啟用 VPN 區網網路發現】")
    
    if platform.system() != "Windows":
        print("  此功能僅適用於 Windows")
        return False
    
    script = """
    # 啟用網路發現（針對 VPN 介面）
    Set-NetFirewallRule -DisplayGroup "Network Discovery" -Enabled True -Profile Domain,Private,Public
    
    # 啟用檔案和印表機共用
    Set-NetFirewallRule -DisplayGroup "File and Printer Sharing" -Enabled True -Profile Domain,Private,Public
    
    # 確保 VPN 介面的網路設定檔為 Private
    $vpnAdapter = Get-NetAdapter | Where-Object {$_.InterfaceDescription -like "*TAP*" -or $_.InterfaceDescription -like "*TUN*" -or $_.InterfaceDescription -like "*VPN*"}
    if ($vpnAdapter) {
        $vpnProfile = Get-NetConnectionProfile -InterfaceIndex $vpnAdapter.ifIndex -ErrorAction SilentlyContinue
        if ($vpnProfile) {
            Set-NetConnectionProfile -InterfaceIndex $vpnAdapter.ifIndex -NetworkCategory Private
            Write-Host "VPN 介面已設定為私人網路"
        }
    }
    
    Write-Host "VPN 區網網路發現已啟用"
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
            print("  ✓ VPN 區網網路發現已啟用")
            print(result.stdout)
        else:
            print("  ⚠️  啟用過程有警告")
            print(result.stderr)
        return True
    except Exception as e:
        print(f"  ✗ 啟用失敗: {e}")
        return False


def scan_vpn_network():
    """掃描 VPN 網段內的設備"""
    print("【掃描 VPN 網段 (10.8.0.0/24)】")
    
    vpn_ip = get_vpn_ip()
    if not vpn_ip:
        print("  ✗ VPN 未連接，無法掃描")
        return
    
    print(f"  本機 VPN IP: {vpn_ip}")
    print("  正在掃描 VPN 網段...")
    print()
    
    accessible_hosts = []
    for i in range(1, 255):
        if i == int(vpn_ip.split('.')[-1]):
            continue  # 跳過本機
        
        host = f"10.8.0.{i}"
        try:
            result = subprocess.run(
                ["ping", "-n", "1", "-w", "500", host],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=2
            )
            
            if result.returncode == 0:
                print(f"  ✓ {host} 可達")
                accessible_hosts.append(host)
        except:
            pass
    
    print()
    if accessible_hosts:
        print(f"  找到 {len(accessible_hosts)} 個可達的主機:")
        for host in accessible_hosts:
            print(f"    - {host}")
    else:
        print("  ✗ 未找到其他可達的主機")
    print()


def test_vpn_smb_connection():
    """測試 VPN 網段內的 SMB 連接"""
    print("【測試 VPN 網段內的 SMB 連接】")
    
    test_hosts = [
        "10.8.0.1",
        "10.8.0.2",
        "10.8.0.10",
    ]
    
    for host in test_hosts:
        # 測試常見的共享名稱
        test_shares = [
            f"\\\\{host}\\wuchang",
            f"\\\\{host}\\wuchang V5.1.0",
            f"\\\\{host}\\share",
            f"\\\\{host}\\wuchang-V5.1.0",
        ]
        
        for share_path in test_shares:
            try:
                path = Path(share_path)
                if path.exists():
                    print(f"  ✓ 找到共享: {share_path}")
                    try:
                        items = list(path.iterdir())
                        print(f"     內容: {len(items)} 個項目")
                    except:
                        print(f"     內容: 無法列出")
            except:
                pass
    
    print()


def configure_vpn_network_sharing():
    """配置 VPN 網路共用"""
    print("【配置 VPN 網路共用】")
    
    if platform.system() != "Windows":
        print("  此功能僅適用於 Windows")
        return
    
    script = """
    # 確保 SMB 服務運行
    $smb = Get-Service -Name LanmanServer -ErrorAction SilentlyContinue
    if ($smb -and $smb.Status -ne 'Running') {
        Start-Service -Name LanmanServer
        Write-Host "SMB 服務已啟動"
    }
    
    # 檢查 VPN 介面的網路設定
    $vpnAdapters = Get-NetAdapter | Where-Object {
        $_.InterfaceDescription -like "*TAP*" -or 
        $_.InterfaceDescription -like "*TUN*" -or 
        $_.InterfaceDescription -like "*OpenVPN*"
    }
    
    foreach ($adapter in $vpnAdapters) {
        Write-Host "VPN 介面: $($adapter.Name)"
        $profile = Get-NetConnectionProfile -InterfaceIndex $adapter.ifIndex -ErrorAction SilentlyContinue
        if ($profile) {
            Set-NetConnectionProfile -InterfaceIndex $adapter.ifIndex -NetworkCategory Private
            Write-Host "  已設定為私人網路"
        }
    }
    
    Write-Host "VPN 網路共用配置完成"
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
        if result.stderr:
            print(result.stderr)
    except Exception as e:
        print(f"  ✗ 配置失敗: {e}")
    print()


def main():
    """主函數"""
    print("=" * 70)
    print("啟用 VPN 區網功能")
    print("確保 VPN 網段內電腦可互相看見")
    print("=" * 70)
    print()
    
    # 檢查 VPN 連接
    if not check_vpn_connection():
        print("請先建立 VPN 連接後再執行此腳本")
        return
    
    # 啟用 VPN 區網網路發現
    enable_vpn_network_discovery()
    
    # 配置 VPN 網路共用
    configure_vpn_network_sharing()
    
    # 掃描 VPN 網段
    scan_vpn_network()
    
    # 測試 SMB 連接
    test_vpn_smb_connection()
    
    print("=" * 70)
    print("【完成】")
    print("VPN 區網功能已啟用")
    print()
    print("【下一步】")
    print("1. 確認伺服器端也啟用了網路發現")
    print("2. 嘗試訪問 VPN 網段內的共享:")
    print("   \\\\10.8.0.1\\wuchang")
    print("   \\\\10.8.0.1\\share")
    print("3. 執行檔案同步:")
    print("   python sync_all_profiles.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
