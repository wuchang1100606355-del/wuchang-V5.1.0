#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整容器卸載與重新部署腳本
按照部署計畫執行完整清理和部署流程
"""

import sys
import os
import subprocess
import time
from pathlib import Path
from datetime import datetime

WORKSPACE_PATH = Path(__file__).parent.parent

def log(message: str, level: str = "INFO"):
    """記錄訊息"""
    icons = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️",
        "PROGRESS": "🔄"
    }
    icon = icons.get(level, "•")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [{level}] {message}")

def check_docker_running():
    """檢查 Docker 是否運行"""
    try:
        result = subprocess.run(
            ['docker', 'ps'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False

def stop_all_containers():
    """停止所有容器"""
    log("停止所有容器...", "PROGRESS")
    
    try:
        # 使用 docker-compose down
        result = subprocess.run(
            ['docker-compose', 'down'],
            cwd=WORKSPACE_PATH,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            log("所有容器已停止", "SUCCESS")
            return True
        else:
            log(f"停止容器時發生錯誤: {result.stderr}", "WARNING")
            # 嘗試強制停止
            return force_stop_containers()
    except Exception as e:
        log(f"停止容器失敗: {e}", "ERROR")
        return False

def force_stop_containers():
    """強制停止所有容器"""
    log("強制停止所有容器...", "PROGRESS")
    
    try:
        # 獲取所有容器
        result = subprocess.run(
            ['docker', 'ps', '-a', '-q', '--filter', 'name=wuchang'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.stdout.strip():
            container_ids = result.stdout.strip().split('\n')
            for container_id in container_ids:
                subprocess.run(
                    ['docker', 'stop', container_id],
                    capture_output=True,
                    timeout=30
                )
                subprocess.run(
                    ['docker', 'rm', container_id],
                    capture_output=True,
                    timeout=30
                )
            log(f"已強制停止 {len(container_ids)} 個容器", "SUCCESS")
            return True
        else:
            log("沒有找到需要停止的容器", "INFO")
            return True
    except Exception as e:
        log(f"強制停止失敗: {e}", "ERROR")
        return False

def remove_volumes():
    """移除所有相關 Volumes"""
    log("移除相關 Volumes...", "PROGRESS")
    
    try:
        # 獲取所有 volumes
        result = subprocess.run(
            ['docker', 'volume', 'ls', '-q', '--filter', 'name=wuchang'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.stdout.strip():
            volume_names = result.stdout.strip().split('\n')
            for volume_name in volume_names:
                subprocess.run(
                    ['docker', 'volume', 'rm', volume_name],
                    capture_output=True,
                    timeout=30
                )
            log(f"已移除 {len(volume_names)} 個 Volumes", "SUCCESS")
        else:
            log("沒有找到相關 Volumes", "INFO")
        
        return True
    except Exception as e:
        log(f"移除 Volumes 失敗: {e}", "WARNING")
        return False

def remove_networks():
    """移除相關 Networks"""
    log("移除相關 Networks...", "PROGRESS")
    
    try:
        # 獲取所有 networks
        result = subprocess.run(
            ['docker', 'network', 'ls', '-q', '--filter', 'name=wuchang'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.stdout.strip():
            network_names = result.stdout.strip().split('\n')
            for network_name in network_names:
                subprocess.run(
                    ['docker', 'network', 'rm', network_name],
                    capture_output=True,
                    timeout=30
                )
            log(f"已移除 {len(network_names)} 個 Networks", "SUCCESS")
        else:
            log("沒有找到相關 Networks", "INFO")
        
        return True
    except Exception as e:
        log(f"移除 Networks 失敗: {e}", "WARNING")
        return False

def cleanup_unused_resources():
    """清理未使用的資源"""
    log("清理未使用的 Docker 資源...", "PROGRESS")
    
    try:
        result = subprocess.run(
            ['docker', 'system', 'prune', '-f', '--volumes'],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            log("未使用的資源已清理", "SUCCESS")
            return True
        else:
            log("清理資源時發生錯誤", "WARNING")
            return False
    except Exception as e:
        log(f"清理資源失敗: {e}", "WARNING")
        return False

def verify_cleanup():
    """驗證清理結果"""
    log("驗證清理結果...", "PROGRESS")
    
    try:
        # 檢查容器
        result = subprocess.run(
            ['docker', 'ps', '-a', '--filter', 'name=wuchang'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        containers = [line for line in result.stdout.strip().split('\n') if line.strip() and not line.startswith('CONTAINER')]
        
        if containers:
            log(f"⚠️ 仍有 {len(containers)} 個容器存在", "WARNING")
            return False
        else:
            log("✅ 所有容器已清理", "SUCCESS")
            return True
    except Exception as e:
        log(f"驗證清理結果失敗: {e}", "WARNING")
        return False

def deploy_containers():
    """部署容器"""
    log("開始部署容器...", "PROGRESS")
    
    try:
        # 構建並啟動容器
        result = subprocess.run(
            ['docker-compose', 'up', '-d', '--build'],
            cwd=WORKSPACE_PATH,
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if result.returncode == 0:
            log("容器部署成功", "SUCCESS")
            return True
        else:
            log(f"容器部署失敗: {result.stderr}", "ERROR")
            return False
    except Exception as e:
        log(f"部署容器失敗: {e}", "ERROR")
        return False

def check_deployment_status():
    """檢查部署狀態"""
    log("檢查部署狀態...", "PROGRESS")
    
    try:
        result = subprocess.run(
            ['docker-compose', 'ps'],
            cwd=WORKSPACE_PATH,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            log("容器狀態:", "INFO")
            print(result.stdout)
            return True
        else:
            log("無法檢查容器狀態", "WARNING")
            return False
    except Exception as e:
        log(f"檢查部署狀態失敗: {e}", "ERROR")
        return False

def install_wuchang_modules():
    """安裝 Wuchang 模組"""
    log("安裝 Wuchang 模組...", "PROGRESS")
    
    install_script = WORKSPACE_PATH / 'scripts' / 'install_wuchang_modules_v2.py'
    if install_script.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(install_script)],
                cwd=WORKSPACE_PATH,
                timeout=600
            )
            
            if result.returncode == 0:
                log("Wuchang 模組安裝完成", "SUCCESS")
                return True
            else:
                log("Wuchang 模組安裝可能有問題", "WARNING")
                return False
        except Exception as e:
            log(f"安裝模組失敗: {e}", "ERROR")
            return False
    else:
        log("找不到模組安裝腳本", "WARNING")
        return False

def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("  🧹 完整容器卸載與重新部署")
    print("=" * 60)
    print(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 檢查 Docker
    if not check_docker_running():
        log("Docker 未運行，請先啟動 Docker Desktop", "ERROR")
        return 1
    
    results = {}
    
    # 階段 1: 完整卸載
    print("\n" + "-" * 60)
    print("階段 1: 完整卸載")
    print("-" * 60)
    
    results['stop_containers'] = stop_all_containers()
    time.sleep(2)
    
    results['remove_volumes'] = remove_volumes()
    time.sleep(2)
    
    results['remove_networks'] = remove_networks()
    time.sleep(2)
    
    results['cleanup_resources'] = cleanup_unused_resources()
    time.sleep(2)
    
    results['verify_cleanup'] = verify_cleanup()
    
    # 階段 2: 重新部署
    print("\n" + "-" * 60)
    print("階段 2: 重新部署")
    print("-" * 60)
    
    results['deploy_containers'] = deploy_containers()
    time.sleep(10)  # 等待容器啟動
    
    results['check_status'] = check_deployment_status()
    
    # 階段 3: 安裝模組
    print("\n" + "-" * 60)
    print("階段 3: 安裝模組")
    print("-" * 60)
    
    if results.get('deploy_containers'):
        results['install_modules'] = install_wuchang_modules()
    else:
        log("跳過模組安裝（容器部署失敗）", "WARNING")
        results['install_modules'] = False
    
    # 總結
    print("\n" + "=" * 60)
    print("  📊 執行總結")
    print("=" * 60)
    
    total_steps = len(results)
    success_steps = sum(1 for v in results.values() if v)
    
    print(f"\n總步驟數: {total_steps}")
    print(f"成功: {success_steps} ✅")
    print(f"失敗: {total_steps - success_steps} ❌")
    print()
    
    for step, status in results.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {step}")
    
    print("\n" + "=" * 60)
    if success_steps == total_steps:
        print("  ✅ 完整卸載與部署完成")
    else:
        print("  ⚠️ 部分步驟需要檢查")
    print("=" * 60)
    
    return 0 if success_steps == total_steps else 1

if __name__ == '__main__':
    sys.exit(main())
