#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cloud_history_database.py

雲端硬碟系統歷史資料庫
- 在雲端硬碟建立系統歷史資料庫
- 分類管理各種資料（備份、健康報告等）
- 未來備份只留路徑檔案（不實際備份內容）
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 設定 UTF-8 編碼輸出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent

# 雲端硬碟資料庫結構
CLOUD_DATABASE_STRUCTURE = {
    "root": "系統歷史資料庫",
    "categories": {
        "backups": {
            "name": "備份",
            "description": "系統備份記錄（只保留路徑）",
            "subcategories": [
                "完整備份",
                "增量備份",
                "設定備份",
                "資料備份"
            ]
        },
        "health_reports": {
            "name": "健康報告",
            "description": "系統健康檢查報告",
            "subcategories": [
                "每日健康報告",
                "週報",
                "月報",
                "異常報告"
            ]
        },
        "deployment_logs": {
            "name": "部署日誌",
            "description": "系統部署和更新記錄",
            "subcategories": [
                "部署記錄",
                "更新記錄",
                "回滾記錄"
            ]
        },
        "audit_logs": {
            "name": "稽核日誌",
            "description": "風險動作稽核記錄",
            "subcategories": [
                "風險動作",
                "授權記錄",
                "變更記錄"
            ]
        },
        "work_logs": {
            "name": "工作日誌",
            "description": "雙J協作工作日誌",
            "subcategories": [
                "地端小j日誌",
                "雲端小j日誌",
                "協作記錄"
            ]
        },
        "dns_changes": {
            "name": "DNS變更記錄",
            "description": "DNS更改清單和記錄",
            "subcategories": [
                "DNS更改清單",
                "DNS替換記錄"
            ]
        },
        "router_configs": {
            "name": "路由器設定",
            "description": "路由器設定備份（只保留路徑）",
            "subcategories": [
                "設定備份",
                "端口轉發記錄",
                "防火牆規則"
            ]
        },
        "system_snapshots": {
            "name": "系統快照",
            "description": "系統狀態快照記錄（只保留路徑）",
            "subcategories": [
                "完整快照",
                "增量快照",
                "配置快照"
            ]
        }
    }
}

# 路徑檔案格式
PATH_FILE_FORMAT = {
    "version": "1.0",
    "file_type": "path_reference",
    "local_path": "",
    "cloud_path": "",
    "file_info": {
        "name": "",
        "size": 0,
        "modified": "",
        "hash": ""
    },
    "metadata": {
        "created": "",
        "category": "",
        "subcategory": "",
        "description": ""
    }
}


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    icons = {"INFO": "ℹ️", "OK": "✅", "WARN": "⚠️", "ERROR": "❌"}
    icon = icons.get(level, "•")
    print(f"{icon} [{timestamp}] [{level}] {message}")


def get_cloud_drive_path() -> Optional[Path]:
    """獲取雲端硬碟路徑"""
    # 嘗試常見的雲端硬碟路徑
    possible_paths = [
        Path(os.path.expanduser("~")) / "Google Drive",
        Path(os.path.expanduser("~")) / "OneDrive",
        Path("J:") / "我的雲端硬碟",
        Path("G:") / "我的雲端硬碟",
    ]
    
    for path in possible_paths:
        if path.exists():
            log(f"找到雲端硬碟: {path}", "OK")
            return path
    
    log("未找到雲端硬碟路徑", "WARN")
    return None


