#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_developer_container.py

開發者容器設置

功能：
- 設置開發者工作區配置
- 配置開發環境變數
- 建立開發者專用目錄結構
- 配置開發工具和依賴
"""

import sys
import json
import os
import subprocess
from pathlib import Path
from typing import Dict, Any

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def create_developer_config():
    """建立開發者配置檔案"""
    print("【步驟 1：建立開發者配置檔案】")
    
    dev_config = {
        "version": 1,
        "developer": {
            "name": "開發者",
            "workspace_root": str(BASE_DIR),
            "environment": "development",
            "features": {
                "neural_network": True,
                "google_tasks": True,
                "encrypted_storage": True,
                "pii_storage": False,  # 開發環境預設關閉
                "authorization": True,
                "file_sync": True
            }
        },
        "workspace": {
            "local_root": str(BASE_DIR),
            "sync_profiles": ["kb", "rules"],
            "backup_enabled": True,
            "auto_sync": False
        },
        "development": {
            "debug_mode": True,
            "log_level": "DEBUG",
            "test_mode": False,
            "mock_services": False
        },
        "network": {
            "vpn_enabled": True,
            "vpn_network": "10.8.0.0/24",
            "local_network_discovery": True,
            "file_sharing_enabled": True
        },
        "tools": {
            "python_version": sys.version.split()[0],
            "required_packages": [
                "requests",
                "cryptography",
                "google-auth",
                "google-auth-oauthlib",
                "google-api-python-client"
            ]
        }
    }
    
    config_file = BASE_DIR / "developer_container_config.json"
    config_file.write_text(
        json.dumps(dev_config, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    print(f"  ✓ 開發者配置已建立: {config_file}")
    print()
    return dev_config


def setup_developer_directories():
    """建立開發者專用目錄結構"""
    print("【步驟 2：建立開發者目錄結構】")
    
    directories = [
        BASE_DIR / "dev",
        BASE_DIR / "dev" / "logs",
        BASE_DIR / "dev" / "cache",
        BASE_DIR / "dev" / "temp",
        BASE_DIR / "dev" / "backups",
        BASE_DIR / "dev" / "scripts",
        BASE_DIR / "dev" / "tests",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ 已建立: {directory}")
    
    print()


def setup_developer_environment_variables():
    """設置開發者環境變數"""
    print("【步驟 3：設置開發者環境變數】")
    
    env_vars = {
        "WUCHANG_DEV_MODE": "true",
        "WUCHANG_DEBUG": "true",
        "WUCHANG_LOG_LEVEL": "DEBUG",
        "WUCHANG_DEV_WORKSPACE": str(BASE_DIR / "dev"),
        "WUCHANG_DEV_LOGS": str(BASE_DIR / "dev" / "logs"),
        "WUCHANG_DEV_CACHE": str(BASE_DIR / "dev" / "cache"),
    }
    
    # 設定當前會話的環境變數
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"  ✓ {key} = {value}")
    
    # 嘗試永久設定（Windows）
    if sys.platform == "win32":
        try:
            import winreg
            for key, value in env_vars.items():
                try:
                    reg_key = winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER,
                        "Environment",
                        0,
                        winreg.KEY_SET_VALUE
                    )
                    winreg.SetValueEx(reg_key, key, 0, winreg.REG_EXPAND_SZ, value)
                    winreg.CloseKey(reg_key)
                    print(f"  ✓ 已永久設定: {key}")
                except Exception as e:
                    print(f"  ⚠️  永久設定失敗 {key}: {e}")
        except ImportError:
            print("  ⚠️  無法永久設定環境變數（需要 winreg 模組）")
    
    print()


def check_developer_dependencies():
    """檢查開發者依賴"""
    print("【步驟 4：檢查開發者依賴】")
    
    required_packages = [
        "requests",
        "cryptography",
        "google-auth",
        "google-auth-oauthlib",
        "google-api-python-client"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✓ {package} 已安裝")
        except ImportError:
            print(f"  ✗ {package} 未安裝")
            missing_packages.append(package)
    
    if missing_packages:
        print()
        print("  【安裝缺少的套件】")
        print(f"  pip install {' '.join(missing_packages)}")
    else:
        print("  ✓ 所有依賴已安裝")
    
    print()


def setup_developer_tools():
    """設置開發者工具"""
    print("【步驟 5：設置開發者工具】")
    
    # 建立開發者工具腳本目錄
    tools_dir = BASE_DIR / "dev" / "scripts"
    tools_dir.mkdir(parents=True, exist_ok=True)
    
    # 建立快速測試腳本
    test_script = tools_dir / "quick_test.py"
    test_script.write_text("""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
