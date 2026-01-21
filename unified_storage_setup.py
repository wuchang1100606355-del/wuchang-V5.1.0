#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
unified_storage_setup.py

統一儲存設定 - 本機和伺服器共用同一套 Google Drive 儲存

功能：
- 統一使用 Google Drive 作為共享儲存
- 本機和伺服器都使用同一個 Google Drive 路徑
- 自動同步，無需手動複製
- 避免重複配置
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

# 統一的 Google Drive 路徑
UNIFIED_GDRIVE_PATH = Path("J:/共用雲端硬碟/五常雲端空間")


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    print(f"[{level}] {message}")


def create_unified_storage_structure():
    """建立統一的儲存結構"""
    print("=" * 70)
    print("統一儲存設定 - 本機和伺服器共用")
    print("=" * 70)
    print()
    
    print(f"統一 Google Drive 路徑: {UNIFIED_GDRIVE_PATH}")
    print()
    
    if not UNIFIED_GDRIVE_PATH.exists():
        log(f"Google Drive 路徑不存在: {UNIFIED_GDRIVE_PATH}", "ERROR")
        print("請確認 Google Drive 已安裝並同步")
        return False
    
    # 建立統一的資料夾結構
    directories = {
        "containers": {
            "data": {
                "odoo": "Odoo 資料（共享）",
                "other": "其他應用資料（共享）"
            },
            "uploads": "上傳檔案（共享）",
            "logs": "日誌檔案（共享）",
            "config": "配置檔案（共享）"
        },
        "backups": {
            "database": "資料庫備份（共享）",
            "system": "系統備份（共享）",
            "migration": "遷移備份（共享）"
        },
        "local_storage": {
            "data": "本地資料（各主機獨立）",
            "database": {
                "data": "資料庫資料（各主機獨立，不共享）",
                "backups": "資料庫備份（會同步到共享）"
            }
        }
    }
    
    created_dirs = []
    
    def create_dirs(base_path: Path, dirs: Dict, prefix: str = ""):
        for name, content in dirs.items():
            current_path = base_path / name
            current_path.mkdir(parents=True, exist_ok=True)
            created_dirs.append(str(current_path))
            
            if isinstance(content, dict):
                print(f"  ✓ {prefix}{name}/")
                create_dirs(current_path, content, prefix + "  ")
            else:
                print(f"  ✓ {prefix}{name} - {content}")
    
    print("【建立統一儲存結構】")
    print()
    create_dirs(UNIFIED_GDRIVE_PATH, directories)
    
    print()
    log(f"已建立 {len(created_dirs)} 個資料夾", "OK")
    print()
    
    return True


def create_unified_docker_compose():
    """建立統一的 Docker Compose 配置"""
    print("【建立統一 Docker Compose 配置】")
    print()
    
    # 轉換路徑格式
    gdrive_path = str(UNIFIED_GDRIVE_PATH).replace("\\", "/")
    local_storage = str(BASE_DIR / "local_storage").replace("\\", "/")
    
    compose_config = f"""# Docker Compose 配置 - 統一儲存方案
# 本機和伺服器共用同一套 Google Drive 儲存
# ⚠️ 重要：資料庫使用本地儲存，避免版本衝突
# Google Drive 用於共享資料和備份

version: '3.8'

services:
  wuchang-web:
    image: odoo:17.0
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      # 共享資料（Google Drive 自動同步）
      - {gdrive_path}/containers/data/odoo:/var/lib/odoo
      - {gdrive_path}/containers/uploads:/var/lib/odoo/filestore
      - {gdrive_path}/containers/logs/odoo:/var/log/odoo
      - {gdrive_path}/containers/config:/config:ro
      # 本地儲存（各主機獨立）
      - {local_storage}/data/other:/var/lib/other
      - ./wuchang_os/addons:/mnt/extra-addons
    restart: unless-stopped
    environment:
      - GDRIVE_SHARED_PATH={gdrive_path}

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=odoo
      - POSTGRES_USER=odoo
    volumes:
      # ⚠️ 資料庫必須使用本地儲存，不能使用 Google Drive 同步資料夾
      - {local_storage}/database/data:/var/lib/postgresql/data
      # 備份目錄（會定期同步到 Google Drive）
      - {local_storage}/database/backups:/backups
      # 共享備份目錄（只讀）
      - {gdrive_path}/backups/database:/shared_backups:ro
    restart: unless-stopped

volumes:
  # 不需要 named volumes，直接使用路徑
"""
    
    config_file = BASE_DIR / "docker-compose.unified.yml"
    config_file.write_text(compose_config, encoding="utf-8")
    
    log(f"統一配置已儲存: {config_file}", "OK")
    print()
    print("使用方式：")
    print(f"  docker-compose -f {config_file.name} up -d")
    print()


