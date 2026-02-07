#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地端小J執行安裝修正腳本
根據雲端小J的修正報告自動執行修正步驟
"""

import sys
import os
import subprocess
import time
from pathlib import Path
from datetime import datetime

WORKSPACE_PATH = Path(__file__).parent.parent
REPORTS_PATH = WORKSPACE_PATH / 'reports'

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
            ['docker', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # 嘗試執行 docker ps
            result = subprocess.run(
                ['docker', 'ps'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def wait_for_docker(max_wait=120):
    """等待 Docker 啟動"""
    log("等待 Docker Desktop 啟動...", "PROGRESS")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        if check_docker_running():
            log("Docker 已啟動", "SUCCESS")
            return True
        time.sleep(2)
        print(".", end="", flush=True)
    
    log("Docker 啟動超時", "ERROR")
    return False

def start_docker_containers():
    """啟動 Docker 容器"""
    log("啟動 Docker 容器...", "PROGRESS")
    
    try:
        result = subprocess.run(
            ['docker-compose', 'up', '-d'],
            cwd=WORKSPACE_PATH,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            log("容器啟動成功", "SUCCESS")
            return True
        else:
            log(f"容器啟動失敗: {result.stderr}", "ERROR")
            return False
    except FileNotFoundError:
        log("找不到 docker-compose 命令", "ERROR")
        return False
    except subprocess.TimeoutExpired:
        log("容器啟動超時", "ERROR")
        return False

def check_container_status():
    """檢查容器狀態"""
    log("檢查容器狀態...", "PROGRESS")
    
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
        log(f"檢查容器狀態時發生錯誤: {e}", "ERROR")
        return False

def check_database_status():
    """檢查資料庫狀態"""
    log("檢查資料庫狀態...", "PROGRESS")
    
    # 先找到資料庫容器
    try:
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Names}}', '--filter', 'name=db'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            db_container = result.stdout.strip().split('\n')[0]
            log(f"找到資料庫容器: {db_container}", "INFO")
            
            # 檢查模組數量
            query = "SELECT COUNT(*) FROM ir_module_module;"
            cmd = [
                'docker', 'exec', db_container,
                'psql', '-U', 'odoo', '-d', 'admin', '-t', '-c', query
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                module_count = result.stdout.strip()
                log(f"資料庫中的模組數量: {module_count}", "INFO")
                
                if module_count == '0' or int(module_count) < 10:
                    log("⚠️ 資料庫可能是新資料庫或模組未安裝", "WARNING")
                    return False
                else:
                    log("資料庫狀態正常", "SUCCESS")
                    return True
            else:
                log("無法查詢資料庫", "WARNING")
                return False
        else:
            log("未找到資料庫容器", "WARNING")
            return False
    except Exception as e:
        log(f"檢查資料庫時發生錯誤: {e}", "ERROR")
        return False

def fix_odoo_ide_module():
    """修復 Odoo IDE 模組"""
    log("修復 Odoo IDE 模組...", "PROGRESS")
    
    fix_script = WORKSPACE_PATH / 'scripts' / 'fix_odoo_ide_extension.py'
    if fix_script.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(fix_script)],
                cwd=WORKSPACE_PATH,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                log("IDE 模組修復完成", "SUCCESS")
                return True
            else:
                log(f"IDE 模組修復失敗: {result.stderr}", "WARNING")
                return False
        except Exception as e:
            log(f"執行修復腳本時發生錯誤: {e}", "ERROR")
            return False
    else:
        log("找不到修復腳本", "WARNING")
        return False

def verify_modules():
    """驗證模組安裝"""
    log("驗證模組安裝...", "PROGRESS")
    
    check_script = WORKSPACE_PATH / 'scripts' / 'check_module_installation.py'
    if check_script.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(check_script)],
                cwd=WORKSPACE_PATH,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                log("模組驗證完成", "SUCCESS")
                return True
            else:
                log("模組驗證有問題", "WARNING")
                return False
        except Exception as e:
            log(f"執行驗證腳本時發生錯誤: {e}", "ERROR")
            return False
    else:
        log("找不到驗證腳本", "WARNING")
        return False

def create_pyright_config():
    """建立 Pyright 配置"""
    log("建立 Pyright 配置...", "PROGRESS")
    
    config_content = """{
  "exclude": [
    "**/node_modules",
    "**/__pycache__",
    "**/.git",
    "**/backups",
    "**/logs",
    "**/database/backups",
    "**/containers",
    "**/downloads",
    "**/uploads",
    "**/reports",
    "**/.conda",
    "**/venv",
    "**/env",
    "**/.venv",
    "**/dist",
    "**/build",
    "**/*.egg-info",
    "**/cloudflared",
    "**/platform-tools",
    "**/USB_DRIVE",
    "**/USB_DRIVE_NEW",
    "**/memory_store",
    "**/local_storage",
    "**/spatial_3d_system",
    "**/spatiotemporal_system",
    "**/wuchang-V5.1.0",
    "**/五常社區服務系統"
  ],
  "include": [
    "wuchang_os",
    "scripts",
    "config"
  ],
  "reportMissingImports": true,
  "reportMissingTypeStubs": false,
  "pythonVersion": "3.11"
}
"""
    
    config_file = WORKSPACE_PATH / 'pyrightconfig.json'
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        log(f"Pyright 配置已建立: {config_file}", "SUCCESS")
        return True
    except Exception as e:
        log(f"建立 Pyright 配置失敗: {e}", "ERROR")
        return False

def main():
    """主函數 - 執行修正步驟"""
    print("\n" + "=" * 60)
    print("  🤖 地端小J執行安裝修正")
    print("=" * 60)
    print(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    # 階段 1: 基礎環境
    print("\n" + "-" * 60)
    print("階段 1: 基礎環境準備")
    print("-" * 60)
    
    # 1.1 檢查 Docker
    log("檢查 Docker 狀態...", "INFO")
    if not check_docker_running():
        log("Docker 未運行，請手動啟動 Docker Desktop", "WARNING")
        log("等待 Docker 啟動...", "INFO")
        if wait_for_docker():
            log("Docker 已啟動", "SUCCESS")
            results['docker_start'] = True
        else:
            log("Docker 啟動失敗，請手動啟動後重新執行", "ERROR")
            return 1
    else:
        log("Docker 正在運行", "SUCCESS")
        results['docker_start'] = True
    
    # 階段 2: 服務啟動
    print("\n" + "-" * 60)
    print("階段 2: 服務啟動")
    print("-" * 60)
    
    # 2.1 啟動容器
    results['containers_start'] = start_docker_containers()
    time.sleep(5)  # 等待容器啟動
    
    # 2.2 檢查容器狀態
    results['containers_status'] = check_container_status()
    
    # 階段 3: 資料庫處理
    print("\n" + "-" * 60)
    print("階段 3: 資料庫處理")
    print("-" * 60)
    
    # 3.1 檢查資料庫狀態
    results['database_check'] = check_database_status()
    
    # 3.2 修復 IDE 模組
    if results.get('containers_start'):
        results['ide_fix'] = fix_odoo_ide_module()
    else:
        log("跳過 IDE 模組修復（容器未啟動）", "WARNING")
        results['ide_fix'] = False
    
    # 階段 4: 驗證與優化
    print("\n" + "-" * 60)
    print("階段 4: 驗證與優化")
    print("-" * 60)
    
    # 4.1 驗證模組
    if results.get('containers_start'):
        results['module_verify'] = verify_modules()
    else:
        log("跳過模組驗證（容器未啟動）", "WARNING")
        results['module_verify'] = False
    
    # 4.2 建立 Pyright 配置
    results['pyright_config'] = create_pyright_config()
    
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
    
    # 儲存執行報告
    report_file = REPORTS_PATH / f'local_j_execution_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    report_data = {
        'execution_time': datetime.now().isoformat(),
        'results': results,
        'summary': {
            'total': total_steps,
            'success': success_steps,
            'failed': total_steps - success_steps
        }
    }
    
    try:
        import json
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        log(f"執行報告已儲存: {report_file}", "SUCCESS")
    except Exception as e:
        log(f"儲存報告失敗: {e}", "WARNING")
    
    print("\n" + "=" * 60)
    if success_steps == total_steps:
        print("  ✅ 所有步驟執行完成")
    else:
        print("  ⚠️ 部分步驟需要手動處理")
    print("=" * 60)
    
    return 0 if success_steps == total_steps else 1

if __name__ == '__main__':
    sys.exit(main())
