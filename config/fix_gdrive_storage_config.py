#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_gdrive_storage_config.py

修正 Google Drive 儲存配置，避免版本衝突

功能：
- 將 Google Drive 改為備份用途，而非直接儲存
- 建立本地儲存結構
- 建立備份腳本
- 更新 docker-compose 配置
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    print(f"[{level}] {message}")


def create_local_storage_structure():
    """建立本地儲存結構"""
    print("=" * 70)
    print("建立本地儲存結構")
    print("=" * 70)
    print()
    
    local_storage = BASE_DIR / "local_storage"
    directories = {
        "data": {
            "odoo": "Odoo 資料",
            "other": "其他應用資料"
        },
        "database": {
            "data": "資料庫資料（本地）",
            "backups": "資料庫備份（會同步到 Google Drive）"
        },
        "uploads": "上傳檔案（本地，定期備份到 Google Drive）",
        "logs": "日誌檔案（本地）",
        "config": "配置檔案（可以同步到 Google Drive）"
    }
    
    created_dirs = []
    
    for main_dir, sub_dirs in directories.items():
        if isinstance(sub_dirs, dict):
            main_path = local_storage / main_dir
            main_path.mkdir(parents=True, exist_ok=True)
            created_dirs.append(str(main_path))
            
            for sub_dir, description in sub_dirs.items():
                sub_path = main_path / sub_dir
                sub_path.mkdir(parents=True, exist_ok=True)
                created_dirs.append(str(sub_path))
                print(f"  ✓ {main_dir}/{sub_dir} - {description}")
        else:
            # 單一資料夾
            path = local_storage / main_dir
            path.mkdir(parents=True, exist_ok=True)
            created_dirs.append(str(path))
            print(f"  ✓ {main_dir} - {sub_dirs}")
    
    print()
    log(f"已建立 {len(created_dirs)} 個本地儲存資料夾", "OK")
    print()
    
    return local_storage


def create_safe_docker_compose(local_storage: Path, gdrive_backup: Path):
    """建立安全的 Docker Compose 配置"""
    print("【建立安全的 Docker Compose 配置】")
    print()
    
    # 轉換路徑格式（Windows 路徑）
    local_storage_str = str(local_storage).replace("\\", "/")
    gdrive_backup_str = str(gdrive_backup).replace("\\", "/")
    
    compose_config = f"""# Docker Compose 配置 - 使用本地儲存 + Google Drive 備份
# ⚠️ 重要：資料庫使用本地儲存，避免版本衝突
# Google Drive 只用於備份和只讀共享

version: '3.8'

services:
  wuchang-web:
    image: odoo:17.0
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      # 使用本地儲存（主要儲存）
      - {local_storage_str}/data/odoo:/var/lib/odoo
      - {local_storage_str}/uploads:/var/lib/odoo/filestore
      - {local_storage_str}/logs/odoo:/var/log/odoo
      # Google Drive 作為備份目標（只讀）
      - {gdrive_backup_str}/backups:/backups:ro
      - ./wuchang_os/addons:/mnt/extra-addons
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=odoo
      - POSTGRES_USER=odoo
    volumes:
      # ⚠️ 資料庫必須使用本地儲存，不能使用 Google Drive 同步資料夾
      - {local_storage_str}/database/data:/var/lib/postgresql/data
      # 備份目錄（會定期同步到 Google Drive）
      - {local_storage_str}/database/backups:/backups
    restart: unless-stopped

volumes:
  # 不需要 named volumes，直接使用本地路徑
"""
    
    config_file = BASE_DIR / "docker-compose.safe.yml"
    config_file.write_text(compose_config, encoding="utf-8")
    
    log(f"安全配置已儲存: {config_file}", "OK")
    print()
    print("使用方式：")
    print(f"  docker-compose -f {config_file.name} up -d")
    print()


def create_backup_script(local_storage: Path, gdrive_backup: Path):
    """建立備份腳本"""
    print("【建立備份腳本】")
    print()
    
    backup_script = f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
backup_to_gdrive.py

將本地儲存備份到 Google Drive

使用方式：
  python backup_to_gdrive.py
\"\"\"

import sys
import shutil
from pathlib import Path
from datetime import datetime

LOCAL_STORAGE = Path(r"{local_storage}")
GDRIVE_BACKUP = Path(r"{gdrive_backup}")

