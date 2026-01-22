#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
complete_uninstall.py

完整卸載系統
- 停止所有服務
- 清理容器
- 清理檔案
- 備份重要資料
"""

import sys
import json
import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 設定 UTF-8 編碼輸出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent

# 需要備份的檔案和目錄
BACKUP_ITEMS = [
    "jules_memory_bank.json",
    "personal_ai_binding.json",
    "internal_id_records.json",
    "dual_j_work_logs",
    "router_api_docs",
    "certs",
    "association_operational_files",
    "wuchang_community_knowledge_index.json",
    "wuchang_community_context_compact.md",
    "dns_records.json",
]

# 需要保留的檔案（不刪除）
KEEP_ITEMS = [
    ".git",
    ".gitignore",
    "README.md",
    "AGENT_CONSTITUTION.md",
    "RISK_ACTION_SOP.md",
    "ASSET_INVENTORY.md",
    "SYSTEM_INVENTORY.md",
]

# 需要清理的目錄
CLEANUP_DIRS = [
    "__pycache__",
    ".pytest_cache",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "sync_temp",
    "snapshots",
    "test_server_dir",
]

# 需要停止的服務
SERVICES_TO_STOP = [
    "local_control_center.py",
    "little_j_jules_container_collaboration.py",
    "auto_jules_task_executor.py",
]


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    print(log_entry)


def stop_services() -> bool:
    """停止所有服務"""
    log("停止所有服務...", "INFO")
    
    success = True
    for service in SERVICES_TO_STOP:
        try:
            # 在 Windows 上使用 taskkill
            if sys.platform == 'win32':
                result = subprocess.run(
                    ["taskkill", "/F", "/IM", service, "/T"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    log(f"  已停止: {service}", "INFO")
                elif "找不到" in result.stderr or "not found" in result.stderr.lower():
                    log(f"  服務未運行: {service}", "INFO")
                else:
                    log(f"  停止失敗: {service}", "WARN")
            else:
                # Linux/Mac 使用 pkill
                subprocess.run(["pkill", "-f", service], timeout=10)
                log(f"  已停止: {service}", "INFO")
        except Exception as e:
            log(f"  停止服務失敗 {service}: {e}", "ERROR")
            success = False
    
    return success


def stop_docker_containers() -> bool:
    """停止 Docker 容器"""
    log("停止 Docker 容器...", "INFO")
    
    try:
        # 檢查 Docker 是否運行
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            log("  Docker 未運行或不可用", "INFO")
            return True
        
        # 停止所有容器
        result = subprocess.run(
            ["docker", "stop", "$(docker ps -q)"],
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            log("  已停止所有 Docker 容器", "INFO")
        else:
            # 嘗試逐個停止
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                containers = [c.strip() for c in result.stdout.split('\n') if c.strip()]
                for container in containers:
                    subprocess.run(["docker", "stop", container], timeout=10)
                log(f"  已停止 {len(containers)} 個容器", "INFO")
        
        return True
    except FileNotFoundError:
        log("  Docker 未安裝", "INFO")
        return True
    except Exception as e:
        log(f"  停止容器失敗: {e}", "ERROR")
        return False


def backup_important_files(backup_dir: Path) -> bool:
    """備份重要檔案"""
    log(f"備份重要檔案到: {backup_dir}", "INFO")
    
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"backup_{timestamp}"
    backup_path.mkdir(exist_ok=True)
    
    backed_up = []
    failed = []
    
    for item in BACKUP_ITEMS:
        source = BASE_DIR / item
        if source.exists():
            try:
                dest = backup_path / item
                if source.is_dir():
                    shutil.copytree(source, dest, dirs_exist_ok=True)
                else:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, dest)
                backed_up.append(item)
                log(f"  已備份: {item}", "INFO")
            except Exception as e:
                log(f"  備份失敗 {item}: {e}", "ERROR")
                failed.append(item)
        else:
            log(f"  不存在，跳過: {item}", "INFO")
    
    # 生成備份清單
    backup_manifest = {
        "timestamp": datetime.now().isoformat(),
        "backup_path": str(backup_path),
        "backed_up": backed_up,
        "failed": failed
    }
    
    manifest_file = backup_path / "backup_manifest.json"
    manifest_file.write_text(
        json.dumps(backup_manifest, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    log(f"備份完成: {len(backed_up)} 個項目", "INFO")
    if failed:
        log(f"備份失敗: {len(failed)} 個項目", "ERROR")
    
    return len(failed) == 0


def cleanup_files() -> bool:
    """清理檔案和目錄"""
    log("清理檔案和目錄...", "INFO")
    
    cleaned = 0
    failed = 0
    
    # 清理 Python 快取
    for root, dirs, files in os.walk(BASE_DIR):
        # 過濾要保留的目錄
        dirs[:] = [d for d in dirs if d not in KEEP_ITEMS and not d.startswith('.git')]
        
        # 刪除 __pycache__
        if '__pycache__' in dirs:
            pycache_path = Path(root) / '__pycache__'
            try:
                shutil.rmtree(pycache_path)
                cleaned += 1
                log(f"  已刪除: {pycache_path}", "INFO")
            except Exception as e:
                log(f"  刪除失敗 {pycache_path}: {e}", "ERROR")
                failed += 1
            dirs.remove('__pycache__')
        
        # 刪除 .pyc 檔案
        for file in files:
            if file.endswith(('.pyc', '.pyo', '.pyd')):
                pyc_path = Path(root) / file
                try:
                    pyc_path.unlink()
                    cleaned += 1
                except Exception as e:
                    log(f"  刪除失敗 {pyc_path}: {e}", "ERROR")
                    failed += 1
    
    # 清理其他目錄
    for cleanup_pattern in CLEANUP_DIRS:
        if '*' in cleanup_pattern:
            # 處理萬用字元
            pattern = cleanup_pattern.replace('*', '')
            for item in BASE_DIR.rglob(pattern):
                if item.is_dir() and item.name not in KEEP_ITEMS:
                    try:
                        shutil.rmtree(item)
                        cleaned += 1
                        log(f"  已刪除: {item}", "INFO")
                    except Exception as e:
                        log(f"  刪除失敗 {item}: {e}", "ERROR")
                        failed += 1
        else:
            cleanup_path = BASE_DIR / cleanup_pattern
            if cleanup_path.exists() and cleanup_path.name not in KEEP_ITEMS:
                try:
                    if cleanup_path.is_dir():
                        shutil.rmtree(cleanup_path)
                    else:
                        cleanup_path.unlink()
                    cleaned += 1
                    log(f"  已刪除: {cleanup_path}", "INFO")
                except Exception as e:
                    log(f"  刪除失敗 {cleanup_path}: {e}", "ERROR")
                    failed += 1
    
    log(f"清理完成: {cleaned} 個項目，失敗 {failed} 個", "INFO")
    return failed == 0


def generate_uninstall_report() -> Path:
    """生成卸載報告"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "uninstall_type": "complete",
        "backup_items": BACKUP_ITEMS,
        "cleaned_items": CLEANUP_DIRS,
        "services_stopped": SERVICES_TO_STOP
    }
    
    report_file = BASE_DIR / f"uninstall_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    return report_file


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="完整卸載系統")
    parser.add_argument("--backup-dir", default=None, help="備份目錄（預設: backups/）")
    parser.add_argument("--no-backup", action="store_true", help="不備份，直接卸載")
    parser.add_argument("--no-cleanup", action="store_true", help="不清理檔案")
    parser.add_argument("--dry-run", action="store_true", help="模擬執行")
    
    args = parser.parse_args()
    
    log("=" * 60, "INFO")
    log("完整卸載系統", "INFO")
    log("=" * 60, "INFO")
    
    if args.dry_run:
        log("【模擬模式】不會實際執行卸載", "INFO")
    
    # 1. 停止服務
    if not args.dry_run:
        log("\n[步驟 1] 停止服務", "INFO")
        stop_services()
        stop_docker_containers()
    
    # 2. 備份重要檔案
    if not args.no_backup and not args.dry_run:
        log("\n[步驟 2] 備份重要檔案", "INFO")
        backup_dir = Path(args.backup_dir) if args.backup_dir else BASE_DIR / "backups"
        backup_important_files(backup_dir)
    
    # 3. 清理檔案
    if not args.no_cleanup and not args.dry_run:
        log("\n[步驟 3] 清理檔案", "INFO")
        cleanup_files()
    
    # 4. 生成報告
    log("\n[步驟 4] 生成卸載報告", "INFO")
    report_file = generate_uninstall_report()
    log(f"卸載報告已儲存: {report_file}", "INFO")
    
    log("\n卸載完成！", "INFO")
    log("=" * 60, "INFO")


if __name__ == "__main__":
    main()
