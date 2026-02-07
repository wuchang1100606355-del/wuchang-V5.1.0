#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
server_auto_deploy.py

五常系統 - 伺服器自動部署管理器

功能：
- 統一管理多個服務器的啟動、停止、重啟
- 自動檢測服務狀態
- 記錄日誌
- 支援開機自動啟動

使用方式：
  python server_auto_deploy.py start    # 啟動所有服務
  python server_auto_deploy.py stop     # 停止所有服務
  python server_auto_deploy.py restart  # 重啟所有服務
  python server_auto_deploy.py status   # 查看服務狀態
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# 服務器配置
SERVERS = {
    "control_center": {
        "name": "本機中控台",
        "script": "local_control_center.py",
        "args": ["--port", "8788"],
        "port": 8788,
        "url": "http://127.0.0.1:8788/",
        "required": True,
    },
    "little_j_hub": {
        "name": "Little J Hub",
        "script": "little_j_hub_server.py",
        "args": ["--bind", "127.0.0.1", "--port", "8799", "--root", "./little_j_hub"],
        "port": 8799,
        "url": "http://127.0.0.1:8799/",
        "required": False,
        "env": {"WUCHANG_HUB_TOKEN": os.getenv("WUCHANG_HUB_TOKEN")},
    },
}

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)


def check_port(port: int) -> bool:
    """檢查端口是否被佔用"""
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(("127.0.0.1", port))
            return result == 0
    except Exception:
        return False


def get_process_by_port(port: int) -> Optional[int]:
    """根據端口獲取進程 ID"""
    try:
        if sys.platform == "win32":
            # Windows: 使用 netstat 和 findstr
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            for line in result.stdout.splitlines():
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        return int(parts[-1])
        else:
            # Linux/Mac: 使用 lsof
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                return int(result.stdout.strip().split()[0])
    except Exception:
        pass
    return None


def start_server(server_id: str, config: Dict) -> bool:
    """啟動單個服務器"""
    script_path = BASE_DIR / config["script"]
    if not script_path.exists():
        if config.get("required", False):
            print(f"[錯誤] 找不到必要檔案: {config['script']}")
            return False
        else:
            print(f"[跳過] 找不到檔案: {config['script']}")
            return True

    # 檢查端口是否已被佔用
    if check_port(config["port"]):
        pid = get_process_by_port(config["port"])
        print(f"[警告] 端口 {config['port']} 已被佔用 (PID: {pid})")
        print(f"[提示] 服務 {config['name']} 可能已在運行")
        return True

    # 準備環境變數
    env = os.environ.copy()
    if "env" in config:
        env.update({k: v for k, v in config["env"].items() if v})

    # 檢查必要的環境變數
    if "env" in config:
        missing_env = [k for k, v in config["env"].items() if not v]
        if missing_env:
            print(f"[跳過] {config['name']}: 缺少環境變數 {', '.join(missing_env)}")
            return True

    # 準備日誌檔案
    log_file = LOG_DIR / f"{server_id}.log"

    # 啟動服務器
    try:
        if sys.platform == "win32":
            # Windows: 使用 start 命令在背景執行
            cmd = [
                "start",
                f"/min",
                f"五常-{config['name']}",
                sys.executable,
                str(script_path),
            ] + config["args"]
            subprocess.Popen(
                cmd,
                shell=True,
                cwd=BASE_DIR,
                env=env,
                stdout=open(log_file, "a", encoding="utf-8"),
                stderr=subprocess.STDOUT,
            )
        else:
            # Linux/Mac: 使用 nohup 或直接執行
            cmd = [sys.executable, str(script_path)] + config["args"]
            with open(log_file, "a", encoding="utf-8") as f:
                subprocess.Popen(
                    cmd,
                    cwd=BASE_DIR,
                    env=env,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                )

        # 等待服務啟動
        time.sleep(2)

        # 檢查是否成功啟動
        if check_port(config["port"]):
            print(f"[成功] {config['name']} 已啟動: {config['url']}")
            return True
        else:
            print(f"[警告] {config['name']} 可能未正常啟動，請檢查日誌: {log_file}")
            return False

    except Exception as e:
        print(f"[錯誤] 啟動 {config['name']} 時發生錯誤: {e}")
        return False


def stop_server(server_id: str, config: Dict) -> bool:
    """停止單個服務器"""
    port = config["port"]
    pid = get_process_by_port(port)

    if not pid:
        print(f"[提示] {config['name']} 未運行 (端口 {port})")
        return True

    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=False)
        else:
            subprocess.run(["kill", str(pid)], check=False)

        # 等待進程結束
        time.sleep(1)

        if not check_port(port):
            print(f"[成功] {config['name']} 已停止")
            return True
        else:
            print(f"[警告] {config['name']} 可能未完全停止")
            return False

    except Exception as e:
        print(f"[錯誤] 停止 {config['name']} 時發生錯誤: {e}")
        return False


def start_all() -> None:
    """啟動所有服務器"""
    print("=" * 50)
    print("啟動五常系統服務器")
    print("=" * 50)
    print()

    success_count = 0
    for server_id, config in SERVERS.items():
        if start_server(server_id, config):
            success_count += 1
        time.sleep(1)

    print()
    print("=" * 50)
    print(f"啟動完成: {success_count}/{len(SERVERS)} 個服務")
    print("=" * 50)


def stop_all() -> None:
    """停止所有服務器"""
    print("=" * 50)
    print("停止五常系統服務器")
    print("=" * 50)
    print()

    for server_id, config in SERVERS.items():
        stop_server(server_id, config)
        time.sleep(1)

    print()
    print("=" * 50)
    print("停止完成")
    print("=" * 50)


def restart_all() -> None:
    """重啟所有服務器"""
    print("=" * 50)
    print("重啟五常系統服務器")
    print("=" * 50)
    print()

    stop_all()
    time.sleep(2)
    print()
    start_all()


def show_status() -> None:
    """顯示服務狀態"""
    print("=" * 50)
    print("五常系統服務器狀態")
    print("=" * 50)
    print()

    for server_id, config in SERVERS.items():
        port = config["port"]
        is_running = check_port(port)
        status = "運行中" if is_running else "未運行"
        pid = get_process_by_port(port) if is_running else None

        print(f"{config['name']}:")
        print(f"  狀態: {status}")
        print(f"  端口: {port}")
        if pid:
            print(f"  進程 ID: {pid}")
        print(f"  網址: {config['url']}")
        print()

    print("=" * 50)


def main() -> None:
    ap = argparse.ArgumentParser(description="五常系統服務器自動部署管理器")
    ap.add_argument(
        "action",
        choices=["start", "stop", "restart", "status"],
        help="執行動作",
    )
    args = ap.parse_args()

    if args.action == "start":
        start_all()
    elif args.action == "stop":
        stop_all()
    elif args.action == "restart":
        restart_all()
    elif args.action == "status":
        show_status()


if __name__ == "__main__":
    main()
