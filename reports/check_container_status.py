#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_container_status.py

檢查容器狀態並生成報告
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
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
        "ERROR": "❌",
        "PROGRESS": "🔄"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")


def get_container_status():
    """取得容器狀態"""
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{.Names}}|{{.Status}}|{{.Ports}}|{{.Image}}"],
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            log("無法執行 docker ps 命令", "ERROR")
            return []
        
        containers = []
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            parts = line.split('|', 3)
            if len(parts) >= 2:
                containers.append({
                    "name": parts[0],
                    "status": parts[1],
                    "ports": parts[2] if len(parts) > 2 else "",
                    "image": parts[3] if len(parts) > 3 else ""
                })
        
        return containers
    except Exception as e:
        log(f"取得容器狀態時發生錯誤: {e}", "ERROR")
        return []


def get_container_logs(container_name: str, tail: int = 20) -> str:
    """取得容器日誌"""
    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", str(tail), container_name],
            capture_output=True,
            text=True,
            timeout=5,
            encoding='utf-8',
            errors='replace'
        )
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return f"無法取得日誌: {e}"


def analyze_status(status: str) -> Dict[str, any]:
    """分析容器狀態"""
    is_running = "Up" in status
    is_restarting = "Restarting" in status
    is_exited = "Exited" in status
    is_created = "Created" in status
    is_paused = "Paused" in status
    
    # 提取運行時間
    uptime = None
    if is_running:
        # 嘗試從狀態中提取時間
        import re
        match = re.search(r'Up\s+([0-9a-z\s]+)', status)
        if match:
            uptime = match.group(1)
    
    return {
        "is_running": is_running,
        "is_restarting": is_restarting,
        "is_exited": is_exited,
        "is_created": is_created,
        "is_paused": is_paused,
        "uptime": uptime,
        "raw_status": status
    }


def main():
    """主函數"""
    print("=" * 70)
    print("容器狀態檢查")
    print("=" * 70)
    print()
    
    log("正在取得容器狀態...", "PROGRESS")
    containers = get_container_status()
    
    if not containers:
        log("未找到容器或無法取得狀態", "ERROR")
        return 1
    
    log(f"找到 {len(containers)} 個容器", "OK")
    print()
    
    # 分類容器
    running = []
    restarting = []
    exited = []
    other = []
    
    for container in containers:
        analysis = analyze_status(container["status"])
        container_info = {**container, **analysis}
        
        if analysis["is_running"]:
            running.append(container_info)
        elif analysis["is_restarting"]:
            restarting.append(container_info)
        elif analysis["is_exited"]:
            exited.append(container_info)
        else:
            other.append(container_info)
    
    # 顯示運行中的容器
    print("=" * 70)
    print("【運行中的容器】")
    print("=" * 70)
    print()
    
    if running:
        for container in sorted(running, key=lambda x: x["name"]):
            status_icon = "✅" if container["is_running"] else "❌"
            print(f"{status_icon} {container['name']}")
            print(f"   狀態: {container['status']}")
            if container['ports']:
                print(f"   端口: {container['ports']}")
            print(f"   映像: {container['image']}")
            print()
    else:
        log("沒有運行中的容器", "WARN")
        print()
    
    # 顯示重啟中的容器
    if restarting:
        print("=" * 70)
        print("【重啟中的容器】⚠️")
        print("=" * 70)
        print()
        
        for container in restarting:
            print(f"⚠️ {container['name']}")
            print(f"   狀態: {container['status']}")
            print(f"   映像: {container['image']}")
            print()
            
            # 顯示最近日誌
            log(f"查看 {container['name']} 的日誌...", "PROGRESS")
            logs = get_container_logs(container['name'], tail=10)
            if logs:
                print("   最近日誌:")
                for log_line in logs.split('\n')[-5:]:
                    if log_line.strip():
                        print(f"   {log_line}")
            print()
    
    # 顯示已停止的容器
    if exited:
        print("=" * 70)
        print("【已停止的容器】")
        print("=" * 70)
        print()
        
        for container in sorted(exited, key=lambda x: x["name"]):
            print(f"⏹️ {container['name']}")
            print(f"   狀態: {container['status']}")
            print(f"   映像: {container['image']}")
            print()
    
    # 其他狀態
    if other:
        print("=" * 70)
        print("【其他狀態的容器】")
        print("=" * 70)
        print()
        
        for container in sorted(other, key=lambda x: x["name"]):
            print(f"❓ {container['name']}")
            print(f"   狀態: {container['status']}")
            print(f"   映像: {container['image']}")
            print()
    
    # 統計
    print("=" * 70)
    print("【統計摘要】")
    print("=" * 70)
    print()
    
    print(f"總容器數: {len(containers)}")
    print(f"✅ 運行中: {len(running)}")
    print(f"⚠️ 重啟中: {len(restarting)}")
    print(f"⏹️ 已停止: {len(exited)}")
    print(f"❓ 其他: {len(other)}")
    print()
    
    # 健康度
    if len(containers) > 0:
        health_percentage = (len(running) / len(containers)) * 100
        if health_percentage == 100:
            log(f"系統健康度: {health_percentage:.0f}% 🟢 優秀", "OK")
        elif health_percentage >= 80:
            log(f"系統健康度: {health_percentage:.0f}% 🟡 良好", "OK")
        elif health_percentage >= 60:
            log(f"系統健康度: {health_percentage:.0f}% 🟠 需要注意", "WARN")
        else:
            log(f"系統健康度: {health_percentage:.0f}% 🔴 異常", "ERROR")
    
    print()
    
    # 建議
    if restarting:
        print("=" * 70)
        print("【建議操作】")
        print("=" * 70)
        print()
        print("發現重啟中的容器，建議執行：")
        for container in restarting:
            print(f"  1. 查看詳細日誌: docker logs {container['name']}")
            print(f"  2. 檢查容器配置: docker inspect {container['name']}")
            print(f"  3. 如果不需要，可移除: docker rm -f {container['name']}")
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
