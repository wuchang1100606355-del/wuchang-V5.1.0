#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
initialize_cloud_storage.py

初始化雲端儲存 - 建立必要的配置檔案和說明文件
"""

import sys
from pathlib import Path
from datetime import datetime

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
GDRIVE_PATH = Path("J:/共用雲端硬碟/五常雲端空間")


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    print(f"[{level}] {message}")


def create_readme_files():
    """建立說明檔案"""
    print("=" * 70)
    print("初始化雲端儲存")
    print("=" * 70)
    print()
    
    # 建立 README 檔案
    readme_content = f"""# 五常雲端空間

這是五常系統的統一雲端儲存空間，用於本機和伺服器共享資料。

## 📁 資料夾結構

### containers/ - 容器共享資料
- `data/odoo/` - Odoo ERP 系統資料（共享）
- `data/other/` - 其他應用資料（共享）
- `uploads/` - 上傳檔案（共享）
- `logs/` - 日誌檔案（共享）
- `config/` - 配置檔案（共享）

### backups/ - 備份檔案
- `database/` - 資料庫備份（共享）
- `system/` - 系統備份（共享）
- `migration/` - 遷移備份（共享）

### local_storage/ - 本地儲存（各主機獨立）
- `data/` - 本地資料
- `database/data/` - 資料庫資料（各主機獨立，不共享）
- `database/backups/` - 資料庫備份（會同步到共享）

## 🔄 同步說明

- **共享資料**：本機和伺服器自動同步
- **本地資料**：各主機獨立，不會同步
- **備份檔案**：自動同步到 Google Drive

## 📝 使用方式

1. 容器運行後，資料會自動儲存到對應資料夾
2. 備份會自動同步到 `backups/` 資料夾
3. 配置檔案放在 `containers/config/` 會自動同步

建立時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    readme_file = GDRIVE_PATH / "README.md"
    readme_file.write_text(readme_content, encoding="utf-8")
    log(f"已建立 README: {readme_file}", "OK")
    
    # 建立 .gitkeep 檔案（保持空資料夾）
    gitkeep_dirs = [
        "containers/data/odoo",
        "containers/data/other",
        "containers/uploads",
        "containers/logs",
        "containers/config",
        "backups/database",
        "backups/system",
        "backups/migration",
    ]
    
    created_keeps = []
    for dir_path in gitkeep_dirs:
        keep_file = GDRIVE_PATH / dir_path / ".gitkeep"
        keep_file.parent.mkdir(parents=True, exist_ok=True)
        keep_file.write_text("# 此資料夾用於儲存容器資料\n", encoding="utf-8")
        created_keeps.append(keep_file)
    
    log(f"已建立 {len(created_keeps)} 個 .gitkeep 檔案", "OK")
    print()


def create_example_configs():
    """建立範例配置檔案"""
    print("【建立範例配置檔案】")
    print()
    
    config_dir = GDRIVE_PATH / "containers" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # 範例配置檔案
    example_config = """# 容器配置範例
# 此檔案會自動同步到本機和伺服器

# Odoo 配置
ODOO_VERSION=17.0
ODOO_PORT=8069

# 資料庫配置
DB_HOST=db
DB_PORT=5432
DB_NAME=postgres
DB_USER=odoo

# 儲存路徑
STORAGE_PATH=J:/共用雲端硬碟/五常雲端空間

建立時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    config_file = config_dir / "example.env"
    config_file.write_text(example_config, encoding="utf-8")
    log(f"已建立範例配置: {config_file}", "OK")
    print()


def check_existing_data():
    """檢查是否有現有資料需要遷移"""
    print("【檢查現有資料】")
    print()
    
    # 檢查本地儲存是否有資料
    local_storage = BASE_DIR / "local_storage"
    if local_storage.exists():
        data_dirs = [
            "data/odoo",
            "uploads",
            "database/backups",
        ]
        
        found_data = []
        for dir_path in data_dirs:
            full_path = local_storage / dir_path
            if full_path.exists():
                items = list(full_path.iterdir())
                if items:
                    found_data.append((dir_path, len(items)))
        
        if found_data:
            print("發現現有資料：")
            for dir_path, count in found_data:
                print(f"  - {dir_path}: {count} 個項目")
            print()
            print("建議：執行備份腳本將資料遷移到 Google Drive")
            print("  python backup_to_gdrive.py")
        else:
            print("  ✓ 目前沒有現有資料需要遷移")
    else:
        print("  ✓ 本地儲存資料夾尚未建立")
    
    print()


def explain_why_empty():
    """說明為什麼資料夾是空的"""
    print("=" * 70)
    print("為什麼資料夾是空的？")
    print("=" * 70)
    print()
    
    print("【這是正常的】")
    print("  ✓ 資料夾結構剛建立，還沒有資料")
    print("  ✓ 容器還沒有運行，所以沒有產生資料")
    print("  ✓ 還沒有進行備份")
    print()
    
    print("【什麼時候會有檔案？】")
    print()
    print("1. 容器運行後：")
    print("   - 啟動容器: docker-compose -f docker-compose.unified.yml up -d")
    print("   - Odoo 資料會儲存到: containers/data/odoo/")
    print("   - 上傳檔案會儲存到: containers/uploads/")
    print()
    
    print("2. 執行備份後：")
    print("   - 執行備份: python backup_to_gdrive.py")
    print("   - 備份檔案會儲存到: backups/database/")
    print()
    
    print("3. 手動上傳檔案：")
    print("   - 將檔案放到對應資料夾")
    print("   - Google Drive 會自動同步")
    print()
    
    print("【資料夾結構已建立】")
    print("  ✓ 所有必要的資料夾都已建立")
    print("  ✓ 容器運行後會自動使用這些資料夾")
    print("  ✓ 資料會自動同步到 Google Drive")
    print()


def main():
    """主函數"""
    if not GDRIVE_PATH.exists():
        log(f"Google Drive 路徑不存在: {GDRIVE_PATH}", "ERROR")
        return 1
    
    # 建立說明檔案
    create_readme_files()
    
    # 建立範例配置
    create_example_configs()
    
    # 檢查現有資料
    check_existing_data()
    
    # 說明為什麼是空的
    explain_why_empty()
    
    print("=" * 70)
    print("【完成】")
    print("=" * 70)
    print()
    print("✓ 已建立說明檔案")
    print("✓ 已建立範例配置")
    print("✓ 已檢查現有資料")
    print()
    print("【下一步】")
    print("1. 啟動容器: docker-compose -f docker-compose.unified.yml up -d")
    print("2. 容器運行後，資料會自動儲存到 Google Drive")
    print("3. 執行備份: python backup_to_gdrive.py")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
