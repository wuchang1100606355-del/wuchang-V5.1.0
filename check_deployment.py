#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_deployment.py

部署後自動檢查腳本

功能：
- 檢查容器狀態
- 檢查服務連接
- 檢查資料庫健康
- 檢查 Google Drive 儲存
- 檢查外網訪問
"""

import sys
import subprocess
import json
import requests
from pathlib import Path
from typing import Dict, List, Tuple

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
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")


def check_containers() -> Tuple[bool, List[Dict]]:
    """檢查容器狀態"""
    print("=" * 70)
    print("【檢查容器狀態】")
    print("=" * 70)
    print()
    
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            log("無法檢查容器狀態", "ERROR")
            return False, []
        
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    container = json.loads(line)
                    containers.append(container)
                except:
                    pass
        
        wuchang_containers = [
            c for c in containers
            if 'wuchang' in c.get('Names', '').lower()
        ]
        
        all_ok = True
        for container in wuchang_containers:
            name = container.get('Names', '')
            status = container.get('Status', '')
            
            if 'Up' in status:
                log(f"{name}: 運行中", "OK")
            else:
                log(f"{name}: {status}", "ERROR")
                all_ok = False
        
        if not wuchang_containers:
            log("沒有找到五常容器", "WARN")
            all_ok = False
        
        return all_ok, wuchang_containers
    
    except Exception as e:
        log(f"檢查容器時發生錯誤: {e}", "ERROR")
        return False, []


def check_services() -> bool:
    """檢查服務連接"""
    print()
    print("=" * 70)
    print("【檢查服務連接】")
    print("=" * 70)
    print()
    
    services = {
        "Odoo": ("http://localhost:8069", 200),
    }
    
    all_ok = True
    for name, (url, expected_status) in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == expected_status:
                log(f"{name} ({url}): 正常", "OK")
            else:
                log(f"{name} ({url}): 狀態碼 {response.status_code}", "WARN")
                all_ok = False
        except requests.exceptions.ConnectionError:
            log(f"{name} ({url}): 無法連接", "ERROR")
            all_ok = False
        except Exception as e:
            log(f"{name} ({url}): 錯誤 - {e}", "ERROR")
            all_ok = False
    
    return all_ok


def check_database() -> bool:
    """檢查資料庫健康"""
    print()
    print("=" * 70)
    print("【檢查資料庫健康】")
    print("=" * 70)
    print()
    
    try:
        # 檢查資料庫容器
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=wuchang-db", "--format", "{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout.strip():
            status = result.stdout.strip()
            if "Up" in status:
                log(f"資料庫容器: {status}", "OK")
            else:
                log(f"資料庫容器: {status}", "ERROR")
                return False
        else:
            log("資料庫容器未運行", "ERROR")
            return False
        
        # 測試資料庫連接
        result = subprocess.run(
            ["docker", "exec", "wuchang-db", "psql", "-U", "odoo", "-d", "postgres", "-c", "SELECT version();"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            log("資料庫連接: 正常", "OK")
            return True
        else:
            log(f"資料庫連接: 失敗 - {result.stderr}", "ERROR")
            return False
    
    except Exception as e:
        log(f"檢查資料庫時發生錯誤: {e}", "ERROR")
        return False


def check_gdrive_storage() -> bool:
    """檢查 Google Drive 儲存"""
    print()
    print("=" * 70)
    print("【檢查 Google Drive 儲存】")
    print("=" * 70)
    print()
    
    if not GDRIVE_PATH.exists():
        log(f"Google Drive 路徑不存在: {GDRIVE_PATH}", "ERROR")
        return False
    
    log(f"Google Drive 路徑: {GDRIVE_PATH}", "OK")
    
    # 檢查必要的資料夾
    required_dirs = [
        "containers/data/odoo",
        "containers/uploads",
        "containers/logs",
        "containers/config",
        "backups/database",
    ]
    
    all_ok = True
    for dir_path in required_dirs:
        full_path = GDRIVE_PATH / dir_path
        if full_path.exists():
            log(f"  ✓ {dir_path}", "OK")
        else:
            log(f"  ✗ {dir_path} (不存在)", "ERROR")
            all_ok = False
    
    # 測試寫入權限
    try:
        test_file = GDRIVE_PATH / "containers" / "test_write.txt"
        test_file.write_text("test", encoding="utf-8")
        test_file.unlink()
        log("寫入權限: 正常", "OK")
    except Exception as e:
        log(f"寫入權限: 失敗 - {e}", "ERROR")
        all_ok = False
    
    return all_ok


def check_external_access() -> bool:
    """檢查外網訪問"""
    print()
    print("=" * 70)
    print("【檢查外網訪問】")
    print("=" * 70)
    print()
    
    # 檢查 Cloudflare Tunnel
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=cloudflared", "--format", "{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout.strip():
            status = result.stdout.strip()
            if "Up" in status:
                log(f"Cloudflare Tunnel: {status}", "OK")
                
                # 檢查配置檔案
                config_file = BASE_DIR / "cloudflared" / "config.yml"
                credentials_file = BASE_DIR / "cloudflared" / "credentials.json"
                
                if config_file.exists() and credentials_file.exists():
                    log("Cloudflare Tunnel 配置: 存在", "OK")
                    return True
                else:
                    log("Cloudflare Tunnel 配置: 不完整", "WARN")
                    return False
            else:
                log(f"Cloudflare Tunnel: {status}", "WARN")
                return False
        else:
            log("Cloudflare Tunnel: 未運行", "INFO")
            return True  # 不是錯誤，只是未配置
    
    except Exception as e:
        log(f"檢查外網訪問時發生錯誤: {e}", "WARN")
        return True  # 不是錯誤，只是未配置


def generate_report(results: Dict[str, bool]):
    """產生檢查報告"""
    print()
    print("=" * 70)
    print("【檢查報告】")
    print("=" * 70)
    print()
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"總檢查項目: {total}")
    print(f"通過: {passed} ✅")
    print(f"失敗: {failed} ❌")
    print()
    
    if failed == 0:
        log("所有檢查項目通過！", "OK")
    else:
        log(f"有 {failed} 個檢查項目失敗，請檢查上述錯誤", "WARN")
    
    print()
    print("=" * 70)
    print("【建議】")
    print("=" * 70)
    print()
    
    if not results.get("containers", True):
        print("1. 檢查容器狀態，確保所有容器正常運行")
    
    if not results.get("services", True):
        print("2. 檢查服務連接，確認服務可以正常訪問")
    
    if not results.get("database", True):
        print("3. 檢查資料庫健康，確認資料庫可以正常連接")
    
    if not results.get("gdrive", True):
        print("4. 檢查 Google Drive 儲存，確認路徑和權限正確")
    
    if not results.get("external", True):
        print("5. 如需外網訪問，請完成 Cloudflare Tunnel 設定")


def main():
    """主函數"""
    print("=" * 70)
    print("部署後自動檢查")
    print("=" * 70)
    print()
    
    results = {}
    
    # 檢查容器
    containers_ok, containers = check_containers()
    results["containers"] = containers_ok
    
    # 檢查服務
    services_ok = check_services()
    results["services"] = services_ok
    
    # 檢查資料庫
    database_ok = check_database()
    results["database"] = database_ok
    
    # 檢查 Google Drive
    gdrive_ok = check_gdrive_storage()
    results["gdrive"] = gdrive_ok
    
    # 檢查外網訪問
    external_ok = check_external_access()
    results["external"] = external_ok
    
    # 產生報告
    generate_report(results)
    
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
