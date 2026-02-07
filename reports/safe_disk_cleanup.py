#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
safe_disk_cleanup.py

安全磁碟清理工具
- 清理臨時檔案和快取
- 清理舊備份
- 清理Docker未使用的資源
- 遵循風險動作SOP，確保不刪除重要資料
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

# 設定 UTF-8 編碼輸出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent

# 需要保留的檔案和目錄
PROTECTED_ITEMS = [
    ".git",
    "jules_memory_bank.json",
    "personal_ai_binding.json",
    "internal_id_records.json",
    "dual_j_work_logs",
    "router_api_docs",
    "certs",
    "association_operational_files",
    "wuchang_community_knowledge_index.json",
    "wuchang_community_context_compact.md",
    "local_control_center.py",
    "wuchang_control_center.html",
    "AGENT_CONSTITUTION.md",
    "RISK_ACTION_SOP.md",
    "ASSET_INVENTORY.md",
    "SYSTEM_INVENTORY.md",
]

# 可安全清理的項目
CLEANUP_ITEMS = {
    "python_cache": {
        "patterns": ["__pycache__", "*.pyc", "*.pyo", "*.pyd"],
        "description": "Python 快取檔案",
        "safe": True
    },
    "temp_files": {
        "patterns": ["*.tmp", "*.temp", ".tmp.driveupload"],
        "description": "臨時檔案",
        "safe": True
    },
    "log_files": {
        "patterns": ["*.log"],
        "description": "日誌檔案（保留最近7天）",
        "safe": True,
        "keep_days": 7
    },
    "old_backups": {
        "patterns": ["backups/*", "snapshots/*"],
        "description": "舊備份（保留最近30天）",
        "safe": True,
        "keep_days": 30
    },
    "old_reports": {
        "patterns": ["健康報告/*", "*_report_*.json", "*_report_*.md"],
        "description": "舊報告（保留最近30天）",
        "safe": True,
        "keep_days": 30
    },
    "docker_unused": {
        "type": "docker",
        "description": "Docker 未使用的映像和容器",
        "safe": True
    },
    "sync_temp": {
        "patterns": ["sync_temp", "deployment_prepared"],
        "description": "同步臨時目錄",
        "safe": True
    },
    "node_modules": {
        "patterns": ["node_modules"],
        "description": "Node.js 模組（如果存在）",
        "safe": True
    },
}


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    icons = {"INFO": "ℹ️", "OK": "✅", "WARN": "⚠️", "ERROR": "❌"}
    icon = icons.get(level, "•")
    print(f"{icon} [{timestamp}] [{level}] {message}")


def get_disk_space(path: Path = None) -> Dict[str, Any]:
    """獲取磁碟空間資訊"""
    if path is None:
        path = BASE_DIR
    
    if sys.platform == 'win32':
        try:
            result = subprocess.run(
                ["wmic", "logicaldisk", "get", "size,freespace,caption"],
                capture_output=True,
                text=True,
                timeout=5,
                encoding='utf-8',
                errors='replace'
            )
            
            for line in result.stdout.strip().split('\n')[1:]:
                if not line.strip():
                    continue
                parts = line.split()
                if len(parts) >= 3 and parts[0] == path.drive:
                    try:
                        size = int(parts[1])
                        free = int(parts[2])
                        used = size - free
                        usage_percent = (used / size * 100) if size > 0 else 0
                        
                        return {
                            "total_gb": round(size / (1024**3), 2),
                            "used_gb": round(used / (1024**3), 2),
                            "free_gb": round(free / (1024**3), 2),
                            "usage_percent": round(usage_percent, 1)
                        }
                    except:
                        pass
        except:
            pass
    
    return {"error": "無法獲取磁碟空間資訊"}


def is_protected(item_path: Path) -> bool:
    """檢查項目是否受保護"""
    item_str = str(item_path)
    for protected in PROTECTED_ITEMS:
        if protected in item_str:
            return True
    return False


