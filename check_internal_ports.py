#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_internal_ports.py

檢查內部端口配置

檢查所有容器的端口映射和內部端口
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")


def get_container_ports():
    """取得所有容器的端口配置"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}|{{.Ports}}"],
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            return []
        
        containers = []
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            parts = line.split('|', 1)
            if len(parts) == 2:
                containers.append({
                    "name": parts[0],
                    "ports": parts[1]
                })
        
        return containers
    except Exception as e:
        log(f"取得容器端口時發生錯誤: {e}", "ERROR")
        return []


def parse_port_mapping(port_string: str) -> List[Dict]:
    """解析端口映射字串"""
    mappings = []
    
    if not port_string or port_string == "None":
        return mappings
    
    # 分割多個端口映射
    port_parts = port_string.split(', ')
    
    for part in port_parts:
        part = part.strip()
        if not part:
            continue
        
        # 解析格式: 0.0.0.0:8069->8069/tcp 或 [::]:8069->8069/tcp
        if '->' in part:
            host_part, container_part = part.split('->', 1)
            container_port = container_part.split('/')[0]
            
            # 提取主機端口
            if ':' in host_part:
                if '[' in host_part:
                    # IPv6 格式: [::]:8069
                    host_port = host_part.split(':')[-1].rstrip(']')
                else:
                    # IPv4 格式: 0.0.0.0:8069
                    host_port = host_part.split(':')[-1]
            else:
                host_port = host_part
            
            mappings.append({
                "host_port": host_port,
                "container_port": container_port,
                "protocol": container_part.split('/')[1] if '/' in container_part else "tcp"
            })
        else:
            # 只有容器端口（未映射）
            port_info = part.split('/')
            container_port = port_info[0]
            protocol = port_info[1] if len(port_info) > 1 else "tcp"
            
            mappings.append({
                "host_port": None,
                "container_port": container_port,
                "protocol": protocol
            })
    
    return mappings


def get_service_info():
    """取得服務資訊"""
    services = {
        "Odoo ERP 系統": {
            "container": "wuchangv510-wuchang-web-1",
            "default_port": 8069,
            "description": "主要業務系統"
        },
        "Open WebUI (AI)": {
            "container": "wuchangv510-open-webui-1",
            "default_port": 8080,
            "description": "AI 智能助手介面"
        },
        "Portainer": {
            "container": "wuchangv510-portainer-1",
            "default_port": 9000,
            "description": "容器管理介面"
        },
        "Uptime Kuma": {
            "container": "wuchangv510-uptime-kuma-1",
            "default_port": 3001,
            "description": "系統監控"
        },
        "Ollama": {
            "container": "wuchangv510-ollama-1",
            "default_port": 11434,
            "description": "AI 模型服務"
        },
        "Caddy": {
            "container": "wuchangv510-caddy-1",
            "default_port": [80, 443],
            "description": "反向代理伺服器"
        },
        "Caddy UI": {
            "container": "wuchangv510-caddy-ui-1",
            "default_port": [8081, 8444],
            "description": "Caddy 管理介面"
        },
        "PostgreSQL": {
            "container": "wuchangv510-db-1",
            "default_port": 5432,
            "description": "資料庫（僅內部）"
        },
        "Cloudflare Tunnel": {
            "container": "wuchangv510-cloudflared-1",
            "default_port": None,
            "description": "外網訪問隧道"
        }
    }
    
    return services


def main():
    """主函數"""
    print("=" * 70)
    print("內部端口檢查")
    print("=" * 70)
    print()
    
    # 取得容器端口
    log("取得容器端口配置...", "INFO")
    containers = get_container_ports()
    
    if not containers:
        log("未找到容器", "ERROR")
        return 1
    
    log(f"找到 {len(containers)} 個容器", "OK")
    print()
    
    # 取得服務資訊
    services = get_service_info()
    
    # 顯示服務端口
    print("=" * 70)
    print("【服務端口配置】")
    print("=" * 70)
    print()
    
    for service_name, service_info in services.items():
        container_name = service_info["container"]
        
        # 找到對應的容器
        container = next((c for c in containers if c["name"] == container_name), None)
        
        if container:
            port_mappings = parse_port_mapping(container["ports"])
            
            print(f"📦 {service_name}")
            print(f"   容器: {container_name}")
            print(f"   說明: {service_info['description']}")
            
            if port_mappings:
                print(f"   端口映射:")
                for mapping in port_mappings:
                    if mapping["host_port"]:
                        print(f"     外部端口 {mapping['host_port']} -> 內部端口 {mapping['container_port']}/{mapping['protocol']}")
                    else:
                        print(f"     內部端口 {mapping['container_port']}/{mapping['protocol']} (僅內部)")
            else:
                print(f"   端口: 未映射（僅內部）")
            
            # 顯示訪問地址
            if service_name == "Odoo ERP 系統":
                if port_mappings and port_mappings[0].get("host_port"):
                    print(f"   訪問: http://localhost:{port_mappings[0]['host_port']}")
            elif service_name == "Open WebUI (AI)":
                if port_mappings and port_mappings[0].get("host_port"):
                    print(f"   訪問: http://localhost:{port_mappings[0]['host_port']}")
            elif service_name == "Portainer":
                if port_mappings and port_mappings[0].get("host_port"):
                    print(f"   訪問: http://localhost:{port_mappings[0]['host_port']}")
            elif service_name == "Uptime Kuma":
                if port_mappings and port_mappings[0].get("host_port"):
                    print(f"   訪問: http://localhost:{port_mappings[0]['host_port']}")
            
            print()
        else:
            print(f"⚠️ {service_name} - 容器未運行")
            print()
    
    # 顯示所有容器端口
    print("=" * 70)
    print("【所有容器端口明細】")
    print("=" * 70)
    print()
    
    for container in sorted(containers, key=lambda x: x["name"]):
        port_mappings = parse_port_mapping(container["ports"])
        
        print(f"📦 {container['name']}")
        if port_mappings:
            for mapping in port_mappings:
                if mapping["host_port"]:
                    print(f"   外部:{mapping['host_port']} -> 內部:{mapping['container_port']}/{mapping['protocol']}")
                else:
                    print(f"   內部:{mapping['container_port']}/{mapping['protocol']} (僅內部)")
        else:
            print(f"   無端口映射（僅內部網絡）")
        print()
    
    # 內部網絡端口總結
    print("=" * 70)
    print("【內部網絡端口總結】")
    print("=" * 70)
    print()
    
    internal_ports = {}
    for container in containers:
        port_mappings = parse_port_mapping(container["ports"])
        for mapping in port_mappings:
            container_port = mapping["container_port"]
            if container_port not in internal_ports:
                internal_ports[container_port] = []
            internal_ports[container_port].append(container["name"])
    
    print("內部端口 -> 容器列表:")
    for port in sorted(internal_ports.keys(), key=lambda x: int(x)):
        containers_list = ", ".join(internal_ports[port])
        print(f"   {port}/tcp -> {containers_list}")
    
    print()
    
    # Cloudflare Tunnel 配置需要的端口
    print("=" * 70)
    print("【Cloudflare Tunnel 配置資訊】")
    print("=" * 70)
    print()
    
    print("配置檔案 (cloudflared/config.yml) 中的服務端口:")
    print()
    
    cloudflare_config = {
        "app.wuchang.org.tw": {
            "service": "wuchangv510-wuchang-web-1",
            "internal_port": 8069,
            "description": "Odoo ERP 系統"
        },
        "ai.wuchang.org.tw": {
            "service": "wuchangv510-open-webui-1",
            "internal_port": 8080,
            "description": "Open WebUI"
        },
        "admin.wuchang.org.tw": {
            "service": "wuchangv510-portainer-1",
            "internal_port": 9000,
            "description": "Portainer"
        },
        "monitor.wuchang.org.tw": {
            "service": "wuchangv510-uptime-kuma-1",
            "internal_port": 3001,
            "description": "Uptime Kuma"
        }
    }
    
    for domain, config in cloudflare_config.items():
        print(f"  {domain}")
        print(f"    服務: {config['service']}")
        print(f"    內部端口: {config['internal_port']}")
        print(f"    說明: {config['description']}")
        print()
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        log("操作已取消", "WARN")
        sys.exit(0)
    except Exception as e:
        log(f"發生錯誤: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)
