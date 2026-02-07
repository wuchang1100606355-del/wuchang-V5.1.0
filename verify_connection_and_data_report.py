#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
驗證伺服器連線環境及數據報告
不依賴 SSH 認證，使用可用的連線方式
"""

import os
import sys
import json
import socket
import subprocess
from pathlib import Path
from datetime import datetime

SERVER_IP = "192.168.50.249"
SERVER_PORTS = {
    22: "SSH",
    80: "HTTP",
    443: "HTTPS",
    8069: "Odoo",
    8080: "AI/Web",
    8766: "Cloud Sync",
    3001: "Status Dashboard",
    3389: "RDP",
    5432: "PostgreSQL"
}

def print_section(title):
    """打印章節標題"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_result(label, status, details=""):
    """打印結果"""
    status_symbol = "[OK]" if status else "[FAIL]"
    status_color = "\033[92m" if status else "\033[91m"
    reset_color = "\033[0m"
    print(f"{status_color}{status_symbol}{reset_color} {label}")
    if details:
        print(f"    {details}")

def test_port(ip, port, timeout=3):
    """測試端口"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def verify_connection_environment():
    """驗證連線環境"""
    print_section("一、伺服器連線環境驗證")
    
    results = {
        "ping": False,
        "ports": {},
        "network_info": {},
        "summary": {}
    }
    
    # 1. Ping 測試
    print("\n[1] 基本連線測試 (Ping)")
    try:
        if os.name == 'nt':
            result = subprocess.run(
                ["ping", "-n", "4", SERVER_IP],
                capture_output=True,
                text=True,
                timeout=10
            )
        else:
            result = subprocess.run(
                ["ping", "-c", "4", SERVER_IP],
                capture_output=True,
                text=True,
                timeout=10
            )
        
        if result.returncode == 0:
            print_result("Ping 測試", True, "伺服器可達")
            results["ping"] = True
            
            # 提取延遲信息
            output = result.stdout
            for line in output.split("\n"):
                if "平均" in line or "Average" in line or "time=" in line:
                    print(f"    {line.strip()}")
        else:
            print_result("Ping 測試", False, "無法 ping 通伺服器")
    except Exception as e:
        print_result("Ping 測試", False, f"錯誤: {e}")
    
    # 2. 端口掃描
    print("\n[2] 服務端口掃描")
    open_ports = []
    closed_ports = []
    
    for port, name in SERVER_PORTS.items():
        is_open = test_port(SERVER_IP, port, timeout=3)
        results["ports"][port] = {
            "name": name,
            "open": is_open
        }
        
        if is_open:
            open_ports.append(port)
            print_result(f"{name} ({port})", True, "開啟")
        else:
            closed_ports.append(port)
            print(f"    {name} ({port}): [CLOSED]")
    
    results["summary"]["open_ports"] = open_ports
    results["summary"]["closed_ports"] = closed_ports
    
    # 3. 網絡信息
    print("\n[3] 本地網絡配置")
    try:
        if os.name == 'nt':
            result = subprocess.run(
                ["ipconfig"],
                capture_output=True,
                text=True
            )
            output = result.stdout
            
            # 查找本機 IP
            for line in output.split("\n"):
                if "IPv4" in line and "192.168.50" in line:
                    ip_line = line.strip()
                    print(f"    本機 IP: {ip_line}")
                    results["network_info"]["local_ip"] = ip_line
                    break
            
            # ARP 表
            result = subprocess.run(
                ["arp", "-a", SERVER_IP],
                capture_output=True,
                text=True
            )
            if SERVER_IP in result.stdout:
                print_result("ARP 表", True, "找到伺服器 MAC 地址")
                for line in result.stdout.split("\n"):
                    if SERVER_IP in line:
                        print(f"      {line.strip()}")
                        results["network_info"]["arp_entry"] = line.strip()
                        break
    except Exception as e:
        print(f"    [WARN] 無法獲取網絡信息: {e}")
    
    return results

def verify_data_accessibility():
    """驗證數據可訪問性"""
    print_section("二、數據可訪問性驗證")
    
    results = {
        "ssh_available": False,
        "rdp_available": False,
        "http_available": False,
        "services_available": False,
        "recommendations": []
    }
    
    # 檢查 SSH
    ssh_open = test_port(SERVER_IP, 22)
    results["ssh_available"] = ssh_open
    if ssh_open:
        print_result("SSH 端口", True, "可用於檔案傳輸")
        results["recommendations"].append("使用 SSH 進行檔案比對和同步")
    else:
        print_result("SSH 端口", False, "無法使用 SSH")
    
    # 檢查 RDP
    rdp_open = test_port(SERVER_IP, 3389)
    results["rdp_available"] = rdp_open
    if rdp_open:
        print_result("RDP 端口", True, "可用於遠端桌面連線")
        results["recommendations"].append("使用 RDP 連線到伺服器進行手動操作")
    else:
        print_result("RDP 端口", False, "無法使用 RDP")
    
    # 檢查 HTTP 服務
    http_open = test_port(SERVER_IP, 80) or test_port(SERVER_IP, 443)
    results["http_available"] = http_open
    if http_open:
        print_result("HTTP/HTTPS", True, "可用於 Web 訪問")
        results["recommendations"].append("通過 Web 界面訪問服務")
    else:
        print_result("HTTP/HTTPS", False, "無法使用 Web 訪問")
    
    # 檢查應用服務
    service_ports = [8069, 8080, 8766, 3001]
    available_services = [p for p in service_ports if test_port(SERVER_IP, p)]
    results["services_available"] = len(available_services) > 0
    
    if available_services:
        print_result("應用服務", True, f"{len(available_services)} 個服務可用: {available_services}")
    else:
        print_result("應用服務", False, "所有應用服務端口都關閉")
        results["recommendations"].append("檢查伺服器上的服務是否已啟動")
    
    return results

def generate_file_comparison_guide():
    """生成檔案比對指南"""
    print_section("三、地端檔案比對方案")
    
    print("\n由於 SSH 認證尚未配置，提供以下檔案比對方案：")
    
    print("\n[方案 1] 使用 RDP 遠端桌面（推薦）")
    print("  1. 使用遠端桌面連線到伺服器:")
    print(f"     mstsc /v:{SERVER_IP}:3389")
    print("  2. 在伺服器上執行檔案比對")
    print("  3. 或使用檔案總管訪問伺服器共享資料夾")
    
    print("\n[方案 2] 配置 SSH 認證後使用自動比對")
    print("  1. 確認伺服器用戶名和密碼")
    print("  2. 執行 SSH 密鑰部署:")
    print("     python deploy_ssh_key.py")
    print("  3. 或使用:")
    print("     .\\setup_ssh_auto.ps1")
    print("  4. 然後執行檔案比對:")
    print("     python verify_and_compare_files.py")
    
    print("\n[方案 3] 使用網絡共享（如果已配置）")
    print("  1. 在伺服器上設定共享資料夾")
    print("  2. 從本機映射網絡驅動器:")
    print(f"     net use Z: \\\\{SERVER_IP}\\wuchang")
    print("  3. 使用本地檔案比對工具比較檔案")
    
    print("\n[方案 4] 使用現有的 PowerShell 腳本")
    print("  1. 修改 quick_compare_sync.ps1 中的伺服器配置")
    print("  2. 配置 SSH 認證後執行:")
    print("     .\\quick_compare_sync.ps1")

def generate_summary_report(connection_results, data_results):
    """生成總結報告"""
    print_section("四、驗證總結報告")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "server_ip": SERVER_IP,
        "connection_environment": connection_results,
        "data_accessibility": data_results,
        "status": {
            "server_reachable": connection_results["ping"],
            "services_available": data_results["services_available"],
            "file_comparison_ready": data_results["ssh_available"] or data_results["rdp_available"]
        }
    }
    
    print("\n連線環境狀態:")
    print(f"  伺服器可達: {'是' if report['status']['server_reachable'] else '否'}")
    print(f"  開啟端口數: {len(connection_results['summary']['open_ports'])}")
    print(f"  關閉端口數: {len(connection_results['summary']['closed_ports'])}")
    
    print("\n數據訪問狀態:")
    print(f"  SSH 可用: {'是' if data_results['ssh_available'] else '否'}")
    print(f"  RDP 可用: {'是' if data_results['rdp_available'] else '否'}")
    print(f"  應用服務: {'可用' if data_results['services_available'] else '不可用'}")
    print(f"  檔案比對就緒: {'是' if report['status']['file_comparison_ready'] else '否'}")
    
    print("\n建議操作:")
    for i, rec in enumerate(data_results['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    # 保存報告
    report_file = Path("connection_verification_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] 報告已保存: {report_file}")
    
    return report

def main():
    """主函數"""
    print("=" * 80)
    print("  伺服器連線環境及數據驗證報告")
    print(f"  目標伺服器: {SERVER_IP}")
    print("=" * 80)
    
    # 步驟 1: 驗證連線環境
    connection_results = verify_connection_environment()
    
    # 步驟 2: 驗證數據可訪問性
    data_results = verify_data_accessibility()
    
    # 步驟 3: 生成檔案比對指南
    generate_file_comparison_guide()
    
    # 步驟 4: 生成總結報告
    report = generate_summary_report(connection_results, data_results)
    
    print("\n" + "=" * 80)
    print("  驗證完成")
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] 操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
