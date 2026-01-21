#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diagnose_server_path_issue.py

診斷伺服器無法讀取資料庫及開發模組的根本原因
"""

from __future__ import annotations

import sys
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

# 從 docker-compose.unified.yml 中提取的路徑
DOCKER_COMPOSE_PATHS = {
    "資料庫數據": Path(r"C:/wuchang V5.1.0/wuchang-V5.1.0/local_storage/database/data"),
    "資料庫備份": Path(r"C:/wuchang V5.1.0/wuchang-V5.1.0/local_storage/database/backups"),
    "Odoo 模組": Path("./wuchang_os/addons"),  # 相對路徑
    "Odoo 數據": Path(r"J:/共用雲端硬碟/五常雲端空間/containers/data/odoo"),
    "Odoo 上傳": Path(r"J:/共用雲端硬碟/五常雲端空間/containers/uploads"),
}

# 實際檔案位置
ACTUAL_PATHS = {
    "Odoo 模組（雲端）": Path(r"J:\共用雲端硬碟\五常雲端空間\wuchang_os\addons"),
    "Odoo 模組（本地）": Path(r"Z:\wuchang_os\addons"),
    "資料庫數據（本地）": Path(r"C:\wuchang V5.1.0\wuchang-V5.1.0\local_storage\database\data"),
    "資料庫備份（本地）": Path(r"C:\wuchang V5.1.0\wuchang-V5.1.0\local_storage\database\backups"),
}

def check_path(path: Path, base_dir: Path = None) -> dict:
    """檢查路徑"""
    result = {
        "path": str(path),
        "resolved_path": None,
        "exists": False,
        "is_dir": False,
        "file_count": 0,
        "error": None,
    }
    
    try:
        # 如果是相對路徑，需要解析
        if not path.is_absolute() and base_dir:
            resolved = (base_dir / path).resolve()
        else:
            resolved = path.resolve()
        
        result["resolved_path"] = str(resolved)
        result["exists"] = resolved.exists()
        
        if resolved.exists():
            result["is_dir"] = resolved.is_dir()
            if resolved.is_dir():
                try:
                    result["file_count"] = sum(1 for _ in resolved.rglob("*") if _.is_file())
                except:
                    pass
    except Exception as e:
        result["error"] = str(e)
    
    return result

def main():
    """主函數"""
    print("=" * 80)
    print("伺服器無法讀取資料庫及開發模組 - 根本原因分析")
    print("=" * 80)
    print()
    
    # 獲取當前工作目錄（Docker Compose 的基礎目錄）
    current_dir = Path.cwd()
    print(f"當前工作目錄: {current_dir}")
    print()
    
    # 檢查 Docker Compose 配置中的路徑
    print("【Docker Compose 配置中的路徑】")
    print("-" * 80)
    print()
    
    compose_issues = []
    for name, path in DOCKER_COMPOSE_PATHS.items():
        result = check_path(path, current_dir)
        status = "✓" if result["exists"] else "✗"
        print(f"{status} {name}: {result['path']}")
        
        if result["resolved_path"]:
            print(f"   解析後路徑: {result['resolved_path']}")
        
        if result["exists"]:
            print(f"   存在: ✓")
            if result["is_dir"]:
                print(f"   檔案數: {result['file_count']:,} 個")
        else:
            print(f"   存在: ✗")
            compose_issues.append({
                "name": name,
                "path": result["path"],
                "resolved": result["resolved_path"],
            })
        
        if result.get("error"):
            print(f"   錯誤: {result['error']}")
        print()
    
    # 檢查實際檔案位置
    print("【實際檔案位置】")
    print("-" * 80)
    print()
    
    actual_found = []
    for name, path in ACTUAL_PATHS.items():
        result = check_path(path)
        status = "✓" if result["exists"] else "✗"
        print(f"{status} {name}: {result['path']}")
        
        if result["exists"]:
            print(f"   存在: ✓")
            if result["is_dir"]:
                print(f"   檔案數: {result['file_count']:,} 個")
            actual_found.append({
                "name": name,
                "path": result["path"],
                "file_count": result["file_count"],
            })
        else:
            print(f"   存在: ✗")
        print()
    
    # 問題分析
    print("=" * 80)
    print("問題分析")
    print("=" * 80)
    print()
    
    # 1. Odoo 模組路徑問題
    odoo_addons_compose = DOCKER_COMPOSE_PATHS["Odoo 模組"]
    odoo_addons_resolved = (current_dir / odoo_addons_compose).resolve() if not odoo_addons_compose.is_absolute() else odoo_addons_compose.resolve()
    
    print("1. Odoo 模組路徑不匹配：")
    print(f"   Docker Compose 配置: {odoo_addons_compose}")
    print(f"   解析後路徑: {odoo_addons_resolved}")
    print(f"   存在: {'✓' if odoo_addons_resolved.exists() else '✗'}")
    print()
    
    # 找到實際的模組位置
    actual_addons = None
    for item in actual_found:
        if "Odoo 模組" in item["name"]:
            actual_addons = item
            break
    
    if actual_addons:
        print(f"   實際模組位置: {actual_addons['path']}")
        print(f"   檔案數: {actual_addons['file_count']:,} 個")
        print()
        print("   ⚠️  問題：Docker Compose 配置的路徑與實際檔案位置不一致")
        print(f"   → 解決方案：將 Docker Compose 中的路徑改為: {actual_addons['path']}")
    print()
    
    # 2. 資料庫路徑問題
    print("2. 資料庫路徑檢查：")
    db_data = DOCKER_COMPOSE_PATHS["資料庫數據"]
    db_data_result = check_path(db_data)
    print(f"   配置路徑: {db_data}")
    print(f"   存在: {'✓' if db_data_result['exists'] else '✗'}")
    if db_data_result['exists']:
        print(f"   檔案數: {db_data_result['file_count']:,} 個")
        if db_data_result['file_count'] == 0:
            print("   ⚠️  問題：資料庫目錄存在但是空的")
            print("   → 可能原因：資料庫尚未初始化，或資料庫檔案在其他位置")
    print()
    
    # 3. Windows 路徑格式問題
    print("3. Windows 路徑格式問題：")
    print("   Docker Compose 在 Windows 上使用路徑時需要注意：")
    print("   - Windows 路徑使用反斜線: C:\\path\\to\\file")
    print("   - Docker 在 Windows 上可以接受正斜線: C:/path/to/file")
    print("   - 但相對路徑可能會有問題")
    print()
    
    # 建議
    print("=" * 80)
    print("建議解決方案")
    print("=" * 80)
    print()
    
    print("1. 修正 Odoo 模組路徑：")
    if actual_addons:
        print(f"   將 docker-compose.unified.yml 中的：")
        print(f"     - ./wuchang_os/addons:/mnt/extra-addons")
        print(f"   改為：")
        print(f"     - {actual_addons['path']}:/mnt/extra-addons")
    print()
    
    print("2. 檢查資料庫初始化：")
    print("   - 確認資料庫容器是否已啟動")
    print("   - 檢查資料庫是否已初始化")
    print("   - 確認資料庫檔案是否在正確位置")
    print()
    
    print("3. 檢查 Docker 路徑掛載：")
    print("   - 確認 Docker Desktop 可以訪問 Windows 路徑")
    print("   - 檢查 Docker 設定中的 File Sharing 設定")
    print("   - 確認路徑在 Docker 的共享路徑列表中")
    print()
    
    print("4. 檢查符號連結：")
    print("   - 如果使用符號連結，確認 Docker 可以正確解析")
    print("   - 某些 Docker 版本可能不支援符號連結")
    print()
    
    print("=" * 80)

if __name__ == "__main__":
    main()
