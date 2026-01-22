#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shared_storage_setup.py

地端檔案共享設置

功能：
- 設置網路共享儲存
- 配置 Docker volumes 使用共享儲存
- 多主機共用檔案系統
- 負載分散配置
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
NETWORK_CONFIG = BASE_DIR / "network_interconnection_config.json"


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    print(f"[{level}] {message}")


def setup_shared_storage():
    """設置共享儲存"""
    print("=" * 70)
    print("地端檔案共享設置")
    print("=" * 70)
    print()
    
    # 載入網路配置
    if NETWORK_CONFIG.exists():
        config = json.loads(NETWORK_CONFIG.read_text(encoding="utf-8"))
        server_share = config.get("server_share", "")
        server_ip = config.get("server_ip", "")
    else:
        server_share = ""
        server_ip = ""
    
    print("【共享儲存選項】")
    print()
    print("1. 網路共享（SMB）")
    print("   - 通過 Windows 網路共享")
    print("   - 路徑: " + (server_share or "未設定"))
    print()
    print("2. Docker Volume（推薦）")
    print("   - 使用 Docker named volumes")
    print("   - 可以跨主機共享")
    print()
    print("3. NFS 共享")
    print("   - 適合 Linux 環境")
    print("   - 高性能檔案共享")
    print()
    
    # 檢查網路共享
    if server_share:
        print("【檢查網路共享】")
        print(f"  共享路徑: {server_share}")
        
        # 測試連接
        try:
            result = subprocess.run(
                ["net", "use", server_share],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=5
            )
            if result.returncode == 0:
                log("網路共享可訪問", "OK")
            else:
                log("網路共享不可訪問，需要映射", "WARN")
        except:
            log("無法測試網路共享", "WARN")
        print()
    
    # Docker Volume 配置
    print("【Docker Volume 配置】")
    print()
    print("可以建立共享的 Docker volumes：")
    print("  - 資料庫資料")
    print("  - 應用程式資料")
    print("  - 上傳檔案")
    print("  - 日誌檔案")
    print()
    print("範例 docker-compose.yml 配置：")
    print("""
volumes:
  shared-data:
    driver: local
    driver_opts:
      type: cifs
      o: username=帳號,password=密碼,file_mode=0777,dir_mode=0777
      device: //伺服器IP/共享路徑
    """)
    print()


def explain_multi_host_benefits():
    """說明多主機優勢"""
    print("=" * 70)
    print("多主機架構優勢")
    print("=" * 70)
    print()
    
    print("【負載分散】")
    print("  ✓ 容器可以分佈在不同主機上")
    print("  ✓ 每台主機只運行部分容器")
    print("  ✓ 降低單一主機的 CPU、記憶體、磁碟負擔")
    print()
    
    print("【資源優化】")
    print("  ✓ 本地主機：運行開發工具、測試容器")
    print("  ✓ 伺服器主機：運行生產服務、資料庫")
    print("  ✓ 根據主機性能分配容器")
    print()
    
    print("【高可用性】")
    print("  ✓ 一台主機故障，其他主機仍可運行")
    print("  ✓ 可以實現容器遷移")
    print("  ✓ 提高系統穩定性")
    print()
    
    print("【擴展性】")
    print("  ✓ 可以輕鬆添加新主機")
    print("  ✓ 動態調整容器分佈")
    print("  ✓ 支援水平擴展")
    print()
    
    print("【當前架構建議】")
    print()
    print("本地主機 (10.8.0.6):")
    print("  - 開發工具容器")
    print("  - 測試環境")
    print("  - 本地服務")
    print()
    print("伺服器主機 (10.8.0.1):")
    print("  - 生產服務容器")
    print("  - 資料庫")
    print("  - Web 服務")
    print()
    print("共享儲存:")
    print("  - 通過網路共享或 Docker volumes")
    print("  - 兩邊都可以訪問相同檔案")
    print()


def create_shared_volume_config():
    """建立共享 Volume 配置"""
    print("【建立共享 Volume 配置】")
    print()
    
    config = {
        "shared_volumes": {
            "data": {
                "type": "named",
                "driver": "local",
                "path": "/shared/data"
            },
            "database": {
                "type": "named",
                "driver": "local",
                "path": "/shared/database"
            },
            "uploads": {
                "type": "named",
                "driver": "local",
                "path": "/shared/uploads"
            }
        },
        "network_share": {
            "enabled": True,
            "path": "\\\\HOME-COMMPUT\\wuchang V5.1.0",
            "mount_point": "Z:",
            "use_for_volumes": True
        }
    }
    
    config_file = BASE_DIR / "shared_storage_config.json"
    config_file.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    log(f"配置已儲存: {config_file}", "OK")
    print()


def main():
    """主函數"""
    setup_shared_storage()
    explain_multi_host_benefits()
    create_shared_volume_config()
    
    print("=" * 70)
    print("【總結】")
    print("=" * 70)
    print()
    print("✓ 可以公用地端檔案（通過網路共享或 Docker volumes）")
    print("✓ 多主機架構可以降低單一伺服器負擔")
    print("✓ 建議使用共享儲存實現檔案共用")
    print("✓ 容器可以分佈在不同主機，實現負載分散")
    print()


if __name__ == "__main__":
    main()
