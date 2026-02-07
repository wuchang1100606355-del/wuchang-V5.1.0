#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
disk_cleanup.py

磁碟清理工具

功能：
- 識別並清理臨時文件
- 清理報告文件
- 清理任務文件
- 清理日誌文件
- 清理快取文件
- 顯示清理統計
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent


def get_file_size_mb(file_path: Path) -> float:
    """獲取文件大小（MB）"""
    try:
        return file_path.stat().st_size / (1024 * 1024)
    except Exception:
        return 0.0


def find_files_to_clean() -> Dict[str, List[Tuple[Path, float]]]:
    """找出需要清理的文件"""
    files_to_clean = {
        "reports": [],      # 報告文件
        "tasks": [],        # 任務文件
        "logs": [],         # 日誌文件
        "cache": [],        # 快取文件
        "temp": [],         # 臨時文件
        "old_snapshots": [], # 舊快照
    }
    
    # 報告文件模式
    report_patterns = [
        "*_report.json",
        "*_status.json",
        "*_audit_report.json",
        "*_verification_report.json",
        "*_execution_report.json",
        "file_diff_report_*.json",
        "dns_status_report.json",
        "domain_deployment_status.json",
        "environment_calibration_report.json",
        "module_installation_report.json",
        "post_deployment_report.json",
        "workspace_status_report.json",
        "auto_sync_execution_report.json",
        "system_issues_report.json",
        "server_response_report.json",
        "uninstall_restart_report.json",
        "server_push_restart_report.json",
        "plan_execution_report.json",
    ]
    
    # 任務文件模式
    task_patterns = [
        "jules_task_*.json",
        "*_task_*.md",
        "network_fix_task_*.md",
        "container_management_task_*.md",
        "file_optimization_task_*.md",
        "system_deployment_suggestion_task_*.md",
    ]
    
    # 日誌文件模式
    log_patterns = [
        "*.log",
        "*.jsonl",
    ]
    
    # 快取目錄
    cache_dirs = [
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "*.pyc",
        "*.pyo",
        "*.pyd",
    ]
    
    # 臨時文件模式
    temp_patterns = [
        "*.tmp",
        "*.temp",
        "*.bak",
        "*.swp",
        "*.swo",
        "*~",
    ]
    
    # 掃描文件
    for file_path in BASE_DIR.rglob("*"):
        if not file_path.is_file():
            continue
        
        # 跳過 .git 目錄
        if ".git" in file_path.parts:
            continue
        
        # 跳過重要配置文件
        important_files = {
            "google_credentials.json",
            "google_token.json",
            ".secrets.json",
            "accounts_policy.json",
            "auto_auth_config.json",
            "network_interconnection_config.json",
            "wuchang_community_knowledge_base.json",
            "wuchang_community_knowledge_index.json",
            "jules_personality_profile.json",
            "jules_memory_bank.json",
            "personal_ai_binding.json",
            "internal_id_records.json",
        }
        if file_path.name in important_files:
            continue
        
        file_size_mb = get_file_size_mb(file_path)
        
        # 檢查報告文件
        for pattern in report_patterns:
            if file_path.match(pattern):
                files_to_clean["reports"].append((file_path, file_size_mb))
                break
        
        # 檢查任務文件
        for pattern in task_patterns:
            if file_path.match(pattern):
                files_to_clean["tasks"].append((file_path, file_size_mb))
                break
        
        # 檢查日誌文件
        for pattern in log_patterns:
            if file_path.match(pattern):
                files_to_clean["logs"].append((file_path, file_size_mb))
                break
        
        # 檢查臨時文件
        for pattern in temp_patterns:
            if file_path.match(pattern):
                files_to_clean["temp"].append((file_path, file_size_mb))
                break
    
    # 掃描快取目錄
    for cache_dir in BASE_DIR.rglob("__pycache__"):
        if cache_dir.is_dir():
            total_size = 0.0
            for file_path in cache_dir.rglob("*"):
                if file_path.is_file():
                    total_size += get_file_size_mb(file_path)
            if total_size > 0:
                files_to_clean["cache"].append((cache_dir, total_size))
    
    # 掃描 Python 編譯文件
    for pyc_file in BASE_DIR.rglob("*.pyc"):
        if pyc_file.is_file():
            files_to_clean["cache"].append((pyc_file, get_file_size_mb(pyc_file)))
    
    for pyo_file in BASE_DIR.rglob("*.pyo"):
        if pyo_file.is_file():
            files_to_clean["cache"].append((pyo_file, get_file_size_mb(pyo_file)))
    
    # 檢查舊快照（保留最近 7 天的）
    snapshots_dir = BASE_DIR / "snapshots"
    if snapshots_dir.exists():
        cutoff_date = datetime.now() - timedelta(days=7)
        for snapshot_dir in snapshots_dir.iterdir():
            if snapshot_dir.is_dir():
                try:
                    # 從目錄名稱提取日期（格式：snapshot_YYYYMMDD_HHMMSS）
                    dir_name = snapshot_dir.name
                    if dir_name.startswith("snapshot_"):
                        date_str = dir_name.replace("snapshot_", "").split("_")[0]
                        snapshot_date = datetime.strptime(date_str, "%Y%m%d")
                        if snapshot_date < cutoff_date:
                            total_size = sum(
                                get_file_size_mb(f) for f in snapshot_dir.rglob("*") if f.is_file()
                            )
                            if total_size > 0:
                                files_to_clean["old_snapshots"].append((snapshot_dir, total_size))
                except Exception:
                    pass
    
    return files_to_clean


