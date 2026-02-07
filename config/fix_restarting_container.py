#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_restarting_container.py

修復重啟容器的腳本

功能：
- 診斷重啟原因
- 提供修復方案
- 自動修復（如果可能）
"""

import sys
import subprocess
import json
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

CONTAINER_NAME = "wuchangv510-cloudflared-named-1"


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


def check_container_exists():
    """檢查容器是否存在"""
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"name={CONTAINER_NAME}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return CONTAINER_NAME in result.stdout
    except:
        return False


def get_container_info():
    """獲取容器資訊"""
    try:
        result = subprocess.run(
            ["docker", "inspect", CONTAINER_NAME, "--format", "json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)[0]
        else:
            return None
    except Exception as e:
        log(f"獲取容器資訊失敗: {e}", "ERROR")
        return None


def analyze_restart_reason(container_info):
    """分析重啟原因"""
    print("=" * 70)
    print("【容器診斷分析】")
    print("=" * 70)
    print()
    
    if not container_info:
        log("無法獲取容器資訊", "ERROR")
        return None
    
    # 檢查狀態
    state = container_info.get("State", {})
    status = state.get("Status", "unknown")
    restart_count = state.get("RestartCount", 0)
    exit_code = state.get("ExitCode", -1)
    
    log(f"容器狀態: {status}", "INFO")
    log(f"重啟次數: {restart_count}", "WARN" if restart_count > 10 else "INFO")
    log(f"退出代碼: {exit_code}", "INFO")
    
    # 檢查配置
    config = container_info.get("Config", {})
    cmd = config.get("Cmd", [])
    entrypoint = config.get("Entrypoint", [])
    image = config.get("Image", "unknown")
    
    print()
    log(f"映像檔: {image}", "INFO")
    log(f"入口點: {entrypoint}", "INFO")
    log(f"命令: {cmd}", "INFO")
    
    # 分析問題
    print()
    print("【問題分析】")
    print()
    
    issues = []
    
    # 檢查命令是否為空或只有幫助訊息
    if not cmd or (len(cmd) == 1 and "help" in str(cmd[0]).lower()):
        issues.append("容器啟動命令不完整或缺失")
        log("問題: 容器啟動命令不完整", "ERROR")
    
    # 檢查是否有配置檔案掛載
    mounts = container_info.get("Mounts", [])
    config_mount = any("config" in str(m.get("Destination", "")).lower() for m in mounts)
    credentials_mount = any("credentials" in str(m.get("Destination", "")).lower() for m in mounts)
    
    if not config_mount:
        issues.append("缺少配置檔案掛載")
        log("問題: 缺少配置檔案掛載", "WARN")
    
    if not credentials_mount:
        issues.append("缺少憑證檔案掛載")
        log("問題: 缺少憑證檔案掛載", "WARN")
    
    # 檢查環境變數
    env = config.get("Env", [])
    tunnel_id = any("TUNNEL" in e for e in env)
    
    if not tunnel_id and not config_mount:
        issues.append("缺少隧道 ID 或配置")
        log("問題: 缺少隧道 ID 或配置", "WARN")
    
    return {
        "status": status,
        "restart_count": restart_count,
        "exit_code": exit_code,
        "issues": issues,
        "has_config": config_mount,
        "has_credentials": credentials_mount
    }


def get_container_logs():
    """獲取容器日誌"""
    print()
    print("=" * 70)
    print("【容器日誌（最後 20 行）】")
    print("=" * 70)
    print()
    
    try:
        result = subprocess.run(
            ["docker", "logs", CONTAINER_NAME, "--tail", "20"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(result.stdout)
            return result.stdout
        else:
            log("無法獲取日誌", "WARN")
            return None
    except Exception as e:
        log(f"獲取日誌失敗: {e}", "ERROR")
        return None


def provide_solutions(analysis):
    """提供解決方案"""
    print()
    print("=" * 70)
    print("【解決方案】")
    print("=" * 70)
    print()
    
    if not analysis:
        log("無法提供解決方案", "ERROR")
        return
    
    issues = analysis.get("issues", [])
    
    if "容器啟動命令不完整" in issues:
        print("方案 1：停止並移除容器（推薦）")
        print("  如果不需要這個容器，可以直接移除：")
        print(f"    docker stop {CONTAINER_NAME}")
        print(f"    docker rm {CONTAINER_NAME}")
        print()
    
    if "缺少配置檔案掛載" in issues or "缺少憑證檔案掛載" in issues:
        print("方案 2：修復配置")
        print("  1. 檢查是否有對應的 docker-compose 配置")
        print("  2. 確認配置檔案和憑證檔案存在")
        print("  3. 重新啟動容器")
        print()
    
    print("方案 3：檢查是否有重複的 Cloudflare Tunnel 容器")
    print("  如果已有其他 cloudflared 容器運行，這個可能是重複的")
    print()


def fix_container():
    """修復容器"""
    print()
    print("=" * 70)
    print("【自動修復】")
    print("=" * 70)
    print()
    
    # 檢查是否有其他 cloudflared 容器
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=cloudflared", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        other_containers = [line for line in result.stdout.strip().split('\n') 
                           if line and line != CONTAINER_NAME]
        
        if other_containers:
            log(f"發現其他 cloudflared 容器: {', '.join(other_containers)}", "INFO")
            log("這個容器可能是重複的，建議移除", "WARN")
            print()
            
            response = input("是否停止並移除這個容器？(y/n): ").strip().lower()
            if response == 'y':
                log("正在停止容器...", "PROGRESS")
                subprocess.run(["docker", "stop", CONTAINER_NAME], timeout=10)
                
                log("正在移除容器...", "PROGRESS")
                subprocess.run(["docker", "rm", CONTAINER_NAME], timeout=10)
                
                log("容器已移除", "OK")
                return True
        else:
            log("沒有發現其他 cloudflared 容器", "INFO")
            log("這個容器可能是必要的，需要修復配置", "WARN")
    
    except Exception as e:
        log(f"修復過程發生錯誤: {e}", "ERROR")
    
    return False


def main():
    """主函數"""
    print("=" * 70)
    print("排查異常容器")
    print("=" * 70)
    print()
    print(f"容器名稱: {CONTAINER_NAME}")
    print()
    
    # 檢查容器是否存在
    if not check_container_exists():
        log("容器不存在", "ERROR")
        return 1
    
    # 獲取容器資訊
    container_info = get_container_info()
    
    # 分析問題
    analysis = analyze_restart_reason(container_info)
    
    # 獲取日誌
    get_container_logs()
    
    # 提供解決方案
    provide_solutions(analysis)
    
    # 嘗試自動修復
    if analysis and analysis.get("restart_count", 0) > 10:
        fixed = fix_container()
        if fixed:
            print()
            log("容器問題已解決", "OK")
            return 0
    
    print()
    print("=" * 70)
    print("【總結】")
    print("=" * 70)
    print()
    print("建議操作：")
    print("  1. 如果不需要這個容器，執行：")
    print(f"     docker stop {CONTAINER_NAME}")
    print(f"     docker rm {CONTAINER_NAME}")
    print()
    print("  2. 如果需要這個容器，請修復配置後重新啟動")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