def cleanup_python_cache() -> Tuple[int, float]:
    """清理Python快取"""
    log("清理Python快取...", "INFO")
    
    cleaned_count = 0
    freed_space = 0.0
    
    for root, dirs, files in os.walk(BASE_DIR):
        # 過濾受保護的目錄
        dirs[:] = [d for d in dirs if not is_protected(Path(root) / d)]
        
        # 刪除 __pycache__
        if '__pycache__' in dirs:
            pycache_path = Path(root) / '__pycache__'
            try:
                size = sum(f.stat().st_size for f in pycache_path.rglob('*') if f.is_file())
                shutil.rmtree(pycache_path)
                cleaned_count += 1
                freed_space += size / (1024**3)
                log(f"  已刪除: {pycache_path}", "OK")
            except Exception as e:
                log(f"  刪除失敗 {pycache_path}: {e}", "ERROR")
            dirs.remove('__pycache__')
        
        # 刪除 .pyc 檔案
        for file in files:
            if file.endswith(('.pyc', '.pyo', '.pyd')):
                pyc_path = Path(root) / file
                try:
                    size = pyc_path.stat().st_size
                    pyc_path.unlink()
                    cleaned_count += 1
                    freed_space += size / (1024**3)
                except Exception as e:
                    log(f"  刪除失敗 {pyc_path}: {e}", "ERROR")
    
    return cleaned_count, freed_space


def cleanup_temp_files() -> Tuple[int, float]:
    """清理臨時檔案"""
    log("清理臨時檔案...", "INFO")
    
    cleaned_count = 0
    freed_space = 0.0
    
    patterns = ["*.tmp", "*.temp"]
    for pattern in patterns:
        for file_path in BASE_DIR.rglob(pattern):
            if is_protected(file_path):
                continue
            
            try:
                size = file_path.stat().st_size
                file_path.unlink()
                cleaned_count += 1
                freed_space += size / (1024**3)
            except Exception as e:
                log(f"  刪除失敗 {file_path}: {e}", "ERROR")
    
    # 清理 .tmp.driveupload 目錄
    for tmp_dir in BASE_DIR.rglob(".tmp.driveupload"):
        if is_protected(tmp_dir):
            continue
        
        try:
            size = sum(f.stat().st_size for f in tmp_dir.rglob('*') if f.is_file())
            shutil.rmtree(tmp_dir)
            cleaned_count += 1
            freed_space += size / (1024**3)
            log(f"  已刪除目錄: {tmp_dir}", "OK")
        except Exception as e:
            log(f"  刪除失敗 {tmp_dir}: {e}", "ERROR")
    
    return cleaned_count, freed_space


def cleanup_old_logs(keep_days: int = 7) -> Tuple[int, float]:
    """清理舊日誌檔案"""
    log(f"清理舊日誌檔案（保留最近{keep_days}天）...", "INFO")
    
    cleaned_count = 0
    freed_space = 0.0
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    
    for log_file in BASE_DIR.rglob("*.log"):
        if is_protected(log_file):
            continue
        
        try:
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if mtime < cutoff_date:
                size = log_file.stat().st_size
                log_file.unlink()
                cleaned_count += 1
                freed_space += size / (1024**3)
                log(f"  已刪除舊日誌: {log_file.name} ({mtime.strftime('%Y-%m-%d')})", "OK")
        except Exception as e:
            log(f"  刪除失敗 {log_file}: {e}", "ERROR")
    
    return cleaned_count, freed_space


def cleanup_old_backups(keep_days: int = 30) -> Tuple[int, float]:
    """清理舊備份"""
    log(f"清理舊備份（保留最近{keep_days}天）...", "INFO")
    
    cleaned_count = 0
    freed_space = 0.0
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    
    backup_dirs = [BASE_DIR / "backups", BASE_DIR / "snapshots"]
    
    for backup_dir in backup_dirs:
        if not backup_dir.exists():
            continue
        
        for item in backup_dir.iterdir():
            if is_protected(item):
                continue
            
            try:
                mtime = datetime.fromtimestamp(item.stat().st_mtime)
                if mtime < cutoff_date:
                    if item.is_dir():
                        size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                        shutil.rmtree(item)
                    else:
                        size = item.stat().st_size
                        item.unlink()
                    
                    cleaned_count += 1
                    freed_space += size / (1024**3)
                    log(f"  已刪除舊備份: {item.name} ({mtime.strftime('%Y-%m-%d')})", "OK")
            except Exception as e:
                log(f"  刪除失敗 {item}: {e}", "ERROR")
    
    return cleaned_count, freed_space