def create_database_structure(cloud_root: Path) -> Dict[str, Any]:
    """建立資料庫結構"""
    log("建立雲端歷史資料庫結構...", "INFO")
    
    database_root = cloud_root / CLOUD_DATABASE_STRUCTURE["root"]
    database_root.mkdir(exist_ok=True)
    
    created_structure = {
        "root": str(database_root),
        "categories": {}
    }
    
    # 建立分類目錄
    for category_id, category_info in CLOUD_DATABASE_STRUCTURE["categories"].items():
        category_path = database_root / category_info["name"]
        category_path.mkdir(exist_ok=True)
        
        created_structure["categories"][category_id] = {
            "path": str(category_path),
            "name": category_info["name"],
            "subcategories": []
        }
        
        # 建立子分類目錄
        for subcategory in category_info.get("subcategories", []):
            subcategory_path = category_path / subcategory
            subcategory_path.mkdir(exist_ok=True)
            created_structure["categories"][category_id]["subcategories"].append({
                "name": subcategory,
                "path": str(subcategory_path)
            })
        
        log(f"  已建立分類: {category_info['name']}", "OK")
    
    # 建立索引檔案
    index_file = database_root / "database_index.json"
    index_data = {
        "version": "1.0",
        "created": datetime.now().isoformat(),
        "structure": created_structure,
        "categories": CLOUD_DATABASE_STRUCTURE["categories"]
    }
    index_file.write_text(
        json.dumps(index_data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    log(f"資料庫結構已建立: {database_root}", "OK")
    return created_structure


def create_path_file(
    local_path: Path,
    category: str,
    subcategory: str = "",
    description: str = ""
) -> Dict[str, Any]:
    """建立路徑檔案（不實際備份內容）"""
    import hashlib
    
    if not local_path.exists():
        return {"error": "檔案不存在"}
    
    # 獲取檔案資訊
    stat = local_path.stat()
    file_size = stat.st_size
    modified_time = datetime.fromtimestamp(stat.st_mtime).isoformat()
    
    # 計算檔案雜湊（可選，用於驗證）
    file_hash = ""
    try:
        if file_size < 100 * 1024 * 1024:  # 只對小於100MB的檔案計算雜湊
            sha256 = hashlib.sha256()
            with open(local_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            file_hash = sha256.hexdigest()
    except:
        pass
    
    # 建立路徑檔案
    path_file = PATH_FILE_FORMAT.copy()
    path_file["local_path"] = str(local_path)
    path_file["file_info"] = {
        "name": local_path.name,
        "size": file_size,
        "modified": modified_time,
        "hash": file_hash
    }
    path_file["metadata"] = {
        "created": datetime.now().isoformat(),
        "category": category,
        "subcategory": subcategory,
        "description": description
    }
    
    return path_file


def save_path_file_to_cloud(
    path_file: Dict[str, Any],
    cloud_root: Path,
    category: str,
    subcategory: str = ""
) -> Optional[Path]:
    """將路徑檔案儲存到雲端"""
    database_root = cloud_root / CLOUD_DATABASE_STRUCTURE["root"]
    category_info = CLOUD_DATABASE_STRUCTURE["categories"].get(category)
    
    if not category_info:
        log(f"未知的分類: {category}", "ERROR")
        return None
    
    category_path = database_root / category_info["name"]
    
    if subcategory:
        category_path = category_path / subcategory
    
    category_path.mkdir(parents=True, exist_ok=True)
    
    # 建立路徑檔案名稱
    file_name = path_file["file_info"]["name"]
    path_file_name = f"{file_name}.path.json"
    path_file_path = category_path / path_file_name
    
    # 設定雲端路徑
    path_file["cloud_path"] = str(path_file_path.relative_to(cloud_root))
    
    # 儲存路徑檔案
    path_file_path.write_text(
        json.dumps(path_file, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    log(f"  路徑檔案已儲存: {path_file_path}", "OK")
    return path_file_path


def archive_backup_path(backup_path: Path, description: str = "") -> bool:
    """歸檔備份路徑（只保留路徑檔案）"""
    log(f"歸檔備份路徑: {backup_path}", "INFO")
    
    cloud_root = get_cloud_drive_path()
    if not cloud_root:
        log("無法找到雲端硬碟路徑", "ERROR")
        return False
    
    # 建立路徑檔案
    path_file = create_path_file(
        backup_path,
        category="backups",
        subcategory="完整備份",
        description=description
    )
    
    if "error" in path_file:
        log(f"建立路徑檔案失敗: {path_file['error']}", "ERROR")
        return False
    
    # 儲存到雲端
    cloud_path = save_path_file_to_cloud(
        path_file,
        cloud_root,
        category="backups",
        subcategory="完整備份"
    )
    
    return cloud_path is not None


def archive_health_report(report_path: Path) -> bool:
    """歸檔健康報告"""
    log(f"歸檔健康報告: {report_path}", "INFO")
    
    cloud_root = get_cloud_drive_path()
    if not cloud_root:
        log("無法找到雲端硬碟路徑", "ERROR")
        return False
    
    # 判斷報告類型
    report_name = report_path.name
    if "每日" in report_name or "daily" in report_name.lower():
        subcategory = "每日健康報告"
    elif "週" in report_name or "week" in report_name.lower():
        subcategory = "週報"
    elif "月" in report_name or "month" in report_name.lower():
        subcategory = "月報"
    else:
        subcategory = "異常報告"
    
    # 建立路徑檔案
    path_file = create_path_file(
        report_path,
        category="health_reports",
        subcategory=subcategory,
        description="系統健康檢查報告"
    )
    
    if "error" in path_file:
        log(f"建立路徑檔案失敗: {path_file['error']}", "ERROR")
        return False
    
    # 儲存到雲端
    cloud_path = save_path_file_to_cloud(
        path_file,
        cloud_root,
        category="health_reports",
        subcategory=subcategory
    )
    
    return cloud_path is not None


def archive_deployment_log(deployment_path: Path) -> bool:
    """歸檔部署日誌"""
    log(f"歸檔部署日誌: {deployment_path}", "INFO")
    
    cloud_root = get_cloud_drive_path()
    if not cloud_root:
        log("無法找到雲端硬碟路徑", "ERROR")
        return False
    
    # 建立路徑檔案
    path_file = create_path_file(
        deployment_path,
        category="deployment_logs",
        subcategory="部署記錄",
        description="系統部署記錄"
    )
    
    if "error" in path_file:
        return False
    
    # 儲存到雲端
    cloud_path = save_path_file_to_cloud(
        path_file,
        cloud_root,
        category="deployment_logs",
        subcategory="部署記錄"
    )
    
    return cloud_path is not None


def archive_all_historical_files() -> Dict[str, Any]:
    """歸檔所有歷史檔案（只保留路徑）"""
    log("開始歸檔所有歷史檔案...", "INFO")
    
    cloud_root = get_cloud_drive_path()
    if not cloud_root:
        return {"ok": False, "error": "無法找到雲端硬碟路徑"}
    
    # 建立資料庫結構
    structure = create_database_structure(cloud_root)
    
    results = {
        "backups": 0,
        "health_reports": 0,
        "deployment_logs": 0,
        "failed": 0
    }
    
    # 歸檔備份
    log("\n歸檔備份...", "INFO")
    backup_dirs = [BASE_DIR / "backups", BASE_DIR / "snapshots"]
    for backup_dir in backup_dirs:
        if backup_dir.exists():
            for backup_file in backup_dir.rglob("*"):
                if backup_file.is_file() and not backup_file.suffix == ".path.json":
                    if archive_backup_path(backup_file):
                        results["backups"] += 1
                    else:
                        results["failed"] += 1
    
    # 歸檔健康報告
    log("\n歸檔健康報告...", "INFO")
    health_report_dir = BASE_DIR / "健康報告"
    if health_report_dir.exists():
        for report_file in health_report_dir.glob("*"):
            if report_file.is_file():
                if archive_health_report(report_file):
                    results["health_reports"] += 1
                else:
                    results["failed"] += 1
    
    # 歸檔部署日誌
    log("\n歸檔部署日誌...", "INFO")
    deployment_files = BASE_DIR.glob("*_report_*.json")
    for deployment_file in deployment_files:
        if "deployment" in deployment_file.name.lower() or "deploy" in deployment_file.name.lower():
            if archive_deployment_log(deployment_file):
                results["deployment_logs"] += 1
            else:
                results["failed"] += 1
    
    results["ok"] = results["failed"] == 0
    return results


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="雲端硬碟系統歷史資料庫管理")
    parser.add_argument("--init", action="store_true", help="初始化資料庫結構")
    parser.add_argument("--archive-all", action="store_true", help="歸檔所有歷史檔案")
    parser.add_argument("--archive-backup", type=str, help="歸檔指定備份檔案")
    parser.add_argument("--archive-report", type=str, help="歸檔指定報告檔案")
    parser.add_argument("--cloud-path", type=str, help="指定雲端硬碟路徑")
    
    args = parser.parse_args()
    
    log("=" * 60, "INFO")
    log("雲端硬碟系統歷史資料庫管理", "INFO")
    log("=" * 60, "INFO")
    
    # 獲取雲端硬碟路徑
    if args.cloud_path:
        cloud_root = Path(args.cloud_path)
    else:
        cloud_root = get_cloud_drive_path()
    
    if not cloud_root:
        log("錯誤: 無法找到雲端硬碟路徑", "ERROR")
        log("請使用 --cloud-path 指定路徑", "INFO")
        return
    
    log(f"雲端硬碟路徑: {cloud_root}", "INFO")
    
    # 初始化資料庫結構
    if args.init:
        log("\n初始化資料庫結構...", "INFO")
        structure = create_database_structure(cloud_root)
        log("資料庫結構初始化完成", "OK")
    
    # 歸檔所有歷史檔案
    if args.archive_all:
        log("\n歸檔所有歷史檔案...", "INFO")
        results = archive_all_historical_files()
        log(f"\n歸檔完成:", "INFO")
        log(f"  備份: {results['backups']} 個", "INFO")
        log(f"  健康報告: {results['health_reports']} 個", "INFO")
        log(f"  部署日誌: {results['deployment_logs']} 個", "INFO")
        if results['failed'] > 0:
            log(f"  失敗: {results['failed']} 個", "ERROR")
    
    # 歸檔指定備份
    if args.archive_backup:
        backup_path = Path(args.archive_backup)
        if archive_backup_path(backup_path):
            log("備份路徑歸檔成功", "OK")
        else:
            log("備份路徑歸檔失敗", "ERROR")
    
    # 歸檔指定報告
    if args.archive_report:
        report_path = Path(args.archive_report)
        if archive_health_report(report_path):
            log("報告歸檔成功", "OK")
        else:
            log("報告歸檔失敗", "ERROR")
    
    log("\n執行完成！", "INFO")
    log("=" * 60, "INFO")


if __name__ == "__main__":
    main()
