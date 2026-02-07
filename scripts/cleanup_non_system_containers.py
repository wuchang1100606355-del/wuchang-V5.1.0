#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cleanup_non_system_containers.py

清理非系統容器檔案

功能：
- 清理已停止的容器
- 清理未使用的 volumes
- 清理未使用的映像（可選）
- 保留核心系統容器（Odoo, PostgreSQL, Caddy, Cloudflare Tunnel）
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

# 核心系統容器（必須保留）
CORE_CONTAINERS = [
    "wuchang-web",
    "wuchangv510-wuchang-web-1",
    "db",
    "wuchangv510-db-1",
    "caddy",
    "wuchangv510-caddy-1",
    "cloudflared",
    "wuchangv510-cloudflared-1",
]

# 核心系統 volumes（必須保留）
CORE_VOLUMES = [
    "wuchangv510_odoo-web-data",
    "wuchangv510_odoo-db-data",
    "wuchangv510_caddy-data",
]


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
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{icon} [{timestamp}] [{level}] {message}")


def run_docker_command(cmd: list, capture_output: bool = True) -> tuple:
    """執行 Docker 命令"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)


def get_stopped_containers() -> list:
    """取得已停止的容器"""
    log("檢查已停止的容器...", "INFO")
    
    success, output, error = run_docker_command(
        ["docker", "ps", "-a", "--filter", "status=exited", "--format", "{{.Names}}|{{.Image}}"]
    )
    
    if not success:
        log(f"無法取得容器列表: {error}", "ERROR")
        return []
    
    containers = []
    for line in output.split('\n'):
        if not line.strip():
            continue
        parts = line.split('|', 1)
        if len(parts) >= 1:
            name = parts[0]
            image = parts[1] if len(parts) > 1 else ""
            # 跳過核心容器
            if not any(core in name for core in CORE_CONTAINERS):
                containers.append({"name": name, "image": image})
    
    return containers


def get_unused_volumes() -> list:
    """取得未使用的 volumes"""
    log("檢查未使用的 volumes...", "INFO")
    
    # 取得所有 volumes
    success, output, error = run_docker_command(
        ["docker", "volume", "ls", "--format", "{{.Name}}"]
    )
    
    if not success:
        log(f"無法取得 volumes 列表: {error}", "ERROR")
        return []
    
    all_volumes = [line.strip() for line in output.split('\n') if line.strip()]
    
    # 取得正在使用的 volumes
    success, output, error = run_docker_command(
        ["docker", "ps", "-a", "--format", "{{.Names}}"]
    )
    
    used_volumes = set()
    if success:
        for container_name in output.split('\n'):
            if not container_name.strip():
                continue
            # 檢查容器的 volumes
            success2, output2, _ = run_docker_command(
                ["docker", "inspect", container_name.strip(), "--format", "{{json .Mounts}}"]
            )
            if success2 and output2:
                try:
                    mounts = json.loads(output2)
                    for mount in mounts:
                        if mount.get("Type") == "volume":
                            used_volumes.add(mount.get("Name", ""))
                except:
                    pass
    
    # 找出未使用的 volumes（排除核心 volumes）
    unused_volumes = []
    for volume in all_volumes:
        if volume not in used_volumes and volume not in CORE_VOLUMES:
            # 檢查是否為舊版本 volumes
            if "wuchangv500" in volume or "jules_session" in volume or "123_" in volume or "odoo19-shadow" in volume:
                unused_volumes.append(volume)
            elif "labspace" in volume or "mochoa" in volume or "woolyai" in volume:
                unused_volumes.append(volume)
    
    return unused_volumes


def remove_containers(containers: list, dry_run: bool = False) -> dict:
    """移除容器"""
    results = {"removed": [], "failed": [], "skipped": []}
    
    if not containers:
        log("沒有需要移除的容器", "INFO")
        return results
    
    log(f"找到 {len(containers)} 個已停止的容器", "INFO")
    
    for container in containers:
        name = container["name"]
        image = container["image"]
        
        if dry_run:
            log(f"[模擬] 將移除容器: {name} ({image})", "INFO")
            results["removed"].append(name)
        else:
            log(f"移除容器: {name}...", "PROGRESS")
            success, output, error = run_docker_command(
                ["docker", "rm", name]
            )
            if success:
                log(f"✓ 已移除容器: {name}", "OK")
                results["removed"].append(name)
            else:
                log(f"✗ 移除失敗: {name} - {error}", "ERROR")
                results["failed"].append(name)
    
    return results


def remove_volumes(volumes: list, dry_run: bool = False) -> dict:
    """移除 volumes"""
    results = {"removed": [], "failed": [], "skipped": []}
    
    if not volumes:
        log("沒有需要移除的 volumes", "INFO")
        return results
    
    log(f"找到 {len(volumes)} 個未使用的 volumes", "INFO")
    
    for volume in volumes:
        if dry_run:
            log(f"[模擬] 將移除 volume: {volume}", "INFO")
            results["removed"].append(volume)
        else:
            log(f"移除 volume: {volume}...", "PROGRESS")
            success, output, error = run_docker_command(
                ["docker", "volume", "rm", volume]
            )
            if success:
                log(f"✓ 已移除 volume: {volume}", "OK")
                results["removed"].append(volume)
            else:
                log(f"✗ 移除失敗: {volume} - {error}", "ERROR")
                results["failed"].append(volume)
    
    return results


def cleanup_docker_system(dry_run: bool = False) -> dict:
    """清理 Docker 系統資源"""
    log("執行 Docker 系統清理...", "INFO")
    
    if dry_run:
        log("[模擬模式] 不會實際刪除任何資源", "WARN")
    
    # 清理未使用的資源（不包含映像，因為可能還在使用）
    cmd = ["docker", "system", "prune", "-f", "--volumes"]
    if dry_run:
        cmd.append("--dry-run")
    
    success, output, error = run_docker_command(cmd)
    
    if success:
        log("✓ Docker 系統清理完成", "OK")
        if output:
            log(f"清理結果:\n{output}", "INFO")
    else:
        log(f"✗ Docker 系統清理失敗: {error}", "ERROR")
    
    return {"success": success, "output": output, "error": error}


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="清理非系統容器檔案")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="模擬模式，不實際刪除"
    )
    parser.add_argument(
        "--containers-only",
        action="store_true",
        help="只清理容器"
    )
    parser.add_argument(
        "--volumes-only",
        action="store_true",
        help="只清理 volumes"
    )
    parser.add_argument(
        "--system-prune",
        action="store_true",
        help="執行 docker system prune"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("清理非系統容器檔案")
    print("=" * 70)
    print()
    
    if args.dry_run:
        print("⚠️  模擬模式：不會實際刪除任何資源")
        print()
    
    results = {
        "containers": {},
        "volumes": {},
        "system": {}
    }
    
    # 清理已停止的容器
    if not args.volumes_only:
        stopped_containers = get_stopped_containers()
        if stopped_containers:
            print()
            print("=" * 70)
            print("【清理已停止的容器】")
            print("=" * 70)
            print()
            results["containers"] = remove_containers(stopped_containers, args.dry_run)
        else:
            log("沒有需要清理的已停止容器", "INFO")
    
    # 清理未使用的 volumes
    if not args.containers_only:
        unused_volumes = get_unused_volumes()
        if unused_volumes:
            print()
            print("=" * 70)
            print("【清理未使用的 Volumes】")
            print("=" * 70)
            print()
            results["volumes"] = remove_volumes(unused_volumes, args.dry_run)
        else:
            log("沒有需要清理的未使用 volumes", "INFO")
    
    # 執行系統清理
    if args.system_prune:
        print()
        print("=" * 70)
        print("【Docker 系統清理】")
        print("=" * 70)
        print()
        results["system"] = cleanup_docker_system(args.dry_run)
    
    # 總結
    print()
    print("=" * 70)
    print("【清理總結】")
    print("=" * 70)
    print()
    
    if results["containers"]:
        removed = len(results["containers"].get("removed", []))
        failed = len(results["containers"].get("failed", []))
        print(f"容器: 已移除 {removed} 個，失敗 {failed} 個")
    
    if results["volumes"]:
        removed = len(results["volumes"].get("removed", []))
        failed = len(results["volumes"].get("failed", []))
        print(f"Volumes: 已移除 {removed} 個，失敗 {failed} 個")
    
    if args.dry_run:
        print()
        print("⚠️  這是模擬模式，實際執行請移除 --dry-run 參數")
    
    print()
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
