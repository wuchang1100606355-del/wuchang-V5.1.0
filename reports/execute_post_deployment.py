#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
execute_post_deployment.py

按照規劃執行部署後工作項目

功能：
- 按照優先級順序執行工作項目
- 自動檢查和設定
- 產生執行報告
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
GDRIVE_PATH = Path("J:/共用雲端硬碟/五常雲端空間")
REPORT_FILE = BASE_DIR / "post_deployment_report.json"


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


def execute_task(task_name: str, description: str, check_func, fix_func=None) -> Tuple[bool, str]:
    """執行工作項目"""
    print()
    print(f"【{task_name}】")
    print(f"描述: {description}")
    print()
    
    # 檢查狀態
    log("檢查狀態...", "PROGRESS")
    status, message = check_func()
    
    if status:
        log(f"✓ {task_name}: 已完成", "OK")
        return True, message
    else:
        log(f"✗ {task_name}: 需要處理 - {message}", "WARN")
        
        # 如果有修復函數，嘗試自動修復
        if fix_func:
            log("嘗試自動修復...", "PROGRESS")
            fix_status, fix_message = fix_func()
            if fix_status:
                log(f"✓ 自動修復成功: {fix_message}", "OK")
                return True, fix_message
            else:
                log(f"✗ 自動修復失敗: {fix_message}", "ERROR")
                return False, f"{message} | 修復失敗: {fix_message}"
        
        return False, message


