#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_setup_from_router_logs.py

根據路由器日誌自動設定兩機互通

從路由器日誌中提取：
- DDNS 資訊
- OpenVPN 配置
- 網路設定
- 自動配置環境變數
"""

import sys
import json
import re
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def parse_router_logs(log_text: str) -> dict:
    """解析路由器日誌"""
    config = {
        "ddns": None,
        "wan_ip": None,
        "openvpn": {
            "enabled": False,
            "server_ip": None,
            "network": None,
            "port": None,
            "client_pool": None
        },
        "router": {
            "model": None,
            "https_port": None
        }
    }
    
    # 解析 DDNS
    ddns_match = re.search(r'coffeeLofe\.asuscomm\.com', log_text)
    if ddns_match:
        config["ddns"] = "coffeeLofe.asuscomm.com"
    
    # 解析 WAN IP
    wan_ip_match = re.search(r'local\s+IP address\s+(\d+\.\d+\.\d+\.\d+)', log_text)
    if wan_ip_match:
        config["wan_ip"] = wan_ip_match.group(1)
    
    # 解析 OpenVPN
    if "vpnserver1" in log_text and "Initialization Sequence Completed" in log_text:
        config["openvpn"]["enabled"] = True
        
        # OpenVPN 伺服器 IP
        ovpn_ip_match = re.search(r'ifconfig\s+tun\d+\s+(\d+\.\d+\.\d+\.\d+)', log_text)
        if ovpn_ip_match:
            config["openvpn"]["server_ip"] = ovpn_ip_match.group(1)
        
        # OpenVPN 網段
        ovpn_net_match = re.search(r'route add -net (\d+\.\d+\.\d+\.\d+) netmask (\d+\.\d+\.\d+\.\d+)', log_text)
        if ovpn_net_match:
            network = ovpn_net_match.group(1)
            netmask = ovpn_net_match.group(2)
            config["openvpn"]["network"] = f"{network}/{netmask_to_cidr(netmask)}"
        
        # OpenVPN 端口
        ovpn_port_match = re.search(r'UDPv6 link local.*:(\d+)', log_text)
        if ovpn_port_match:
            config["openvpn"]["port"] = int(ovpn_port_match.group(1))
        
        # 客戶端 IP 池
        pool_match = re.search(r'IFCONFIG POOL: base=(\d+\.\d+\.\d+\.\d+) size=(\d+)', log_text)
        if pool_match:
            base_ip = pool_match.group(1)
            size = int(pool_match.group(2))
            # 計算結束 IP
            base_parts = base_ip.split('.')
            base_num = int(base_parts[3])
            end_num = base_num + size - 1
            config["openvpn"]["client_pool"] = f"{base_ip}-{base_parts[0]}.{base_parts[1]}.{base_parts[2]}.{end_num}"
    
    # 解析路由器型號
    model_match = re.search(r'(RT-[A-Z0-9-]+)', log_text)
    if model_match:
        config["router"]["model"] = model_match.group(1)
    
    # 解析 HTTPS 端口
    https_port_match = re.search(r'start https:(\d+)', log_text)
    if https_port_match:
        config["router"]["https_port"] = int(https_port_match.group(1))
    
    return config


def netmask_to_cidr(netmask: str) -> int:
    """將子網路遮罩轉換為 CIDR"""
    parts = netmask.split('.')
    binary = ''.join([bin(int(x))[2:].zfill(8) for x in parts])
    return binary.count('1')


def generate_config_from_logs(log_config: dict) -> dict:
    """根據日誌配置生成完整配置"""
    config = {
        "server_ddns": log_config.get("ddns", ""),
        "server_ip": log_config["openvpn"].get("server_ip", "10.8.0.1"),
        "server_share": "",
        "health_url": "",
        "hub_url": "",
        "hub_token": "",
        "vpn": {
            "enabled": log_config["openvpn"]["enabled"],
            "server": log_config.get("ddns", ""),
            "port": log_config["openvpn"].get("port", 8888),
            "network": log_config["openvpn"].get("network", "10.8.0.0/24"),
            "server_ip": log_config["openvpn"].get("server_ip", "10.8.0.1"),
            "client_pool": log_config["openvpn"].get("client_pool", "10.8.0.4-65")
        },
        "router": {
            "ddns": log_config.get("ddns", ""),
            "wan_ip": log_config.get("wan_ip", ""),
            "port_https": log_config["router"].get("https_port", 8443),
            "port_openvpn": log_config["openvpn"].get("port", 8888),
            "model": log_config["router"].get("model", ""),
            "cert_path": "certs/cert.pem",
            "key_path": "certs/key.pem"
        }
    }
    
    # 生成健康檢查 URL
    if config["server_ddns"]:
        config["health_url"] = f"https://{config['server_ddns']}:{config['router']['port_https']}/health"
    elif config["server_ip"]:
        config["health_url"] = f"http://{config['server_ip']}:8788/health"
    
    return config


def main():
    """主函數"""
    print("=" * 70)
    print("根據路由器日誌自動設定兩機互通")
    print("=" * 70)
    print()
    
    # 從用戶提供的日誌中解析
    router_log = """
