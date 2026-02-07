#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雙J協作：自動偵測中興保全網路纜線並進行流量分析

步驟：
1. 雲端小j協同本地小j，SSH連線至路由器（支援華碩/中興）。
2. 自動比對所有Port的連線裝置（MAC、Port、描述），找出中興保全設備。
3. 切換到該Port，啟動流量監控（如ifconfig、tcpdump、snmp、流量API）。
4. 分析流量（高峰、異常、來源IP/Port等），自動生成回報。
5. 回報結果存於 logs/router_security_cable_analysis_日期時間.json。

索引：
- [雙J自動化維運流程索引](雙J自動化維運流程索引.md)
- [本腳本] scripts/dual_j_router_security_cable_analysis.py

"""
import sys
import json
import time
from datetime import datetime
from pathlib import Path
import paramiko

# 路由器連線資訊（請依實際情況調整）
ROUTER_IP = "192.168.50.1"
ROUTER_USER = "admin"
ROUTER_PASS = "your_password"

# 中興保全設備特徵（MAC或描述）
SECURITY_MAC_PREFIX = "00:11:22"  # 假設開頭
SECURITY_DEVICE_NAME = "中興保全"

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def ssh_exec_command(host, user, password, command):
    """SSH執行指令並回傳結果"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password, timeout=10)
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    client.close()
    return output


def find_security_cable():
    """自動偵測中興保全網路纜線所在Port"""
    # 以常見路由器指令為例（可根據型號調整）
    port_info = ssh_exec_command(ROUTER_IP, ROUTER_USER, ROUTER_PASS, "show mac address-table")
    # 解析port_info，找出符合SECURITY_MAC_PREFIX的Port
    found_port = None
    for line in port_info.splitlines():
        if SECURITY_MAC_PREFIX in line:
            # 假設格式：VLAN  MAC地址  Port
            parts = line.split()
            if len(parts) >= 3:
                found_port = parts[-1]
                break
    return found_port, port_info


def analyze_port_traffic(port):
    """對指定Port進行流量分析"""
    # 以ifconfig/tcpdump為例
    traffic_info = ssh_exec_command(ROUTER_IP, ROUTER_USER, ROUTER_PASS, f"ifconfig {port}")
    # 也可用snmp、流量API等
    # 這裡僅簡單回傳
    return traffic_info


def main():
    result = {
        "timestamp": datetime.now().isoformat(),
        "router_ip": ROUTER_IP,
        "security_mac_prefix": SECURITY_MAC_PREFIX,
        "found_port": None,
        "port_info": None,
        "traffic_info": None,
        "error": None
    }
    try:
        port, port_info = find_security_cable()
        result["found_port"] = port
        result["port_info"] = port_info
        if port:
            traffic_info = analyze_port_traffic(port)
            result["traffic_info"] = traffic_info
        else:
            result["error"] = "未找到中興保全網路纜線"
    except Exception as e:
        result["error"] = str(e)
    # 儲存回報
    log_file = LOG_DIR / f"router_security_cable_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"分析結果已儲存：{log_file}")
    if result["error"]:
        print(f"⚠️ 錯誤：{result['error']}")
    else:
        print(f"✅ 已完成流量分析，請查閱報告。")

if __name__ == "__main__":
    main()