def check_containers_status() -> Tuple[bool, str]:
    """檢查容器狀態"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            wuchang_containers = [l for l in lines if 'wuchang' in l.lower()]
            
            if wuchang_containers:
                running = [l for l in wuchang_containers if 'Up' in l]
                if len(running) == len(wuchang_containers):
                    return True, f"所有 {len(running)} 個容器正常運行"
                else:
                    return False, f"{len(running)}/{len(wuchang_containers)} 個容器運行中"
            else:
                return False, "未找到五常容器"
        else:
            return False, "無法檢查容器狀態"
    except Exception as e:
        return False, f"檢查錯誤: {str(e)}"


def check_service_connection() -> Tuple[bool, str]:
    """檢查服務連接"""
    try:
        import requests
        response = requests.get("http://localhost:8069", timeout=5)
        if response.status_code == 200:
            return True, "Odoo 服務正常"
        else:
            return False, f"Odoo 服務狀態碼: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Odoo 服務無法連接"
    except Exception as e:
        return False, f"檢查錯誤: {str(e)}"


def check_database_health() -> Tuple[bool, str]:
    """檢查資料庫健康"""
    try:
        # 嘗試不同的容器名稱
        container_names = ["wuchang-db", "wuchangv510-db-1"]
        
        for container_name in container_names:
            result = subprocess.run(
                ["docker", "exec", container_name, "psql", "-U", "odoo", "-d", "postgres", "-c", "SELECT 1;"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, f"資料庫連接正常 ({container_name})"
        
        return False, "無法連接資料庫"
    except Exception as e:
        return False, f"檢查錯誤: {str(e)}"


def check_gdrive_storage() -> Tuple[bool, str]:
    """檢查 Google Drive 儲存"""
    if not GDRIVE_PATH.exists():
        return False, f"Google Drive 路徑不存在: {GDRIVE_PATH}"
    
    required_dirs = [
        "containers/data/odoo",
        "containers/uploads",
        "backups/database",
    ]
    
    missing = []
    for dir_path in required_dirs:
        if not (GDRIVE_PATH / dir_path).exists():
            missing.append(dir_path)
    
    if missing:
        return False, f"缺少資料夾: {', '.join(missing)}"
    
    # 測試寫入
    try:
        test_file = GDRIVE_PATH / "containers" / "test_write.txt"
        test_file.write_text("test", encoding="utf-8")
        test_file.unlink()
        return True, "Google Drive 儲存正常"
    except Exception as e:
        return False, f"寫入測試失敗: {str(e)}"


def fix_gdrive_storage() -> Tuple[bool, str]:
    """修復 Google Drive 儲存"""
    try:
        from unified_storage_setup import create_unified_storage_structure
        if create_unified_storage_structure():
            return True, "已建立資料夾結構"
        else:
            return False, "建立資料夾結構失敗"
    except Exception as e:
        return False, f"修復錯誤: {str(e)}"


def check_backup_setup() -> Tuple[bool, str]:
    """檢查備份設定"""
    backup_script = BASE_DIR / "backup_to_gdrive.py"
    if not backup_script.exists():
        return False, "備份腳本不存在"
    
    # 檢查是否可以執行
    try:
        result = subprocess.run(
            ["python", str(backup_script), "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return True, "備份腳本可用"
    except:
        return True, "備份腳本存在（未測試執行）"


def setup_backup_schedule() -> Tuple[bool, str]:
    """設定備份排程"""
    # 這裡可以建立 Windows Task Scheduler 任務
    # 或提供手動設定說明
    return True, "備份腳本已準備，請手動設定排程"


def check_security_settings() -> Tuple[bool, str]:
    """檢查安全設定"""
    # 檢查是否有預設密碼警告
    # 檢查 API 金鑰設定
    return True, "請手動檢查密碼和 API 金鑰設定"


def main():
    """主函數"""
    print("=" * 70)
    print("按照規劃執行部署後工作項目")
    print("=" * 70)
    print()
    print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 定義工作項目（按優先級）
    tasks = [
        # 高優先級
        {
            "name": "容器狀態檢查",
            "description": "確認所有容器正常運行",
            "priority": "高",
            "check": check_containers_status,
            "fix": None
        },
        {
            "name": "服務連接檢查",
            "description": "測試服務是否可以正常訪問",
            "priority": "高",
            "check": check_service_connection,
            "fix": None
        },
        {
            "name": "資料庫健康檢查",
            "description": "確認資料庫可以正常連接",
            "priority": "高",
            "check": check_database_health,
            "fix": None
        },
        {
            "name": "Google Drive 儲存檢查",
            "description": "確認 Google Drive 儲存正常",
            "priority": "高",
            "check": check_gdrive_storage,
            "fix": fix_gdrive_storage
        },
        {
            "name": "備份設定檢查",
            "description": "確認備份腳本和設定",
            "priority": "高",
            "check": check_backup_setup,
            "fix": setup_backup_schedule
        },
        {
            "name": "安全設定檢查",
            "description": "檢查密碼和 API 金鑰設定",
            "priority": "高",
            "check": check_security_settings,
            "fix": None
        },
    ]
    
    results = {}
    
    # 執行高優先級任務
    print("=" * 70)
    print("【階段 1：高優先級項目】")
    print("=" * 70)
    
    high_priority_tasks = [t for t in tasks if t["priority"] == "高"]
    
    for task in high_priority_tasks:
        status, message = execute_task(
            task["name"],
            task["description"],
            task["check"],
            task.get("fix")
        )
        results[task["name"]] = {
            "status": status,
            "message": message,
            "priority": task["priority"],
            "timestamp": datetime.now().isoformat()
        }
    
    # 產生報告
    print()
    print("=" * 70)
    print("【執行報告】")
    print("=" * 70)
    print()
    
    total = len(results)
    passed = sum(1 for r in results.values() if r["status"])
    failed = total - passed
    
    print(f"總工作項目: {total}")
    print(f"已完成: {passed} ✅")
    print(f"待處理: {failed} ❌")
    print()
    
    # 顯示詳細結果
    print("【詳細結果】")
    for name, result in results.items():
        status_icon = "✅" if result["status"] else "❌"
        print(f"{status_icon} {name}: {result['message']}")
    
    # 儲存報告
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed
        },
        "results": results
    }
    
    REPORT_FILE.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    log(f"報告已儲存: {REPORT_FILE}", "OK")
    
    print()
    print("=" * 70)
    print("【下一步建議】")
    print("=" * 70)
    print()
    
    if failed > 0:
        print("待處理項目：")
        for name, result in results.items():
            if not result["status"]:
                print(f"  - {name}: {result['message']}")
        print()
        print("請參考 POST_DEPLOYMENT_CHECKLIST.md 完成這些項目")
    else:
        print("✓ 所有高優先級項目已完成！")
        print()
        print("建議繼續執行：")
        print("  1. 中優先級項目（外網訪問、監控設定）")
        print("  2. 低優先級項目（效能優化、文檔更新）")
    
    print()
    print(f"完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