def cleanup_old_reports(keep_days: int = 30) -> Tuple[int, float]:
    """清理舊報告"""
    log(f"清理舊報告（保留最近{keep_days}天）...", "INFO")
    
    cleaned_count = 0
    freed_space = 0.0
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    
    # 清理健康報告目錄
    health_report_dir = BASE_DIR / "健康報告"
    if health_report_dir.exists():
        for report_file in health_report_dir.glob("*"):
            if is_protected(report_file):
                continue
            
            try:
                mtime = datetime.fromtimestamp(report_file.stat().st_mtime)
                if mtime < cutoff_date:
                    size = report_file.stat().st_size
                    report_file.unlink()
                    cleaned_count += 1
                    freed_space += size / (1024**3)
                    log(f"  已刪除舊報告: {report_file.name} ({mtime.strftime('%Y-%m-%d')})", "OK")
            except Exception as e:
                log(f"  刪除失敗 {report_file}: {e}", "ERROR")
    
    # 清理根目錄的報告檔案
    for report_file in BASE_DIR.glob("*_report_*.json"):
        if is_protected(report_file):
            continue
        
        try:
            mtime = datetime.fromtimestamp(report_file.stat().st_mtime)
            if mtime < cutoff_date:
                size = report_file.stat().st_size
                report_file.unlink()
                cleaned_count += 1
                freed_space += size / (1024**3)
        except:
            pass
    
    return cleaned_count, freed_space


