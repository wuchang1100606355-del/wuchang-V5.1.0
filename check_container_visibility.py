#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_container_visibility.py

檢查容器內容是否可見

功能：
- 檢查網路共享路徑內容
- 檢查映射磁碟機內容
- 列出可見的檔案和目錄
"""

import sys
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def check_path_visibility(path_str: str, label: str = ""):
    """檢查路徑內容是否可見"""
    print(f"【檢查 {label}】")
    print(f"  路徑: {path_str}")
    
    try:
        path = Path(path_str)
        
        if not path.exists():
            print(f"  ✗ 路徑不存在或不可訪問")
            return False
        
        print(f"  ✓ 路徑可訪問")
        
        # 嘗試列出內容
        try:
            items = list(path.iterdir())
            print(f"  ✓ 內容可見，共 {len(items)} 個項目")
            print()
            print("  【內容列表】（前 20 項）")
            for i, item in enumerate(items[:20], 1):
                item_type = "目錄" if item.is_dir() else "檔案"
                size = ""
                if item.is_file():
                    try:
                        size = f" ({item.stat().st_size / 1024:.1f} KB)"
                    except:
                        size = ""
                print(f"    {i:2d}. [{item_type}] {item.name}{size}")
            
            if len(items) > 20:
                print(f"    ... 還有 {len(items) - 20} 個項目")
            
            return True
        except PermissionError:
            print(f"  ✗ 權限不足，無法列出內容")
            return False
        except Exception as e:
            print(f"  ✗ 無法列出內容: {e}")
            return False
            
    except Exception as e:
        print(f"  ✗ 檢查失敗: {e}")
        return False


def main():
    """主函數"""
    print("=" * 70)
    print("檢查容器內容可見性")
    print("=" * 70)
    print()
    
    # 讀取配置
    config_file = BASE_DIR / "network_interconnection_config.json"
    network_path = None
    if config_file.exists():
        try:
            import json
            config = json.loads(config_file.read_text(encoding="utf-8"))
            network_path = config.get("server_share", "")
        except:
            pass
    
    # 檢查網路共享路徑
    if network_path:
        check_path_visibility(network_path, "網路共享路徑")
        print()
    
    # 檢查 Z: 磁碟機
    check_path_visibility("Z:\\", "Z: 磁碟機")
    print()
    
    # 檢查其他可能的路徑
    alternative_paths = [
        "\\\\HOME-COMMPUT\\wuchang V5.1.0",
        "\\\\HOME-COMPUTER\\wuchang V5.1.0",
        "\\\\HOME-COMPUT\\wuchang V5.1.0",
        "\\\\10.8.0.1\\wuchang",
        "\\\\10.8.0.1\\share",
    ]
    
    print("【檢查替代路徑】")
    found_accessible = False
    for alt_path in alternative_paths:
        try:
            if Path(alt_path).exists():
                print(f"  ✓ 找到可訪問路徑: {alt_path}")
                check_path_visibility(alt_path, f"替代路徑: {alt_path}")
                found_accessible = True
                break
        except:
            continue
    
    if not found_accessible:
        print("  ✗ 未找到可訪問的替代路徑")
    
    print()
    print("=" * 70)
    print("【總結】")
    
    # 檢查環境變數
    import os
    copy_to = os.getenv("WUCHANG_COPY_TO", "")
    if copy_to:
        print(f"環境變數 WUCHANG_COPY_TO: {copy_to}")
        if Path(copy_to).exists():
            print("  ✓ 環境變數指向的路徑可訪問")
        else:
            print("  ✗ 環境變數指向的路徑不可訪問")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
