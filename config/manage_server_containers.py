#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
manage_server_containers.py

管理伺服器端容器

功能：
- 檢查伺服器端容器狀態
- 遠程管理容器（啟動、停止、重啟）
- 同步容器配置
- 監控容器健康狀態
"""

import sys
import json
import requests
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
SERVER_CONFIG_FILE = BASE_DIR / "server_container_config.json"


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    print(f"[{level}] {message}")


def check_local_containers() -> List[Dict[str, Any]]:
    """檢查本地容器狀態"""
    log("檢查本地容器狀態...", "INFO")
    
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10
        )
        
        if result.returncode != 0:
            log(f"檢查容器失敗: {result.stderr}", "ERROR")
            return []
        
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    container = json.loads(line)
                    containers.append({
                        "id": container.get("ID", "")[:12],
                        "name": container.get("Names", ""),
                        "image": container.get("Image", ""),
                        "status": container.get("Status", ""),
                        "ports": container.get("Ports", ""),
                    })
                except:
                    pass
        
        log(f"找到 {len(containers)} 個容器", "OK")
        return containers
        
    except Exception as e:
        log(f"檢查容器時發生錯誤: {e}", "ERROR")
        return []


def check_server_containers_via_ssh(server_ip: str, ssh_user: str = None) -> List[Dict[str, Any]]:
    """通過 SSH 檢查伺服器端容器"""
    log(f"通過 SSH 檢查伺服器端容器: {server_ip}", "INFO")
    
    # 這裡需要 SSH 配置
    # 可以通過環境變數或配置文件獲取 SSH 認證資訊
    ssh_key = os.getenv("WUCHANG_SSH_KEY", "")
    ssh_user = ssh_user or os.getenv("WUCHANG_SSH_USER", "root")
    
    try:
        # 使用 SSH 執行 docker ps
        ssh_cmd = ["ssh"]
        if ssh_key:
            ssh_cmd.extend(["-i", ssh_key])
        ssh_cmd.extend([f"{ssh_user}@{server_ip}", "docker ps -a --format json"])
        
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10
        )
        
        if result.returncode != 0:
            log(f"SSH 連接失敗: {result.stderr}", "ERROR")
            return []
        
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    container = json.loads(line)
                    containers.append({
                        "id": container.get("ID", "")[:12],
                        "name": container.get("Names", ""),
                        "image": container.get("Image", ""),
                        "status": container.get("Status", ""),
                        "ports": container.get("Ports", ""),
                    })
                except:
                    pass
        
        log(f"伺服器端找到 {len(containers)} 個容器", "OK")
        return containers
        
    except Exception as e:
        log(f"檢查伺服器容器時發生錯誤: {e}", "ERROR")
        return []


def check_server_containers_via_api(server_url: str) -> List[Dict[str, Any]]:
    """通過 API 檢查伺服器端容器"""
    log(f"通過 API 檢查伺服器端容器: {server_url}", "INFO")
    
    try:
        # 假設伺服器有容器管理 API
        response = requests.get(
            f"{server_url}/api/containers/status",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                containers = data.get("containers", [])
                log(f"伺服器端找到 {len(containers)} 個容器", "OK")
                return containers
        else:
            log(f"API 回應錯誤: {response.status_code}", "ERROR")
            return []
            
    except requests.exceptions.ConnectionError:
        log("無法連接到伺服器 API", "ERROR")
        return []
    except Exception as e:
        log(f"檢查伺服器容器時發生錯誤: {e}", "ERROR")
        return []


def sync_container_config(local_config: Dict[str, Any], server_config: Dict[str, Any]):
    """同步容器配置"""
    log("同步容器配置...", "INFO")
    
    # 比較配置差異
    differences = []
    
    # 這裡可以比較 docker-compose.yml、環境變數等
    # 簡化版本：只顯示提示
    
    if differences:
        log(f"發現 {len(differences)} 個配置差異", "WARN")
        for diff in differences:
            log(f"  - {diff}", "INFO")
    else:
        log("配置一致", "OK")


def manage_server_container(server_ip: str, container_name: str, action: str):
    """管理伺服器端容器（啟動、停止、重啟）"""
    import os
    log(f"{action} 伺服器端容器: {container_name}", "INFO")
    
    ssh_user = os.getenv("WUCHANG_SSH_USER", "root")
    ssh_key = os.getenv("WUCHANG_SSH_KEY", "")
    
    try:
        # 通過 SSH 執行 docker 命令
        docker_cmd = f"docker {action} {container_name}"
        
        ssh_cmd = ["ssh"]
        if ssh_key:
            ssh_cmd.extend(["-i", ssh_key])
        ssh_cmd.extend([f"{ssh_user}@{server_ip}", docker_cmd])
        
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30
        )
        
        if result.returncode == 0:
            log(f"✓ 容器 {container_name} {action} 成功", "OK")
            return True
        else:
            log(f"✗ 容器 {container_name} {action} 失敗: {result.stderr}", "ERROR")
            return False
            
    except Exception as e:
        log(f"管理容器時發生錯誤: {e}", "ERROR")
        return False


def main():
    """主函數"""
    import os
    import argparse
    
    parser = argparse.ArgumentParser(description="管理伺服器端容器")
    parser.add_argument("--server-ip", help="伺服器 IP 地址")
    parser.add_argument("--server-url", help="伺服器 API URL")
    parser.add_argument("--action", choices=["status", "start", "stop", "restart"], default="status", help="操作類型")
    parser.add_argument("--container", help="容器名稱（用於 start/stop/restart）")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("伺服器端容器管理")
    print("=" * 70)
    print()
    
    # 檢查本地容器
    local_containers = check_local_containers()
    if local_containers:
        print("【本地容器】")
        for container in local_containers[:5]:  # 只顯示前 5 個
            print(f"  - {container['name']}: {container['status']}")
        print()
    
    # 檢查伺服器端容器
    server_containers = []
    
    if args.server_url:
        server_containers = check_server_containers_via_api(args.server_url)
    elif args.server_ip:
        server_containers = check_server_containers_via_ssh(args.server_ip)
    else:
        # 從環境變數或配置檔案讀取
        server_ip = os.getenv("WUCHANG_SERVER_IP", "")
        server_url = os.getenv("WUCHANG_HEALTH_URL", "").replace("/health", "")
        
        if server_url:
            server_containers = check_server_containers_via_api(server_url)
        elif server_ip:
            server_containers = check_server_containers_via_ssh(server_ip)
        else:
            log("未指定伺服器 IP 或 URL", "WARN")
            log("請使用 --server-ip 或 --server-url 參數", "INFO")
    
    if server_containers:
        print("【伺服器端容器】")
        for container in server_containers[:5]:  # 只顯示前 5 個
            print(f"  - {container['name']}: {container['status']}")
        print()
    
    # 執行操作
    if args.action != "status" and args.container:
        server_ip = args.server_ip or os.getenv("WUCHANG_SERVER_IP", "")
        if server_ip:
            manage_server_container(server_ip, args.container, args.action)
        else:
            log("需要指定伺服器 IP", "ERROR")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
