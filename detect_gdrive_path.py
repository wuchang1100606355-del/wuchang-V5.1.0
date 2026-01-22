#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
detect_gdrive_path.py

自動偵測 Google Drive 路徑（支援 Windows 和 Linux）
"""

import sys
import platform
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass


def detect_gdrive_path():
    """自動偵測 Google Drive 路徑"""
    system = platform.system()
    
    print(f"系統類型: {system}")
    print()
    
    if system == "Windows":
        possible_paths = [
            Path("J:/共用雲端硬碟/五常雲端空間"),
            Path("J:/我的雲端硬碟/五常雲端空間"),
            Path.home() / "Google Drive" / "五常雲端空間",
            Path.home() / "Google 雲端硬碟" / "五常雲端空間",
            Path("G:/Google Drive/五常雲端空間"),
            Path("G:/Google 雲端硬碟/五常雲端空間"),
        ]
    else:  # Linux/Mac
        possible_paths = [
            Path.home() / "Google Drive" / "五常雲端空間",
            Path("/mnt/google-drive/五常雲端空間"),
            Path("/home") / Path.home().name / "Google Drive" / "五常雲端空間",
        ]
    
    print("【搜尋 Google Drive 路徑】")
    print()
    
    found_paths = []
    for path in possible_paths:
        if path.exists():
            found_paths.append(path)
            print(f"  ✓ 找到: {path}")
        else:
            print(f"  ✗ 不存在: {path}")
    
    print()
    
    if found_paths:
        primary_path = found_paths[0]
        print(f"【主要路徑】: {primary_path}")
        print()
        
        # 檢查資料夾結構
        print("【資料夾結構】")
        for subdir in ["containers", "backups", "local_storage"]:
            subpath = primary_path / subdir
            if subpath.exists():
                print(f"  ✓ {subdir}/")
            else:
                print(f"  ✗ {subdir}/ (不存在)")
        
        return primary_path
    else:
        print("⚠️  未找到 Google Drive 路徑")
        print()
        print("請確認：")
        print("  1. Google Drive 已安裝並同步")
        print("  2. 資料夾 '五常雲端空間' 已建立")
        print("  3. 路徑正確")
        return None


def generate_env_file(gdrive_path: Path):
    """產生 .env 檔案"""
    env_content = f"""# Google Drive 路徑配置
# 自動產生，請根據實際路徑調整

GDRIVE_PATH={gdrive_path}
"""
    
    env_file = Path(".env")
    env_file.write_text(env_content, encoding="utf-8")
    
    print(f"【已產生 .env 檔案】")
    print(f"  路徑: {env_file.absolute()}")
    print()
    print("內容：")
    print(env_content)


def main():
    """主函數"""
    print("=" * 70)
    print("Google Drive 路徑自動偵測")
    print("=" * 70)
    print()
    
    gdrive_path = detect_gdrive_path()
    
    if gdrive_path:
        print()
        print("=" * 70)
        print("【建議配置】")
        print("=" * 70)
        print()
        print("在 docker-compose.unified.yml 中使用：")
        print(f"  - {gdrive_path}/containers/data/odoo:/var/lib/odoo")
        print()
        print("或使用環境變數：")
        print(f"  GDRIVE_PATH={gdrive_path}")
        print()
        
        # 詢問是否產生 .env 檔案
        try:
            response = input("是否產生 .env 檔案？(y/n): ").strip().lower()
            if response == 'y':
                generate_env_file(gdrive_path)
        except:
            pass
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
