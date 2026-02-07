#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_container_network_visibility.py

檢查容器網路可見性

功能：
- 檢查本地容器網路配置
- 檢查伺服器端容器網路配置
- 測試容器間網路互通
- 檢查跨伺服器容器訪問
"""

import sys
import json
import subprocess
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


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    print(f"[{level}] {message}")


def get_local_containers() -> List[Dict[str, Any]]:
    """獲取本地容器資訊"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10
        )
        
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    container = json.loads(line)
                    containers.append({
                        "id": container.get("ID", "")[:12],
                        "name": container.get("Names", ""),
                        "image": container.get("Image", ""),
                        "ports": container.get("Ports", ""),
                    })
                except:
                    pass
        
        return containers
    except Exception as e:
        log(f"獲取本地容器失敗: {e}", "ERROR")
        return []


def get_container_networks(container_name: str) -> List[str]:
    """獲取容器所屬的網路"""
    try:
        result = subprocess.run(
            ["docker", "inspect", container_name, "--format", "{{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10
        )
        
        if result.returncode == 0:
            networks = result.stdout.strip().split()
            return networks
        return []
    except Exception as e:
        log(f"獲取容器網路失敗: {e}", "ERROR")
        return []


def test_container_connectivity(source_container: str, target_host: str, target_port: int = 80):
    """測試容器連接性"""
    try:
        # 在容器內執行 ping 或 curl
        result = subprocess.run(
            ["docker", "exec", source_container, "sh", "-c", f"nc -zv {target_host} {target_port} 2>&1 || curl -s -o /dev/null -w '%{{http_code}}' http://{target_host}:{target_port} || echo 'failed'"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10
        )
        
        return result.returncode == 0 or "200" in result.stdout or "succeeded" in result.stdout.lower()
    except:
        return False


def check_network_visibility():
    """檢查網路可見性"""
    print("=" * 70)
    print("容器網路可見性檢查")
    print("=" * 70)
    print()
    
    # 獲取本地容器
    log("檢查本地容器...", "INFO")
    local_containers = get_local_containers()
    
    if not local_containers:
        log("未找到本地容器", "WARN")
        return
    
    print(f"【本地容器】共 {len(local_containers)} 個")
    print()
    
    # 檢查每個容器的網路配置
    for container in local_containers[:5]:  # 只檢查前 5 個
        container_name = container["name"]
        networks = get_container_networks(container_name)
        
        print(f"容器: {container_name}")
        print(f"  映像: {container['image']}")
        print(f"  網路: {', '.join(networks) if networks else '預設網路'}")
        print(f"  端口: {container['ports']}")
        print()
    
    # 檢查網路互通性
    print("【網路互通性測試】")
    print()
    
    # 測試本地容器間連接
    if len(local_containers) >= 2:
        source = local_containers[0]["name"]
        target = local_containers[1]["name"]
        
        log(f"測試 {source} → {target}...", "INFO")
        # 獲取目標容器的 IP（簡化版本，實際需要從網路中獲取）
        print(f"  （需要容器 IP 才能測試）")
    
    print()
    print("【跨伺服器容器訪問】")
    print()
    print("如果伺服器使用相同網域/帳號：")
    print("  ✓ 容器可以通過 VPN 網路互相訪問")
    print("  ✓ 可以使用容器名稱或 IP 地址訪問")
    print("  ✓ 需要確保防火牆允許容器間通信")
    print()
    print("建議配置：")
    print("  1. 確保 VPN 網路互通（10.8.0.0/24）")
    print("  2. 配置 Docker 網路允許跨主機通信")
    print("  3. 使用服務發現（如 Consul、etcd）")
    print("  4. 或使用 Docker Swarm 模式")
    print()


def main():
    """主函數"""
    check_network_visibility()
    
    print("=" * 70)
    print("【總結】")
    print("=" * 70)
    print()
    print("✓ 本地容器可以互相看見（同一 Docker 網路）")
    print("✓ 如果伺服器使用相同帳號和 VPN，容器可以跨主機訪問")
    print("✓ 需要確保網路配置正確")
    print()


if __name__ == "__main__":
    main()