快速測試腳本
\"\"\"
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def test_imports():
    \"\"\"測試模組導入\"\"\"
    print("測試模組導入...")
    try:
        from local_control_center import BASE_DIR as CC_BASE
        print("  ✓ local_control_center 可導入")
    except Exception as e:
        print(f"  ✗ local_control_center 導入失敗: {e}")
    
    try:
        from google_tasks_integration import get_google_tasks_integration
        print("  ✓ google_tasks_integration 可導入")
    except Exception as e:
        print(f"  ✗ google_tasks_integration 導入失敗: {e}")

if __name__ == "__main__":
    test_imports()
""", encoding="utf-8")
    
    print(f"  ✓ 已建立快速測試腳本: {test_script}")
    print()


def generate_developer_readme():
    """生成開發者 README"""
    print("【步驟 6：生成開發者文件】")
    
    readme_content = """# 開發者容器設置

## 開發環境配置

### 環境變數
- `WUCHANG_DEV_MODE`: 開發模式開關
- `WUCHANG_DEBUG`: 除錯模式
- `WUCHANG_LOG_LEVEL`: 日誌級別
- `WUCHANG_DEV_WORKSPACE`: 開發工作區路徑
- `WUCHANG_DEV_LOGS`: 日誌目錄
- `WUCHANG_DEV_CACHE`: 快取目錄

### 目錄結構
```
dev/
├── logs/          # 日誌檔案
├── cache/         # 快取檔案
├── temp/          # 臨時檔案
├── backups/       # 備份檔案
├── scripts/       # 開發腳本
└── tests/         # 測試檔案
```

### 快速測試
```bash
python dev/scripts/quick_test.py
```

### 開發工具
- 快速測試腳本: `dev/scripts/quick_test.py`
- 配置檔案: `developer_container_config.json`

## 注意事項
- 開發環境預設關閉 PII 儲存功能
- 除錯模式會輸出詳細日誌
- 測試模式不會執行實際操作
"""
    
    readme_file = BASE_DIR / "dev" / "README.md"
    readme_file.write_text(readme_content, encoding="utf-8")
    
    print(f"  ✓ 已建立開發者文件: {readme_file}")
    print()


def main():
    """主函數"""
    print("=" * 70)
    print("開發者容器設置")
    print("=" * 70)
    print()
    
    # 建立開發者配置
    config = create_developer_config()
    
    # 建立目錄結構
    setup_developer_directories()
    
    # 設置環境變數
    setup_developer_environment_variables()
    
    # 檢查依賴
    check_developer_dependencies()
    
    # 設置開發工具
    setup_developer_tools()
    
    # 生成文件
    generate_developer_readme()
    
    print("=" * 70)
    print("【完成】")
    print("開發者容器設置已完成")
    print()
    print("【配置摘要】")
    print(f"  工作區根目錄: {BASE_DIR}")
    print(f"  開發目錄: {BASE_DIR / 'dev'}")
    print(f"  配置檔案: {BASE_DIR / 'developer_container_config.json'}")
    print()
    print("【下一步】")
    print("1. 檢查開發者配置: developer_container_config.json")
    print("2. 執行快速測試: python dev/scripts/quick_test.py")
    print("3. 查看開發者文件: dev/README.md")
    print("=" * 70)


if __name__ == "__main__":
    main()