def create_unified_config():
    """建立統一配置檔案"""
    print("【建立統一配置檔案】")
    print()
    
    config = {
        "unified_storage": {
            "enabled": True,
            "type": "google_drive",
            "path": str(UNIFIED_GDRIVE_PATH),
            "description": "本機和伺服器共用同一套 Google Drive 儲存"
        },
        "shared_paths": {
            "containers": str(UNIFIED_GDRIVE_PATH / "containers"),
            "backups": str(UNIFIED_GDRIVE_PATH / "backups"),
            "config": str(UNIFIED_GDRIVE_PATH / "containers" / "config")
        },
        "local_paths": {
            "database_data": str(BASE_DIR / "local_storage" / "database" / "data"),
            "database_backups": str(BASE_DIR / "local_storage" / "database" / "backups")
        },
        "hosts": {
            "local": {
                "name": "LUNGSMSI",
                "ip": "10.8.0.6",
                "gdrive_path": str(UNIFIED_GDRIVE_PATH)
            },
            "server": {
                "name": "HOME-COMMPUT",
                "ip": "10.8.0.1",
                "gdrive_path": "需要伺服器也安裝 Google Drive 並同步到相同路徑"
            }
        },
        "notes": [
            "本機和伺服器都使用同一個 Google Drive 路徑",
            "Google Drive 會自動同步，無需手動複製",
            "資料庫使用本地儲存，避免版本衝突",
            "共享資料（上傳檔案、配置）會自動同步",
            "備份會自動同步到 Google Drive"
        ]
    }
    
    config_file = BASE_DIR / "unified_storage_config.json"
    config_file.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    log(f"統一配置已儲存: {config_file}", "OK")
    print()


def explain_unified_benefits():
    """說明統一儲存的優勢"""
    print("=" * 70)
    print("統一儲存優勢")
    print("=" * 70)
    print()
    
    print("【一套配置，兩邊共用】")
    print("  ✓ 本機和伺服器使用同一個 Google Drive 路徑")
    print("  ✓ 不需要維護兩套配置")
    print("  ✓ 自動同步，無需手動複製")
    print()
    
    print("【自動同步】")
    print("  ✓ 本機修改 → Google Drive 自動同步 → 伺服器自動更新")
    print("  ✓ 伺服器修改 → Google Drive 自動同步 → 本機自動更新")
    print("  ✓ 無需手動操作")
    print()
    
    print("【資料一致性】")
    print("  ✓ 上傳檔案：兩邊都可以看到")
    print("  ✓ 配置檔案：兩邊都使用相同配置")
    print("  ✓ 備份檔案：統一管理")
    print()
    
    print("【安全設計】")
    print("  ✓ 資料庫使用本地儲存，避免版本衝突")
    print("  ✓ 共享資料自動同步")
    print("  ✓ 備份自動同步到 Google Drive")
    print()
    
    print("【使用場景】")
    print("  1. 本機開發 → 資料在 Google Drive → 伺服器自動同步")
    print("  2. 伺服器運行 → 資料在 Google Drive → 本機自動同步")
    print("  3. 本機關機 → 伺服器繼續運行（使用本地資料庫）")
    print("  4. 伺服器關機 → 本機繼續運行（使用本地資料庫）")
    print()


def main():
    """主函數"""
    print("=" * 70)
    print("統一儲存設定")
    print("本機和伺服器共用同一套 Google Drive 儲存")
    print("=" * 70)
    print()
    
    # 建立統一儲存結構
    if not create_unified_storage_structure():
        return 1
    
    # 建立統一 Docker Compose 配置
    create_unified_docker_compose()
    
    # 建立統一配置檔案
    create_unified_config()
    
    # 說明優勢
    explain_unified_benefits()
    
    print("=" * 70)
    print("【完成】")
    print("=" * 70)
    print()
    print("✓ 已建立統一儲存結構")
    print("✓ 已建立統一 Docker Compose 配置")
    print("✓ 已建立統一配置檔案")
    print()
    print("【重要說明】")
    print("1. 本機和伺服器都使用同一個 Google Drive 路徑")
    print("2. 伺服器也需要安裝 Google Drive 並同步到相同路徑")
    print("3. 資料庫使用本地儲存，避免版本衝突")
    print("4. 共享資料（上傳檔案、配置）會自動同步")
    print()
    print("【伺服器設定】")
    print("在伺服器上執行相同設定，確保 Google Drive 路徑一致")
    print("或使用網路共享讓伺服器訪問本機的 Google Drive")
    print()
    print("【使用方式】")
    print("  docker-compose -f docker-compose.unified.yml up -d")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