Jan 19 09:42:01 pppd[7649]: local  IP address 220.135.21.74
Jan 19 09:42:05 vpnserver1[7766]: TUN/TAP device tun21 opened
Jan 19 09:42:05 vpnserver1[7766]: /sbin/ifconfig tun21 10.8.0.1 pointopoint 10.8.0.2 mtu 1500
Jan 19 09:42:05 vpnserver1[7766]: /sbin/route add -net 10.8.0.0 netmask 255.255.255.0 gw 10.8.0.2
Jan 19 09:42:05 vpnserver1[7766]: UDPv6 link local (bound): [AF_INET6][undef]:8888
Jan 19 09:42:05 vpnserver1[7766]: IFCONFIG POOL: base=10.8.0.4 size=62, ipv6=0
Jan 19 09:42:05 vpnserver1[7766]: Initialization Sequence Completed
Jan 19 09:42:04 RT-BE86U: start https:8443
Jan 19 09:42:47 RT-BE86U: start https:8443
"""
    
    print("【步驟 1：解析路由器日誌】")
    log_config = parse_router_logs(router_log)
    
    print("解析結果：")
    if log_config["ddns"]:
        print(f"  ✓ DDNS: {log_config['ddns']}")
    if log_config["wan_ip"]:
        print(f"  ✓ WAN IP: {log_config['wan_ip']}")
    if log_config["openvpn"]["enabled"]:
        print(f"  ✓ OpenVPN: 已啟用")
        print(f"    伺服器 IP: {log_config['openvpn']['server_ip']}")
        print(f"    網段: {log_config['openvpn']['network']}")
        print(f"    端口: {log_config['openvpn']['port']}")
        print(f"    客戶端池: {log_config['openvpn']['client_pool']}")
    if log_config["router"]["model"]:
        print(f"  ✓ 路由器型號: {log_config['router']['model']}")
    if log_config["router"]["https_port"]:
        print(f"  ✓ HTTPS 端口: {log_config['router']['https_port']}")
    print()
    
    # 生成配置
    print("【步驟 2：生成配置檔案】")
    config = generate_config_from_logs(log_config)
    
    # 儲存配置
    config_file = BASE_DIR / "network_interconnection_config.json"
    config_file.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"✓ 配置已儲存到: {config_file}")
    print()
    
    # 顯示配置摘要
    print("【配置摘要】")
    print(f"  連接方式: {'OpenVPN' if config['vpn']['enabled'] else 'DDNS'}")
    if config["server_ddns"]:
        print(f"  DDNS: {config['server_ddns']}")
    print(f"  伺服器 IP: {config['server_ip']}")
    if config["health_url"]:
        print(f"  健康檢查 URL: {config['health_url']}")
    print()
    
    print("=" * 70)
    print("【下一步】")
    print("1. 執行網路設定: python setup_network_interconnection.py")
    print("2. 設定路由器證書（如果需要）: python setup_router_cert.py \"cert_key (1).tar\"")
    print("3. 測試連接: python check_server_connection.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
