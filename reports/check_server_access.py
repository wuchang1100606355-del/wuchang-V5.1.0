#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_server_access.py

檢查伺服器無法讀取資料庫及開發模組的原因
"""

from __future__ import annotations

import sys
import os
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

# 可能的資料庫和模組位置
POSSIBLE_PATHS = {
    "資料庫": [
        Path(r"C:\wuchang V5.1.0\wuchang-V5.1.0\local_storage\database"),
        Path(r"J:\共用雲端硬碟\五常雲端空間\database"),
        Path(r"C:\wuchang V5.1.0\wuchang-V5.1.0\local_storage\database\backups"),
        Path(r"J:\共用雲端硬碟\五常雲端空間\database\backups"),
    ],
    "Odoo 模組": [
        Path(r"C:\wuchang V5.1.0\wuchang-V5.1.0"),
        Path(r"J:\共用雲端硬碟\五常雲端空間\wuchang-V5.1.0"),
        Path(r"Z:\wuchang_os\addons"),
        Path(r"J:\共用雲端硬碟\五常雲端空間\wuchang_os\addons"),
    ],
}

def check_path(path: Path, description: str) -> dict:
    """檢查路徑"""
    result = {
        "path": str(path),
        "exists": path.exists(),
        "is_symlink": False,
        "is_dir": False,
        "is_file": False,
        "readable": False,
        "writable": False,
        "symlink_target": None,
        "file_count": 0,
        "error": None,
    }
    
    if not path.exists():
        return result
    
    try:
        result["is_symlink"] = path.is_symlink()
        result["is_dir"] = path.is_dir()
        result["is_file"] = path.is_file()
        
        if path.is_symlink():
            try:
                result["symlink_target"] = str(path.readlink())
                result["target_exists"] = path.readlink().exists()
            except Exception as e:
                result["symlink_target"] = f"無法讀取: {e}"
                result["target_exists"] = False
        
        # 檢查權限
        if path.is_dir():
            try:
                test_file = path / ".test_write"
                test_file.touch()
                result["writable"] = True
                test_file.unlink()
            except:
                result["writable"] = False
            
            try:
                list(path.iterdir())
                result["readable"] = True
            except:
                result["readable"] = False
            
            # 計算檔案數
            try:
                result["file_count"] = sum(1 for _ in path.rglob("*") if _.is_file())
            except:
                pass
        elif path.is_file():
            try:
                with open(path, 'rb') as f:
                    f.read(1)
                result["readable"] = True
            except:
                result["readable"] = False
    except Exception as e:
        result["error"] = str(e)
    
    return result

def main():
    """主函數"""
    print("=" * 80)
    print("伺服器無法讀取資料庫及開發模組 - 診斷報告")
    print("=" * 80)
    print()
    
    # 檢查所有可能的路徑
    all_results = {}
    
    for category, paths in POSSIBLE_PATHS.items():
        print(f"【{category}路徑檢查】")
        print("-" * 80)
        print()
        
        category_results = []
        for path in paths:
            result = check_path(path, category)
            category_results.append(result)
            
            status = "✓" if result["exists"] else "✗"
            print(f"{status} {result['path']}")
            
            if result["exists"]:
                print(f"   存在: ✓")
                if result["is_symlink"]:
                    target_status = "✓" if result.get("target_exists") else "✗"
                    print(f"   是符號連結: ✓ -> {result['symlink_target']} ({target_status})")
                print(f"   類型: {'目錄' if result['is_dir'] else '檔案'}")
                print(f"   可讀: {'✓' if result['readable'] else '✗'}")
                if result['is_dir']:
                    print(f"   可寫: {'✓' if result['writable'] else '✗'}")
                    print(f"   檔案數: {result['file_count']:,} 個")
            else:
                print(f"   存在: ✗")
            
            if result.get("error"):
                print(f"   錯誤: {result['error']}")
            print()
        
        all_results[category] = category_results
    
    # 分析問題
    print("=" * 80)
    print("問題分析")
    print("=" * 80)
    print()
    
    # 檢查符號連結問題
    symlink_issues = []
    for category, results in all_results.items():
        for result in results:
            if result["is_symlink"] and not result.get("target_exists"):
                symlink_issues.append({
                    "category": category,
                    "path": result["path"],
                    "target": result["symlink_target"],
                })
    
    if symlink_issues:
        print("⚠️  發現符號連結問題：")
        for issue in symlink_issues:
            print(f"   {issue['category']}: {issue['path']}")
            print(f"      指向: {issue['target']}")
            print(f"      問題: 符號連結指向的目標不存在")
        print()
    
    # 檢查路徑不存在問題
    missing_paths = []
    for category, results in all_results.items():
        for result in results:
            if not result["exists"]:
                missing_paths.append({
                    "category": category,
                    "path": result["path"],
                })
    
    if missing_paths:
        print("⚠️  發現路徑不存在：")
        for missing in missing_paths:
            print(f"   {missing['category']}: {missing['path']}")
        print()
    
    # 檢查權限問題
    permission_issues = []
    for category, results in all_results.items():
        for result in results:
            if result["exists"] and not result["readable"]:
                permission_issues.append({
                    "category": category,
                    "path": result["path"],
                })
    
    if permission_issues:
        print("⚠️  發現權限問題：")
        for issue in permission_issues:
            print(f"   {issue['category']}: {issue['path']}")
            print(f"      問題: 無法讀取")
        print()
    
    # 建議
    print("=" * 80)
    print("建議解決方案")
    print("=" * 80)
    print()
    
    if symlink_issues:
        print("1. 符號連結問題：")
        print("   - 檢查符號連結指向的目標是否存在")
        print("   - 如果目標在雲端，確認 Google Drive 已同步")
        print("   - 考慮重新創建符號連結")
        print()
    
    if missing_paths:
        print("2. 路徑不存在：")
        print("   - 確認檔案是否已遷移到其他位置")
        print("   - 檢查伺服器配置中的路徑設定是否正確")
        print("   - 確認同步是否完成")
        print()
    
    if permission_issues:
        print("3. 權限問題：")
        print("   - 檢查檔案/目錄權限")
        print("   - 確認伺服器執行帳號有讀取權限")
        print("   - 如果是符號連結，確認目標路徑的權限")
        print()
    
    # 檢查伺服器可能期望的路徑
    print("4. 伺服器路徑配置：")
    print("   - 檢查 Docker Compose 配置中的 volume 掛載")
    print("   - 檢查環境變數中的路徑設定")
    print("   - 確認伺服器配置檔案中的路徑是否與實際位置一致")
    print()
    
    print("=" * 80)

if __name__ == "__main__":
    main()