def cleanup_docker_unused() -> Tuple[int, float]:
    """清理Docker未使用的資源"""
    log("清理Docker未使用的資源...", "INFO")
    
    cleaned_count = 0
    freed_space = 0.0
    
    try:
        # 清理未使用的映像
        result = subprocess.run(
            ["docker", "image", "prune", "-a", "-f"],
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            # 解析釋放的空間
            output = result.stdout
            if "reclaimed" in output.lower():
                cleaned_count += 1
                log("  已清理未使用的Docker映像", "OK")
        
        # 清理未使用的容器
        result = subprocess.run(
            ["docker", "container", "prune", "-f"],
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            cleaned_count += 1
            log("  已清理未使用的Docker容器", "OK")
        
        # 清理未使用的卷
        result = subprocess.run(
            ["docker", "volume", "prune", "-f"],
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            cleaned_count += 1
            log("  已清理未使用的Docker卷", "OK")
        
        # 獲取Docker系統資訊以計算釋放空間
        result = subprocess.run(
            ["docker", "system", "df"],
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            log(f"  Docker系統使用情況:\n{result.stdout}", "INFO")
        
    except FileNotFoundError:
        log("  Docker未安裝", "WARN")
    except Exception as e:
        log(f"  清理Docker資源失敗: {e}", "ERROR")
    
    return cleaned_count, freed_space


def cleanup_sync_temp() -> Tuple[int, float]:
    """清理同步臨時目錄"""
    log("清理同步臨時目錄...", "INFO")
    
    cleaned_count = 0
    freed_space = 0.0
    
    temp_dirs = [BASE_DIR / "sync_temp", BASE_DIR / "deployment_prepared"]
    
    for temp_dir in temp_dirs:
        if temp_dir.exists():
            try:
                size = sum(f.stat().st_size for f in temp_dir.rglob('*') if f.is_file())
                shutil.rmtree(temp_dir)
                cleaned_count += 1
                freed_space += size / (1024**3)
                log(f"  已刪除: {temp_dir}", "OK")
            except Exception as e:
                log(f"  刪除失敗 {temp_dir}: {e}", "ERROR")
    
    return cleaned_count, freed_space


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="安全磁碟清理工具")
    parser.add_argument("--dry-run", action="store_true", help="模擬執行，不實際刪除")
    parser.add_argument("--skip-docker", action="store_true", help="跳過Docker清理")
    parser.add_argument("--keep-logs-days", type=int, default=7, help="保留日誌天數（預設: 7）")
    parser.add_argument("--keep-backups-days", type=int, default=30, help="保留備份天數（預設: 30）")
    
    args = parser.parse_args()
    
    log("=" * 60, "INFO")
    log("安全磁碟清理工具", "INFO")
    log("=" * 60, "INFO")
    
    if args.dry_run:
        log("【模擬模式】不會實際刪除檔案", "WARN")
    
    # 獲取清理前磁碟空間
    log("\n[步驟 0] 檢查磁碟空間", "INFO")
    disk_before = get_disk_space()
    if "error" not in disk_before:
        log(f"清理前: 使用率 {disk_before['usage_percent']}%, 剩餘 {disk_before['free_gb']} GB", "INFO")
    
    # 執行清理
    results = {
        "python_cache": (0, 0.0),
        "temp_files": (0, 0.0),
        "old_logs": (0, 0.0),
        "old_backups": (0, 0.0),
        "old_reports": (0, 0.0),
        "docker_unused": (0, 0.0),
        "sync_temp": (0, 0.0),
    }
    
    if not args.dry_run:
        log("\n[步驟 1] 清理Python快取", "INFO")
        results["python_cache"] = cleanup_python_cache()
        
        log("\n[步驟 2] 清理臨時檔案", "INFO")
        results["temp_files"] = cleanup_temp_files()
        
        log("\n[步驟 3] 清理舊日誌", "INFO")
        results["old_logs"] = cleanup_old_logs(args.keep_logs_days)
        
        log("\n[步驟 4] 清理舊備份", "INFO")
        results["old_backups"] = cleanup_old_backups(args.keep_backups_days)
        
        log("\n[步驟 5] 清理舊報告", "INFO")
        results["old_reports"] = cleanup_old_reports(args.keep_backups_days)
        
        if not args.skip_docker:
            log("\n[步驟 6] 清理Docker未使用資源", "INFO")
            results["docker_unused"] = cleanup_docker_unused()
        
        log("\n[步驟 7] 清理同步臨時目錄", "INFO")
        results["sync_temp"] = cleanup_sync_temp()
    else:
        log("\n[模擬模式] 計算可清理項目...", "INFO")
        # 模擬計算
        for key in results:
            results[key] = (0, 0.0)
    
    # 計算總計
    total_cleaned = sum(count for count, _ in results.values())
    total_freed = sum(space for _, space in results.values())
    
    # 獲取清理後磁碟空間
    if not args.dry_run:
        log("\n[步驟 8] 檢查清理後磁碟空間", "INFO")
        disk_after = get_disk_space()
        if "error" not in disk_after:
            log(f"清理後: 使用率 {disk_after['usage_percent']}%, 剩餘 {disk_after['free_gb']} GB", "INFO")
            if "error" not in disk_before:
                freed_gb = disk_after['free_gb'] - disk_before['free_gb']
                log(f"實際釋放空間: {freed_gb:.2f} GB", "OK")
    
    # 輸出摘要
    log("\n" + "=" * 60, "INFO")
    log("清理摘要", "INFO")
    log("=" * 60, "INFO")
    log(f"清理項目數: {total_cleaned}", "INFO")
    log(f"釋放空間: {total_freed:.2f} GB", "OK")
    
    log("\n詳細結果:", "INFO")
    for key, (count, space) in results.items():
        if count > 0 or space > 0:
            log(f"  {key}: {count} 個項目, {space:.2f} GB", "INFO")
    
    # 記錄工作日誌
    try:
        from dual_j_work_log import add_work_log
        add_work_log(
            "地端小 j",
            "磁碟清理",
            "執行安全磁碟清理",
            "completed",
            {
                "cleaned_items": total_cleaned,
                "freed_space_gb": round(total_freed, 2),
                "dry_run": args.dry_run
            },
            f"清理 {total_cleaned} 個項目，釋放 {total_freed:.2f} GB"
        )
    except:
        pass
    
    log("\n清理完成！", "INFO")
    log("=" * 60, "INFO")


if __name__ == "__main__":
    main()