def clean_files(files_to_clean: Dict[str, List[Tuple[Path, float]]], dry_run: bool = True) -> Dict[str, Dict]:
    """清理文件"""
    results = {
        "reports": {"count": 0, "size_mb": 0.0, "files": []},
        "tasks": {"count": 0, "size_mb": 0.0, "files": []},
        "logs": {"count": 0, "size_mb": 0.0, "files": []},
        "cache": {"count": 0, "size_mb": 0.0, "files": []},
        "temp": {"count": 0, "size_mb": 0.0, "files": []},
        "old_snapshots": {"count": 0, "size_mb": 0.0, "files": []},
    }
    
    for category, file_list in files_to_clean.items():
        for file_path, size_mb in file_list:
            results[category]["count"] += 1
            results[category]["size_mb"] += size_mb
            results[category]["files"].append(str(file_path))
            
            if not dry_run:
                try:
                    if file_path.is_file():
                        file_path.unlink()
                    elif file_path.is_dir():
                        import shutil
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"  錯誤：無法刪除 {file_path}: {e}", file=sys.stderr)
    
    return results


def print_summary(results: Dict[str, Dict], dry_run: bool = True):
    """打印清理摘要"""
    print("\n" + "=" * 60)
    print("磁碟清理摘要")
    print("=" * 60)
    
    total_count = 0
    total_size = 0.0
    
    for category, data in results.items():
        if data["count"] > 0:
            category_name = {
                "reports": "報告文件",
                "tasks": "任務文件",
                "logs": "日誌文件",
                "cache": "快取文件",
                "temp": "臨時文件",
                "old_snapshots": "舊快照",
            }.get(category, category)
            
            print(f"\n{category_name}:")
            print(f"  數量: {data['count']}")
            print(f"  大小: {data['size_mb']:.2f} MB")
            
            total_count += data["count"]
            total_size += data["size_mb"]
    
    print("\n" + "-" * 60)
    print(f"總計:")
    print(f"  文件/目錄數: {total_count}")
    print(f"  總大小: {total_size:.2f} MB ({total_size/1024:.2f} GB)")
    print("=" * 60)
    
    if dry_run:
        print("\n這是預覽模式，尚未實際刪除文件。")
        print("使用 --execute 參數來執行實際清理。")
    else:
        print("\n清理完成！")


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="磁碟清理工具")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="執行實際清理（預設為預覽模式）",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出將要清理的文件",
    )
    
    args = parser.parse_args()
    
    print("正在掃描文件...")
    files_to_clean = find_files_to_clean()
    
    if args.list:
        print("\n將要清理的文件列表：")
        for category, file_list in files_to_clean.items():
            if file_list:
                category_name = {
                    "reports": "報告文件",
                    "tasks": "任務文件",
                    "logs": "日誌文件",
                    "cache": "快取文件",
                    "temp": "臨時文件",
                    "old_snapshots": "舊快照",
                }.get(category, category)
                print(f"\n{category_name}:")
                for file_path, size_mb in file_list:
                    print(f"  {file_path} ({size_mb:.2f} MB)")
    
    dry_run = not args.execute
    results = clean_files(files_to_clean, dry_run=dry_run)
    print_summary(results, dry_run=dry_run)


if __name__ == "__main__":
    main()
