#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_module_installation.py

模組安裝檢查

功能：
- 檢查 Odoo 模組安裝狀態
- 檢查 Python 套件安裝
- 檢查 Docker 映像檔
- 檢查系統依賴
"""

import sys
import subprocess
import json
import importlib
from pathlib import Path
from typing import Dict, List, Tuple

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
REQUIREMENTS_FILE = BASE_DIR / "requirements.txt"


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌",
        "PROGRESS": "🔄"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")


def check_python_packages():
    """檢查 Python 套件安裝"""
    print("=" * 70)
    print("【檢查 Python 套件安裝】")
    print("=" * 70)
    print()
    
    if not REQUIREMENTS_FILE.exists():
        log("requirements.txt 不存在", "WARN")
        return {}
    
    # 讀取 requirements.txt
    requirements = []
    with open(REQUIREMENTS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # 解析套件名稱（移除版本號）
                package_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].split('!=')[0].strip()
                if package_name:
                    requirements.append(package_name)
    
    results = {}
    missing = []
    installed = []
    
    # 使用 pip list 檢查已安裝的套件
    try:
        pip_result = subprocess.run(
            ["pip", "list", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if pip_result.returncode == 0:
            installed_packages_json = json.loads(pip_result.stdout)
            installed_package_names = {pkg['name'].lower() for pkg in installed_packages_json}
        else:
            installed_package_names = set()
    except:
        installed_package_names = set()
    
    for package in requirements:
        package_lower = package.lower()
        
        # 檢查是否在 pip list 中
        if package_lower in installed_package_names:
            results[package] = True
            installed.append(package)
        else:
            # 嘗試導入套件（備用方法）
            try:
                # 處理套件名稱轉換
                import_name = package.replace('-', '_')
                if import_name == 'python_dateutil':
                    import_name = 'dateutil'
                elif import_name == 'google_api_python_client':
                    import_name = 'googleapiclient'
                elif import_name == 'google_auth':
                    import_name = 'google.auth'
                
                importlib.import_module(import_name)
                results[package] = True
                installed.append(package)
            except ImportError:
                results[package] = False
                missing.append(package)
            except Exception as e:
                results[package] = None
                log(f"{package}: 檢查時發生錯誤 - {e}", "WARN")
    
    # 顯示結果
    if installed:
        log(f"已安裝: {len(installed)} 個套件", "OK")
        for pkg in installed[:10]:  # 只顯示前 10 個
            print(f"  ✓ {pkg}")
        if len(installed) > 10:
            print(f"  ... 還有 {len(installed) - 10} 個")
    
    if missing:
        log(f"未安裝: {len(missing)} 個套件", "WARN")
        for pkg in missing:
            print(f"  ✗ {pkg}")
        print()
        print("安裝方式：")
        print(f"  pip install -r {REQUIREMENTS_FILE.name}")
    
    print()
    return results


def check_docker_images():
    """檢查 Docker 映像檔"""
    print("=" * 70)
    print("【檢查 Docker 映像檔】")
    print("=" * 70)
    print()
    
    required_images = {
        "odoo:17.0": "Odoo ERP 系統",
        "postgres:15": "PostgreSQL 資料庫",
        "cloudflare/cloudflared:latest": "Cloudflare Tunnel",
    }
    
    try:
        result = subprocess.run(
            ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            installed_images = result.stdout.strip().split('\n')
            installed_images = [img for img in installed_images if img]
            
            results = {}
            missing = []
            installed = []
            
            for image, description in required_images.items():
                # 檢查映像檔是否存在（支援版本標籤）
                found = False
                for installed_img in installed_images:
                    if image.split(':')[0] in installed_img:
                        found = True
                        break
                
                if found:
                    results[image] = True
                    installed.append((image, description))
                else:
                    results[image] = False
                    missing.append((image, description))
            
            # 顯示結果
            if installed:
                log(f"已安裝: {len(installed)} 個映像檔", "OK")
                for img, desc in installed:
                    print(f"  ✓ {img} - {desc}")
            
            if missing:
                log(f"未安裝: {len(missing)} 個映像檔", "WARN")
                for img, desc in missing:
                    print(f"  ✗ {img} - {desc}")
                print()
                print("安裝方式：")
                print("  docker pull <映像檔名稱>")
                print("  或使用 docker-compose 自動下載")
            
            print()
            return results
        else:
            log("無法檢查 Docker 映像檔", "ERROR")
            return {}
    
    except Exception as e:
        log(f"檢查 Docker 映像檔時發生錯誤: {e}", "ERROR")
        return {}


def check_odoo_modules():
    """檢查 Odoo 模組"""
    print("=" * 70)
    print("【檢查 Odoo 模組】")
    print("=" * 70)
    print()
    
    # 檢查 Odoo 容器是否運行
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=wuchang-web", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout.strip():
            log("Odoo 容器正在運行", "OK")
            
            # 檢查 Odoo 目錄結構
            odoo_addons_path = BASE_DIR / "wuchang_os" / "addons"
            if odoo_addons_path.exists():
                log(f"Odoo 模組目錄存在: {odoo_addons_path}", "OK")
                
                # 列出模組
                modules = [d.name for d in odoo_addons_path.iterdir() 
                          if d.is_dir() and not d.name.startswith('.')]
                
                if modules:
                    log(f"找到 {len(modules)} 個模組", "OK")
                    for module in modules[:10]:
                        print(f"  ✓ {module}")
                    if len(modules) > 10:
                        print(f"  ... 還有 {len(modules) - 10} 個模組")
                else:
                    log("未找到自訂模組", "INFO")
            else:
                log(f"Odoo 模組目錄不存在: {odoo_addons_path}", "WARN")
            
            # 嘗試檢查 Odoo 模組列表（通過 API 或直接查詢）
            print()
            log("Odoo 模組安裝狀態需要通過 Odoo 介面查看", "INFO")
            print("  訪問: http://localhost:8069")
            print("  前往: 應用程式 > 更新應用程式清單")
            print()
            
            return True
        else:
            log("Odoo 容器未運行", "WARN")
            return False
    
    except Exception as e:
        log(f"檢查 Odoo 模組時發生錯誤: {e}", "ERROR")
        return False


def check_system_dependencies():
    """檢查系統依賴"""
    print("=" * 70)
    print("【檢查系統依賴】")
    print("=" * 70)
    print()
    
    dependencies = {
        "docker": {
            "command": ["docker", "--version"],
            "description": "Docker 容器引擎"
        },
        "python": {
            "command": ["python", "--version"],
            "description": "Python 解釋器"
        },
        "pip": {
            "command": ["pip", "--version"],
            "description": "Python 套件管理器"
        },
    }
    
    results = {}
    
    for name, info in dependencies.items():
        try:
            result = subprocess.run(
                info["command"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                log(f"{name}: {version}", "OK")
                print(f"  {info['description']}")
                results[name] = True
            else:
                log(f"{name}: 未安裝", "ERROR")
                results[name] = False
        except FileNotFoundError:
            log(f"{name}: 未安裝", "ERROR")
            results[name] = False
        except Exception as e:
            log(f"{name}: 檢查錯誤 - {e}", "WARN")
            results[name] = None
    
    print()
    return results


def check_file_structure():
    """檢查檔案結構"""
    print("=" * 70)
    print("【檢查檔案結構】")
    print("=" * 70)
    print()
    
    required_files = {
        "docker-compose.unified.yml": "統一部署配置",
        "docker-compose.cloud.yml": "雲端部署配置",
        "requirements.txt": "Python 套件清單",
        "backup_to_gdrive.py": "備份腳本",
        "cloud_deployment.py": "部署腳本",
    }
    
    required_dirs = {
        "local_storage": "本地儲存",
        "cloudflared": "Cloudflare Tunnel 配置",
        "wuchang_os/addons": "Odoo 模組目錄",
    }
    
    results = {}
    
    # 檢查檔案
    print("【必要檔案】")
    for file_name, description in required_files.items():
        file_path = BASE_DIR / file_name
        if file_path.exists():
            log(f"✓ {file_name} - {description}", "OK")
            results[file_name] = True
        else:
            log(f"✗ {file_name} - {description} (不存在)", "WARN")
            results[file_name] = False
    
    print()
    
    # 檢查目錄
    print("【必要目錄】")
    for dir_name, description in required_dirs.items():
        dir_path = BASE_DIR / dir_name
        if dir_path.exists():
            log(f"✓ {dir_name}/ - {description}", "OK")
            results[dir_name] = True
        else:
            log(f"✗ {dir_name}/ - {description} (不存在)", "WARN")
            results[dir_name] = False
    
    print()
    return results


def generate_report(all_results: Dict):
    """產生檢查報告"""
    print("=" * 70)
    print("【檢查報告】")
    print("=" * 70)
    print()
    
    total_checks = 0
    passed_checks = 0
    failed_checks = 0
    
    for category, results in all_results.items():
        if isinstance(results, dict):
            for item, status in results.items():
                total_checks += 1
                if status is True:
                    passed_checks += 1
                elif status is False:
                    failed_checks += 1
    
    print(f"總檢查項目: {total_checks}")
    print(f"通過: {passed_checks} ✅")
    print(f"失敗: {failed_checks} ❌")
    print(f"未檢查: {total_checks - passed_checks - failed_checks} ⚠️")
    print()
    
    if failed_checks == 0:
        log("所有檢查項目通過！", "OK")
    else:
        log(f"有 {failed_checks} 個檢查項目失敗", "WARN")
        print()
        print("【修復建議】")
        print()
        
        if "python_packages" in all_results:
            missing_packages = [pkg for pkg, status in all_results["python_packages"].items() 
                              if status is False]
            if missing_packages:
                print("1. 安裝缺少的 Python 套件：")
                print(f"   pip install -r requirements.txt")
                print()
        
        if "docker_images" in all_results:
            missing_images = [img for img, status in all_results["docker_images"].items() 
                            if status is False]
            if missing_images:
                print("2. 下載缺少的 Docker 映像檔：")
                for img in missing_images:
                    print(f"   docker pull {img}")
                print()
        
        if "file_structure" in all_results:
            missing_files = [f for f, status in all_results["file_structure"].items() 
                           if status is False]
            if missing_files:
                print("3. 缺少的檔案或目錄：")
                for f in missing_files:
                    print(f"   - {f}")
                print()


def main():
    """主函數"""
    print("=" * 70)
    print("模組安裝檢查")
    print("=" * 70)
    print()
    
    all_results = {}
    
    # 1. 檢查系統依賴
    all_results["system_dependencies"] = check_system_dependencies()
    
    # 2. 檢查 Python 套件
    all_results["python_packages"] = check_python_packages()
    
    # 3. 檢查 Docker 映像檔
    all_results["docker_images"] = check_docker_images()
    
    # 4. 檢查 Odoo 模組
    odoo_status = check_odoo_modules()
    all_results["odoo_modules"] = {"status": odoo_status}
    
    # 5. 檢查檔案結構
    all_results["file_structure"] = check_file_structure()
    
    # 產生報告
    generate_report(all_results)
    
    # 儲存報告
    report_file = BASE_DIR / "module_installation_report.json"
    try:
        import json
        # 轉換結果為可序列化的格式
        serializable_results = {}
        for category, results in all_results.items():
            if isinstance(results, dict):
                serializable_results[category] = {
                    k: bool(v) if v is not None else None 
                    for k, v in results.items()
                }
            else:
                serializable_results[category] = results
        
        report_data = {
            "timestamp": str(datetime.now()),
            "results": serializable_results
        }
        
        report_file.write_text(
            json.dumps(report_data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        log(f"報告已儲存: {report_file}", "OK")
    except Exception as e:
        log(f"儲存報告失敗: {e}", "WARN")
    
    return 0


if __name__ == "__main__":
    from datetime import datetime
    sys.exit(main())
