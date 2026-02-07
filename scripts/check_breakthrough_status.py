#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_breakthrough_status.py

檢查突破狀態

功能：
- 檢查 VPN 連接狀態
- 檢查區域網路設定
- 檢查網路發現狀態
- 檢查共享路徑可訪問性
- 生成突破狀態報告
"""

import sys
import subprocess
import socket
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def check_vpn_breakthrough():
    """檢查 VPN 突破狀態"""
    print("【VPN 區網突破檢查】")
    
    vpn_ip = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.8.0.1", 80))
        vpn_ip = s.getsockname()[0]
        s.close()
    except:
        pass
    
    if vpn_ip and vpn_ip.startswith("10.8.0."):
        print(f"  ✓ VPN 已連接")
        print(f"  VPN IP: {vpn_ip}")
        print(f"  VPN 網段: 10.8.0.0/24")
        
        # 測試 VPN 網段內的主機
        print("  測試 VPN 網段內主機:")
        for ip in ["10.8.0.1", "10.8.0.2", "10.8.0.10"]:
            try:
                result = subprocess.run(
                    ["ping", "-n", "1", "-w", "500", ip],
                    capture_output=True,
                    timeout=2
                )
                if result.returncode == 0:
                    print(f"    ✓ {ip} 可達")
                else:
                    print(f"    ✗ {ip} 不可達")
            except:
                print(f"    ✗ {ip} 測試失敗")
        
        return True
    else:
        print("  ✗ VPN 未連接")
        return False


def check_local_network_breakthrough():
    """檢查區域網路突破狀態"""
    print()
    print("【區域網路突破檢查】")
    
    # 檢查網路設定檔
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-NetConnectionProfile | Select-Object NetworkCategory | Format-List"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=10
        )
        
        if "Private" in result.stdout:
            print("  ✓ 網路設定檔: Private (私人)")
        else:
            print("  ⚠️  網路設定檔: 非 Private")
    except:
        pass
    
    # 檢查網路發現
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-NetFirewallRule -DisplayGroup 'Network Discovery' | Where-Object {$_.Enabled -eq $true} | Measure-Object | Select-Object -ExpandProperty Count"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=10
        )
        
        count = result.stdout.strip()
        if count and int(count) > 0:
            print(f"  ✓ 網路發現: 已啟用 ({count} 個規則)")
        else:
            print("  ✗ 網路發現: 未啟用")
    except:
        print("  ⚠️  無法檢查網路發現狀態")
    
    # 檢查檔案共用
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-NetFirewallRule -DisplayGroup 'File and Printer Sharing' | Where-Object {$_.Enabled -eq $true} | Measure-Object | Select-Object -ExpandProperty Count"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=10
        )
        
        count = result.stdout.strip()
        if count and int(count) > 0:
            print(f"  ✓ 檔案共用: 已啟用 ({count} 個規則)")
        else:
            print("  ✗ 檔案共用: 未啟用")
    except:
        print("  ⚠️  無法檢查檔案共用狀態")
    
    # 檢查 SMB 服務
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-Service -Name LanmanServer | Select-Object -ExpandProperty Status"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=10
        )
        
        status = result.stdout.strip()
        if "Running" in status:
            print("  ✓ SMB 服務: 運行中")
        else:
            print("  ✗ SMB 服務: 未運行")
    except:
        print("  ⚠️  無法檢查 SMB 服務狀態")


def check_share_accessibility():
    """檢查共享路徑可訪問性"""
    print()
    print("【共享路徑可訪問性檢查】")
    
    test_paths = [
        "\\\\HOME-COMMPUT\\wuchang V5.1.0",
        "\\\\HOME-COMPUTER\\wuchang V5.1.0",
        "\\\\10.8.0.1\\wuchang",
        "\\\\10.8.0.1\\share",
        "Z:\\",
    ]
    
    accessible = []
    for path_str in test_paths:
        try:
            path = Path(path_str)
            if path.exists():
                print(f"  ✓ 可訪問: {path_str}")
                accessible.append(path_str)
                try:
                    items = list(path.iterdir())
                    print(f"     內容: {len(items)} 個項目")
                except:
                    print(f"     內容: 無法列出")
            else:
                print(f"  ✗ 不可訪問: {path_str}")
        except Exception as e:
            print(f"  ✗ 錯誤: {path_str} - {str(e)[:50]}")
    
    return accessible


def main():
    """主函數"""
    print("=" * 70)
    print("突破狀態檢查報告")
    print("=" * 70)
    print()
    
    # 檢查 VPN 突破
    vpn_ok = check_vpn_breakthrough()
    
    # 檢查區域網路突破
    check_local_network_breakthrough()
    
    # 檢查共享可訪問性
    accessible = check_share_accessibility()
    
    # 總結
    print()
    print("=" * 70)
    print("【突破狀態總結】")
    print("=" * 70)
    
    if vpn_ok:
        print("✓ VPN 區網: 已突破")
        print("  - VPN 連接正常")
        print("  - 可在 VPN 網段內通信")
    else:
        print("✗ VPN 區網: 未突破")
        print("  - VPN 未連接")
    
    print()
    
    if accessible:
        print(f"✓ 共享訪問: 已突破 ({len(accessible)} 個路徑可訪問)")
        for path in accessible:
            print(f"  - {path}")
    else:
        print("✗ 共享訪問: 未突破")
        print("  - 所有測試路徑均不可訪問")
        print("  - 需要確認共享伺服器狀態")
    
    print()
    print("=" * 70)
    
    # 生成突破報告
    breakthrough_report = {
        "vpn_breakthrough": vpn_ok,
        "share_accessible": len(accessible) > 0,
        "accessible_paths": accessible,
        "timestamp": __import__("time").strftime("%Y-%m-%dT%H:%M:%S%z")
    }
    
    report_file = BASE_DIR / "breakthrough_status.json"
    import json
    report_file.write_text(
        json.dumps(breakthrough_report, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"突破狀態報告已儲存到: {report_file}")


if __name__ == "__main__":
    main()
