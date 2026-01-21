#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diagnose_network_share.py

診斷網路共享連接問題

功能：
- 檢查網路磁碟機狀態
- 測試共享路徑訪問
- 提供診斷資訊和解決方案
"""

import sys
import subprocess
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def check_network_drive(drive_letter: str = "Z:"):
    """檢查網路磁碟機狀態"""
    print(f"【檢查 {drive_letter} 磁碟機】")
    
    # 檢查 net use 輸出
    try:
        result = subprocess.run(
            ["net", "use"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if drive_letter in result.stdout:
            print(f"  ✓ {drive_letter} 已映射")
            # 提取映射資訊
            for line in result.stdout.split('\n'):
                if drive_letter in line:
                    print(f"    映射資訊: {line.strip()}")
        else:
            print(f"  ✗ {drive_letter} 未映射")
    except Exception as e:
        print(f"  ✗ 檢查失敗: {e}")
    
    print()
    
    # 檢查路徑可訪問性
    drive_path = Path(f"{drive_letter}\\")
    print(f"【檢查路徑可訪問性】")
    print(f"  路徑: {drive_path}")
    
    try:
        exists = drive_path.exists()
        print(f"  exists(): {exists}")
        
        if exists:
            is_dir = drive_path.is_dir()
            print(f"  is_dir(): {is_dir}")
            
            if is_dir:
                try:
                    items = list(drive_path.iterdir())
                    print(f"  ✓ 內容可見，共 {len(items)} 個項目")
                    print()
                    print("  【內容列表】（前 10 項）")
                    for i, item in enumerate(items[:10], 1):
                        item_type = "目錄" if item.is_dir() else "檔案"
                        print(f"    {i:2d}. [{item_type}] {item.name}")
                    return True
                except PermissionError:
                    print(f"  ✗ 權限不足，無法列出內容")
                    return False
                except Exception as e:
                    print(f"  ✗ 無法列出內容: {e}")
                    return False
            else:
                print(f"  ✗ 路徑不是目錄")
                return False
        else:
            print(f"  ✗ 路徑不存在或不可訪問")
            return False
    except Exception as e:
        print(f"  ✗ 檢查失敗: {e}")
        return False


def test_network_paths():
    """測試各種網路路徑"""
    print("【測試網路路徑】")
    
    test_paths = [
        "\\\\HOME-COMMPUT\\wuchang V5.1.0",
        "\\\\HOME-COMPUTER\\wuchang V5.1.0",
        "\\\\HOME-COMPUT\\wuchang V5.1.0",
        "\\\\HOME-COMMPUT\\wuchang",
        "\\\\10.8.0.1\\wuchang",
        "\\\\10.8.0.1\\share",
        "Z:\\",
    ]
    
    accessible_paths = []
    for path_str in test_paths:
        try:
            path = Path(path_str)
            if path.exists():
                print(f"  ✓ 可訪問: {path_str}")
                accessible_paths.append(path_str)
                try:
                    items = list(path.iterdir())
                    print(f"     內容: {len(items)} 個項目")
                except:
                    print(f"     內容: 無法列出")
            else:
                print(f"  ✗ 不可訪問: {path_str}")
        except Exception as e:
            print(f"  ✗ 錯誤: {path_str} - {e}")
    
    print()
    return accessible_paths


def provide_solutions():
    """提供解決方案"""
    print("=" * 70)
    print("【診斷與解決方案】")
    print("=" * 70)
    print()
    
    print("如果 Z: 磁碟機已映射但內容不可見，可能原因：")
    print()
    print("1. 網路連接中斷")
    print("   解決方案：")
    print("   - 檢查網路連接")
    print("   - ping HOME-COMMPUT")
    print("   - 確認 VPN 連接正常")
    print()
    
    print("2. 共享路徑名稱錯誤")
    print("   解決方案：")
    print("   - 檢查正確的電腦名稱（COMMPUT vs COMPUTER）")
    print("   - 使用 net view 掃描網路")
    print("   - 確認共享名稱")
    print()
    
    print("3. 需要認證")
    print("   解決方案：")
    print("   - 重新映射並提供認證資訊：")
    print("     net use Z: /delete")
    print("     net use Z: \\\\正確路徑 /user:用戶名 密碼 /persistent:yes")
    print()
    
    print("4. 共享伺服器未運行")
    print("   解決方案：")
    print("   - 確認共享伺服器正在運行")
    print("   - 檢查共享服務狀態")
    print()
    
    print("5. 防火牆阻擋")
    print("   解決方案：")
    print("   - 檢查防火牆設定")
    print("   - 確認 SMB 端口（445）開放")
    print()


def main():
    """主函數"""
    print("=" * 70)
    print("網路共享診斷工具")
    print("=" * 70)
    print()
    
    # 檢查 Z: 磁碟機
    z_accessible = check_network_drive("Z:")
    
    # 測試其他路徑
    accessible_paths = test_network_paths()
    
    # 提供解決方案
    provide_solutions()
    
    # 總結
    print("=" * 70)
    print("【總結】")
    print("=" * 70)
    
    if z_accessible:
        print("✓ Z: 磁碟機內容可見")
        print("  可以執行檔案同步")
    elif accessible_paths:
        print(f"⚠️  Z: 不可訪問，但找到其他可訪問路徑：")
        for path in accessible_paths:
            print(f"  - {path}")
        print("  建議更新 WUCHANG_COPY_TO 環境變數")
    else:
        print("✗ 所有測試路徑均不可訪問")
        print("  需要確認網路連接和共享設定")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