def backup_directory(src: Path, dst: Path, name: str):
    \"\"\"備份目錄\"\"\"
    if not src.exists():
        print(f"⚠️  來源不存在: {{src}}")
        return False
    
    dst.mkdir(parents=True, exist_ok=True)
    
    # 建立時間戳記備份
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dst = dst / f"{{name}}_{{timestamp}}"
    
    try:
        if src.is_dir():
            shutil.copytree(src, backup_dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, backup_dst)
        print(f"✓ 已備份 {{name}} 到 {{backup_dst}}")
        return True
    except Exception as e:
        print(f"✗ 備份 {{name}} 失敗: {{e}}")
        return False

def main():
    print("=" * 70)
    print("備份本地儲存到 Google Drive")
    print("=" * 70)
    print()
    
    # 備份資料庫
    backup_directory(
        LOCAL_STORAGE / "database" / "backups",
        GDRIVE_BACKUP / "database" / "backups",
        "database_backups"
    )
    
    # 備份上傳檔案
    backup_directory(
        LOCAL_STORAGE / "uploads",
        GDRIVE_BACKUP / "uploads",
        "uploads"
    )
    
    # 備份配置檔案
    backup_directory(
        LOCAL_STORAGE / "config",
        GDRIVE_BACKUP / "config",
        "config"
    )
    
    print()
    print("備份完成！")

if __name__ == "__main__":
    main()
"""
    
    script_file = BASE_DIR / "backup_to_gdrive.py"
    script_file.write_text(backup_script, encoding="utf-8")
    
    log(f"備份腳本已建立: {script_file}", "OK")
    print()


def create_migration_guide():
    """建立遷移指南"""
    guide = """# 容器遷移指南

## 從本機遷移到伺服器

### 步驟 1：停止本機容器
```bash
docker-compose -f docker-compose.safe.yml down
```

### 步驟 2：備份資料
```bash
python backup_to_gdrive.py
```

### 步驟 3：在伺服器還原
1. 在伺服器安裝 Google Drive 並同步
2. 從 Google Drive 備份還原到伺服器本地儲存
3. 啟動伺服器容器

### 步驟 4：驗證
- 檢查資料是否正確
- 測試服務是否正常

## 從伺服器遷移回本機

反向執行上述步驟即可。
"""
    
    guide_file = BASE_DIR / "CONTAINER_MIGRATION_GUIDE.md"
    guide_file.write_text(guide, encoding="utf-8")
    log(f"遷移指南已建立: {guide_file}", "OK")


def main():
    """主函數"""
    print("=" * 70)
    print("修正 Google Drive 儲存配置")
    print("避免版本衝突問題")
    print("=" * 70)
    print()
    
    # 尋找 Google Drive 備份路徑
    possible_gdrive_paths = [
        Path("J:/共用雲端硬碟/五常雲端空間"),
        Path("J:/我的雲端硬碟/wuchang_containers"),
        Path.home() / "Google Drive" / "wuchang_containers",
        Path.home() / "Google 雲端硬碟" / "wuchang_containers",
    ]
    
    gdrive_backup = None
    for path in possible_gdrive_paths:
        if path.exists():
            gdrive_backup = path
            break
    
    if not gdrive_backup:
        log("未找到 Google Drive 路徑，使用預設路徑", "WARN")
        gdrive_backup = Path("J:/共用雲端硬碟/五常雲端空間")
    
    print(f"Google Drive 備份路徑: {gdrive_backup}")
    print()
    
    # 建立本地儲存
    local_storage = create_local_storage_structure()
    
    # 建立安全配置
    create_safe_docker_compose(local_storage, gdrive_backup)
    
    # 建立備份腳本
    create_backup_script(local_storage, gdrive_backup)
    
    # 建立遷移指南
    create_migration_guide()
    
    print("=" * 70)
    print("【完成】")
    print("=" * 70)
    print()
    print("✓ 已建立本地儲存結構")
    print("✓ 已建立安全的 Docker Compose 配置")
    print("✓ 已建立備份腳本")
    print("✓ 已建立遷移指南")
    print()
    print("【重要提醒】")
    print("1. 資料庫必須使用本地儲存，不能直接使用 Google Drive")
    print("2. Google Drive 只用於備份和只讀共享")
    print("3. 定期執行備份腳本：python backup_to_gdrive.py")
    print("4. 容器遷移時使用備份還原的方式")
    print()
    print("【使用方式】")
    print("  docker-compose -f docker-compose.safe.yml up -d")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
