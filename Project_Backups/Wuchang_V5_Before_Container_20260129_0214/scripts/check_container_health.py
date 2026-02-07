#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
容器健康檢查腳本
檢查所有 UI 相關容器的健康狀態
"""

import subprocess
import json
import sys
import io
import socket
from datetime import datetime
from typing import Dict, List, Any

# 設定輸出編碼（Windows）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def run_command(cmd: List[str]) -> tuple:
    """執行命令並返回結果"""
    try:
        # Windows 上使用 UTF-8 編碼
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=10,
            encoding='utf-8',
            errors='replace'  # 遇到無法解碼的字元時替換而不是失敗
        )
        return (result.returncode == 0, result.stdout or "", result.stderr or "")
    except Exception as e:
        return (False, "", str(e))

def check_docker_running() -> bool:
    """檢查 Docker 是否運行"""
    success, _, _ = run_command(["docker", "--version"])
    return success

def get_container_status() -> List[Dict[str, Any]]:
    """取得容器狀態"""
    success, output, _ = run_command([
        "docker", "ps", "-a", "--format", "json"
    ])
    
    if not success:
        return []
    
    containers = []
    if not output:
        return containers
    
    for line in output.strip().split('\n'):
        if line:
            try:
                container = json.loads(line)
                containers.append({
                    "name": container.get("Names", ""),
                    "status": container.get("Status", ""),
                    "ports": container.get("Ports", ""),
                    "id": container.get("ID", "")
                })
            except (json.JSONDecodeError, AttributeError):
                pass
    
    return containers

def get_container_logs(container_name: str, lines: int = 50) -> str:
    """取得容器日誌"""
    success, output, error = run_command([
        "docker", "logs", "--tail", str(lines), container_name
    ])
    
    if success:
        return output
    else:
        return error

def check_port(port: int) -> Dict[str, Any]:
    """檢查端口狀態"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return {
            "port": port,
            "open": result == 0,
            "status": "open" if result == 0 else "closed"
        }
    except Exception as e:
        return {
            "port": port,
            "open": False,
            "status": f"error: {str(e)}"
        }

def check_http_endpoint(url: str) -> Dict[str, Any]:
    """檢查 HTTP 端點"""
    try:
        try:
            import requests
        except ImportError:
            return {
                "url": url,
                "accessible": False,
                "error": "requests module not installed"
            }
        response = requests.get(url, timeout=3)
        return {
            "url": url,
            "status_code": response.status_code,
            "accessible": True,
            "response_time": response.elapsed.total_seconds()
        }
    except Exception as e:
        return {
            "url": url,
            "accessible": False,
            "error": str(e)
        }

def main():
    """主函數"""
    print("=" * 60)
    print("UI 容器健康檢查")
    print("=" * 60)
    print()
    
    # 檢查 Docker
    print("[1/6] 檢查 Docker...")
    if not check_docker_running():
        print("[X] Docker 未運行")
        sys.exit(1)
    print("[OK] Docker 運行中")
    
    # 取得容器狀態
    print("\n[2/6] 取得容器狀態...")
    containers = get_container_status()
    ui_containers = [c for c in containers if any(name in c["name"] for name in 
                   ["wuchang", "odoo", "uptime", "portainer", "ai", "status"])]
    
    print(f"找到 {len(ui_containers)} 個 UI 相關容器:")
    for container in ui_containers:
        status_icon = "[OK]" if "Up" in container["status"] else "[X]"
        print(f"  {status_icon} {container['name']}: {container['status']}")
    
    # 檢查容器日誌
    print("\n[3/6] 檢查容器日誌（錯誤）...")
    for container in ui_containers:
        if "Up" not in container["status"]:
            print(f"\n--- {container['name']} 日誌（最近錯誤）---")
            logs = get_container_logs(container["name"], 30)
            error_lines = [line for line in logs.split('\n') if any(keyword in line.lower() 
                          for keyword in ['error', 'exception', 'failed', 'fatal'])]
            if error_lines:
                for line in error_lines[-10:]:
                    print(f"  {line}")
            else:
                print("  無明顯錯誤")
    
    # 檢查端口
    print("\n[4/6] 檢查端口狀態...")
    ports = [8069, 8080, 3001, 8888, 9000]
    for port in ports:
        port_status = check_port(port)
        status_icon = "[OK]" if port_status["open"] else "[X]"
        print(f"  {status_icon} 端口 {port}: {port_status['status']}")
    
    # 檢查 HTTP 端點
    print("\n[5/6] 檢查 HTTP 端點...")
    endpoints = [
        "http://localhost:8069/web/health",
        "http://localhost:8080/health",
        "http://localhost:3001/health",
        "http://localhost:8888/api/supervisor/status"
    ]
    
    for endpoint in endpoints:
        result = check_http_endpoint(endpoint)
        status_icon = "[OK]" if result.get("accessible") else "[X]"
        if result.get("accessible"):
            print(f"  {status_icon} {endpoint}: HTTP {result.get('status_code')} "
                  f"({result.get('response_time', 0):.2f}s)")
        else:
            print(f"  {status_icon} {endpoint}: 無法訪問")
    
    # 生成報告
    print("\n[6/6] 生成診斷報告...")
    report = {
        "timestamp": datetime.now().isoformat(),
        "containers": ui_containers,
        "ports": [check_port(p) for p in ports],
        "endpoints": [check_http_endpoint(e) for e in endpoints]
    }
    
    report_file = "container_health_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] 報告已儲存: {report_file}")
    
    print("\n" + "=" * 60)
    print("檢查完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
