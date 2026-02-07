#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_three_locations.py

分析「五常雲端空間」、J 碟和 C 碟三個位置的差異
"""

from __future__ import annotations

import sys
import shutil
from pathlib import Path
from typing import Dict, List

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

# 三個位置
C_DRIVE = Path("C:\\")
J_DRIVE = Path("J:\\")
WUCHANG_CLOUD = Path(r"J:\共用雲端硬碟\五常雲端空間")
WUCHANG_LOCAL = Path(r"C:\wuchang V5.1.0\wuchang-V5.1.0")
WUCHANG_CLOUD_PROJECT = Path(r"J:\共用雲端硬碟\五常雲端空間\wuchang-V5.1.0")


def get_drive_info(path: Path) -> Dict:
    """獲取磁碟機資訊"""
    info = {
        "path": str(path),
        "exists": path.exists(),
        "is_symlink": path.is_symlink() if path.exists() else False,
        "total_size": 0,
        "used_size": 0,
        "free_size": 0,
        "type": "unknown",
    }
    
    if not path.exists():
        return info
    
    try:
        # 獲取磁碟使用情況
        total, used, free = shutil.disk_usage(path)
        info["total_size"] = total
        info["used_size"] = used
        info["free_size"] = free
        
        # 判斷類型
        if path == C_DRIVE:
            info["type"] = "本機實體硬碟"
        elif path == J_DRIVE:
            info["type"] = "Google Drive 掛載點（雲端映射）"
        else:
            info["type"] = "目錄"
    except Exception as e:
        info["error"] = str(e)
    
    return info


def get_directory_info(path: Path) -> Dict:
    """獲取目錄資訊"""
    info = {
        "path": str(path),
        "exists": path.exists(),
        "is_symlink": path.is_symlink() if path.exists() else False,
        "file_count": 0,
        "dir_count": 0,
        "total_size": 0,
        "symlink_target": None,
    }
    
    if not path.exists():
        return info
    
    # 檢查是否為符號連結
    if path.is_symlink():
        try:
            info["symlink_target"] = str(path.readlink())
        except:
            info["symlink_target"] = "無法讀取"
    
    # 計算檔案和目錄數量、大小
    try:
        for item in path.rglob("*"):
            if item.is_file():
                info["file_count"] += 1
                try:
                    info["total_size"] += item.stat().st_size
                except:
                    pass
            elif item.is_dir():
                info["dir_count"] += 1
    except Exception as e:
        info["error"] = str(e)
    
    return info


def format_size(size: int) -> str:
    """格式化大小"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def main():
    """主函數"""
    print("=" * 80)
    print("「五常雲端空間」、J 碟和 C 碟差異分析")
    print("=" * 80)
    print()
    
    # 1. 磁碟機層級分析
    print("【1. 磁碟機層級分析】")
    print("-" * 80)
    print()
    
    c_drive_info = get_drive_info(C_DRIVE)
    j_drive_info = get_drive_info(J_DRIVE)
    
    print(f"Windows (C:) 磁碟機")
    print(f"  類型: {c_drive_info['type']}")
    print(f"  總容量: {format_size(c_drive_info['total_size'])}")
    print(f"  已使用: {format_size(c_drive_info['used_size'])}")
    print(f"  剩餘空間: {format_size(c_drive_info['free_size'])}")
    print(f"  使用率: {(c_drive_info['used_size'] / c_drive_info['total_size'] * 100):.1f}%")
    print()
    
    print(f"Google Drive (J:) 磁碟機")
    print(f"  類型: {j_drive_info['type']}")
    print(f"  總容量: {format_size(j_drive_info['total_size'])}")
    print(f"  已使用: {format_size(j_drive_info['used_size'])}")
    print(f"  剩餘空間: {format_size(j_drive_info['free_size'])}")
    print(f"  使用率: {(j_drive_info['used_size'] / j_drive_info['total_size'] * 100):.1f}%")
    print()
    
    # 比較
    print("磁碟機比較：")
    if c_drive_info['total_size'] == j_drive_info['total_size']:
        print(f"  ⚠️  總容量相同: {format_size(c_drive_info['total_size'])}")
        print(f"     這表示 J 碟顯示的是 Google Drive 的配額，不是實體硬碟")
    size_diff = abs(c_drive_info['used_size'] - j_drive_info['used_size'])
    print(f"  已使用空間差異: {format_size(size_diff)}")
    print()
    
    # 2. 目錄層級分析
    print("【2. 目錄層級分析】")
    print("-" * 80)
    print()
    
    print("五常雲端空間（J:\\共用雲端硬碟\\五常雲端空間）")
    cloud_info = get_directory_info(WUCHANG_CLOUD)
    if cloud_info['exists']:
        print(f"  存在: ✓")
        print(f"  檔案數: {cloud_info['file_count']:,} 個")
        print(f"  目錄數: {cloud_info['dir_count']:,} 個")
        print(f"  總大小: {format_size(cloud_info['total_size'])}")
        if cloud_info['is_symlink']:
            print(f"  是符號連結: ✓ -> {cloud_info['symlink_target']}")
    else:
        print(f"  存在: ✗")
    print()
    
    print("C 碟 wuchang 專案（C:\\wuchang V5.1.0\\wuchang-V5.1.0）")
    local_info = get_directory_info(WUCHANG_LOCAL)
    if local_info['exists']:
        print(f"  存在: ✓")
        print(f"  檔案數: {local_info['file_count']:,} 個")
        print(f"  目錄數: {local_info['dir_count']:,} 個")
        print(f"  總大小: {format_size(local_info['total_size'])}")
        if local_info['is_symlink']:
            print(f"  是符號連結: ✓ -> {local_info['symlink_target']}")
    else:
        print(f"  存在: ✗")
    print()
    
    print("雲端 wuchang 專案（J:\\共用雲端硬碟\\五常雲端空間\\wuchang-V5.1.0）")
    cloud_project_info = get_directory_info(WUCHANG_CLOUD_PROJECT)
    if cloud_project_info['exists']:
        print(f"  存在: ✓")
        print(f"  檔案數: {cloud_project_info['file_count']:,} 個")
        print(f"  目錄數: {cloud_project_info['dir_count']:,} 個")
        print(f"  總大小: {format_size(cloud_project_info['total_size'])}")
        if cloud_project_info['is_symlink']:
            print(f"  是符號連結: ✓ -> {cloud_project_info['symlink_target']}")
    else:
        print(f"  存在: ✗")
    print()
    
    # 3. 差異分析
    print("【3. 差異分析】")
    print("-" * 80)
    print()
    
    if local_info['exists'] and cloud_project_info['exists']:
        size_diff = abs(local_info['total_size'] - cloud_project_info['total_size'])
        size_diff_percent = (size_diff / max(local_info['total_size'], cloud_project_info['total_size']) * 100) if max(local_info['total_size'], cloud_project_info['total_size']) > 0 else 0
        
        print("C 碟專案 vs 雲端專案：")
        print(f"  大小差異: {format_size(size_diff)} ({size_diff_percent:.2f}%)")
        print(f"  檔案數差異: {abs(local_info['file_count'] - cloud_project_info['file_count']):,} 個")
        print()
        
        if size_diff_percent < 1:
            print("  ⚠️  大小幾乎相同，這表示：")
            print("     - Google Drive 正在同步 C 碟的內容")
            print("     - 檔案同時存在於 C 碟和雲端")
            print("     - C 碟仍佔用實體空間")
        else:
            print("  ✓ 大小有差異，可能表示：")
            print("     - 同步尚未完成")
            print("     - 或部分檔案未同步")
        print()
    
    # 4. 關係說明
    print("【4. 關係說明】")
    print("-" * 80)
    print()
    print("三個位置的關係：")
    print()
    print("1. Windows (C:) 磁碟機")
    print("   - 本機實體硬碟")
    print("   - 存儲實際檔案資料")
    print("   - 佔用實體儲存空間")
    print()
    print("2. Google Drive (J:) 磁碟機")
    print("   - Google Drive 的本地掛載點")
    print("   - 不是實體硬碟，而是雲端空間的映射")
    print("   - 顯示的容量是 Google Drive 的配額")
    print("   - 檔案實際存儲在 Google 雲端")
    print()
    print("3. 五常雲端空間（J:\\共用雲端硬碟\\五常雲端空間）")
    print("   - 位於 Google Drive (J:) 內的一個資料夾")
    print("   - 是 Google Drive 共享資料夾的一部分")
    print("   - 內容會自動同步到所有連接的設備")
    print()
    print("當前狀態：")
    if local_info['exists'] and cloud_project_info['exists']:
        if not local_info['is_symlink']:
            print("  ⚠️  C 碟專案是實體目錄，佔用 C 碟空間")
            print("  ⚠️  雲端專案是同步副本，也佔用雲端配額")
            print("  → 建議：將 C 碟專案改為符號連結，指向雲端專案")
        else:
            print("  ✓ C 碟專案是符號連結，不佔用 C 碟空間")
    print()
    
    # 5. 建議
    print("【5. 建議】")
    print("-" * 80)
    print()
    if local_info['exists'] and cloud_project_info['exists'] and not local_info['is_symlink']:
        print("若要節省 C 碟空間，可以：")
        print("  1. 使用 create_cloud_symlink.py 將 C 碟專案改為符號連結")
        print("  2. 這樣檔案實際存儲在雲端，C 碟只保留符號連結")
        print("  3. 可節省約 " + format_size(local_info['total_size']) + " 的 C 碟空間")
    else:
        print("當前配置看起來已經優化")
    print()
    
    print("=" * 80)


if __name__ == "__main__":
    main()
