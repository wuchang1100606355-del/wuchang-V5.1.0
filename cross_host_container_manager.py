#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cross_host_container_manager.py

跨主機容器管理（開發環境）

功能：
- 本地和伺服器可以互相管理對方的容器
- 通過 SSH 或 API 遠程執行 Docker 命令
- 同步容器配置
- 監控容器狀態
"""

import sys
import json
import subprocess
import requests
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
NETWORK_CONFIG = BASE_DIR / "network_interconnection_config.json"


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    print(f"[{level}] {message}")


def load_network_config() -> Dict[str, Any]:
    """載入網路配置"""
    if NETWORK_CONFIG.exists():
        try:
            return json.loads(NETWORK_CONFIG.read_text(encoding="utf-8"))
        except:
            pass
    return {}


def execute_local_docker(command: List[str]) -> Dict[str, Any]:
    """在本地執行 Docker 命令"""
    try:
        result = subprocess.run(
            ["docker"] + command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30
        )
        
        return {
            "ok": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "stdout": "",
            "stderr": str(e),
            "returncode": -1,
        }


def execute_remote_docker_via_ssh(server_ip: str, command: List[str], ssh_user: str = None) -> Dict[str, Any]:
    """通過 SSH 在伺服器執行 Docker 命令"""
    ssh_user = ssh_user or os.getenv("WUCHANG_SSH_USER", "root")
    ssh_key = os.getenv("WUCHANG_SSH_KEY", "")
    
    try:
        # 構建 SSH 命令
        ssh_cmd = ["ssh"]
        if ssh_key:
            ssh_cmd.extend(["-i", ssh_key])
        
        # 構建遠程命令
        remote_cmd = " ".join(["docker"] + [f'"{arg}"' if " " in arg else arg for arg in command])
        ssh_cmd.extend([f"{ssh_user}@{server_ip}", remote_cmd])
        
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30
        )
        
        return {
            "ok": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "stdout": "",
            "stderr": str(e),
            "returncode": -1,
        }


def execute_remote_docker_via_api(server_url: str, command: List[str]) -> Dict[str, Any]:
    """通過 API 在伺服器執行 Docker 命令"""
    try:
        response = requests.post(
            f"{server_url}/api/docker/execute",
            json={"command": command},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "ok": False,
                "error": f"API 回應錯誤: {response.status_code}",
                "stdout": "",
                "stderr": response.text,
                "returncode": response.status_code,
            }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "stdout": "",
            "stderr": str(e),
            "returncode": -1,
        }


def list_containers(host: str = "local") -> List[Dict[str, Any]]:
    """列出容器"""
    if host == "local":
        result = execute_local_docker(["ps", "-a", "--format", "json"])
    else:
        config = load_network_config()
        server_ip = config.get("server_ip", host)
        server_url = config.get("health_url", "").replace("/health", "")
        
        # 優先使用 SSH（更可靠）
        if server_ip:
            result = execute_remote_docker_via_ssh(server_ip, ["ps", "-a", "--format", "json"])
        elif server_url:
            result = execute_remote_docker_via_api(server_url, ["ps", "-a", "--format", "json"])
        else:
            return []
    
    if not result.get("ok"):
        log(f"獲取容器列表失敗: {result.get('error', '未知錯誤')}", "ERROR")
        return []
    
    containers = []
    for line in result["stdout"].strip().split('\n'):
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
    
    return containers


def manage_container(host: str, container_name: str, action: str) -> bool:
    """管理容器（啟動、停止、重啟、刪除）"""
    log(f"{action} {host} 的容器: {container_name}", "INFO")
    
    if host == "local":
        result = execute_local_docker([action, container_name])
    else:
        config = load_network_config()
        server_ip = config.get("server_ip", host)
        server_url = config.get("health_url", "").replace("/health", "")
        
        if server_url:
            result = execute_remote_docker_via_api(server_url, [action, container_name])
        else:
            result = execute_remote_docker_via_ssh(server_ip, [action, container_name])
    
    if result.get("ok"):
        log(f"✓ 容器 {container_name} {action} 成功", "OK")
        if result.get("stdout"):
            print(result["stdout"])
        return True
    else:
        log(f"✗ 容器 {container_name} {action} 失敗: {result.get('error', result.get('stderr', '未知錯誤'))}", "ERROR")
        return False


def sync_container_config(local_config_path: Path, remote_host: str):
    """同步容器配置（docker-compose.yml）"""
    log(f"同步容器配置到 {remote_host}...", "INFO")
    
    if not local_config_path.exists():
        log(f"本地配置檔案不存在: {local_config_path}", "ERROR")
        return False
    
    config = load_network_config()
    server_ip = config.get("server_ip", remote_host)
    ssh_user = os.getenv("WUCHANG_SSH_USER", "root")
    ssh_key = os.getenv("WUCHANG_SSH_KEY", "")
    
    try:
        # 使用 SCP 複製配置檔案
        scp_cmd = ["scp"]
        if ssh_key:
            scp_cmd.extend(["-i", ssh_key])
        
        remote_path = f"{ssh_user}@{server_ip}:{local_config_path.name}"
        scp_cmd.extend([str(local_config_path), remote_path])
        
        result = subprocess.run(
            scp_cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30
        )
        
        if result.returncode == 0:
            log(f"✓ 配置檔案已同步到 {remote_host}", "OK")
            return True
        else:
            log(f"✗ 同步失敗: {result.stderr}", "ERROR")
            return False
            
    except Exception as e:
        log(f"✗ 同步時發生錯誤: {e}", "ERROR")
        return False


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="跨主機容器管理（開發環境）")
    parser.add_argument("--host", choices=["local", "server"], default="local", help="目標主機")
    parser.add_argument("--action", choices=["list", "start", "stop", "restart", "logs", "exec"], default="list", help="操作類型")
    parser.add_argument("--container", help="容器名稱")
    parser.add_argument("--sync-config", help="同步配置檔案路徑")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("跨主機容器管理（開發環境）")
    print("=" * 70)
    print()
    
    config = load_network_config()
    print(f"本地 IP: {config.get('local_ip', '未知')}")
    print(f"伺服器 IP: {config.get('server_ip', '未知')}")
    print()
    
    if args.action == "list":
        # 列出容器
        print(f"【{args.host.upper()} 容器列表】")
        print()
        containers = list_containers(args.host)
        
        if containers:
            for container in containers:
                print(f"  {container['name']:30} {container['status']:20} {container['image']}")
        else:
            print("  未找到容器")
        print()
        
        # 同時顯示本地和伺服器
        if args.host == "local":
            print("【伺服器容器列表】")
            print()
            server_containers = list_containers("server")
            if server_containers:
                for container in server_containers:
                    print(f"  {container['name']:30} {container['status']:20} {container['image']}")
            else:
                print("  無法連接到伺服器或未找到容器")
            print()
    
    elif args.action in ["start", "stop", "restart"]:
        if not args.container:
            log("需要指定容器名稱: --container <name>", "ERROR")
            return 1
        
        manage_container(args.host, args.container, args.action)
    
    elif args.action == "logs":
        if not args.container:
            log("需要指定容器名稱: --container <name>", "ERROR")
            return 1
        
        if args.host == "local":
            result = execute_local_docker(["logs", "--tail", "50", args.container])
        else:
            config = load_network_config()
            server_ip = config.get("server_ip", "server")
            result = execute_remote_docker_via_ssh(server_ip, ["logs", "--tail", "50", args.container])
        
        if result.get("ok"):
            print(result["stdout"])
        else:
            log(f"獲取日誌失敗: {result.get('error', '未知錯誤')}", "ERROR")
    
    elif args.action == "exec":
        if not args.container:
            log("需要指定容器名稱: --container <name>", "ERROR")
            return 1
        
        # 執行命令（簡化版本）
        command = input("請輸入要在容器內執行的命令: ").strip()
        if not command:
            return 1
        
        if args.host == "local":
            result = execute_local_docker(["exec", args.container, "sh", "-c", command])
        else:
            config = load_network_config()
            server_ip = config.get("server_ip", "server")
            result = execute_remote_docker_via_ssh(server_ip, ["exec", args.container, "sh", "-c", command])
        
        if result.get("ok"):
            print(result["stdout"])
        else:
            log(f"執行失敗: {result.get('error', '未知錯誤')}", "ERROR")
    
    if args.sync_config:
        sync_container_config(Path(args.sync_config), args.host if args.host != "local" else "server")
    
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
