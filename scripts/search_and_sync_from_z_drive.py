#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
search_and_sync_from_z_drive.py

從 Z_drive 搜尋並同步必要檔案

功能：
- 搜尋 Z_drive 中的必要檔案
- 比對系統需求
- 同步檔案到系統目錄
- 記錄操作日誌
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
Z_DRIVE = Path("Z:/")

# 匯入工作日誌管理器
sys.path.insert(0, str(BASE_DIR / "scripts"))
try:
    from work_log_manager import WorkLogManager
    log_manager = WorkLogManager()
except ImportError:
    log_manager = None

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

def check_z_drive():
    """檢查 Z_drive 是否存在"""
    if not Z_DRIVE.exists():
        log("Z_drive 不存在", "ERROR")
        return False
    
    log(f"✓ Z_drive 存在: {Z_DRIVE}", "OK")
    return True

def search_necessary_files() -> Dict[str, List[Path]]:
    """搜尋必要檔案"""
    log("搜尋 Z_drive 中的必要檔案...", "PROGRESS")
    
    necessary_files = {
        "credentials": [],
        "configs": [],
        "scripts": [],
        "modules": [],
        "docker": [],
        "documentation": []
    }
    
    if not Z_DRIVE.exists():
        return necessary_files
    
    # 搜尋憑證檔案
    credential_patterns = [
        "*credentials*.json",
        "*token*.json",
        "*credential*.json",
        "*google*.json",
        "*sa*.json",  # service account
        "*.pem",
        "*.key"
    ]
    
    # 搜尋配置檔案
    config_patterns = [
        "*.env",
        "*config*.yml",
        "*config*.yaml",
        "*config*.json",
        "*docker-compose*.yml",
        "*docker-compose*.yaml"
    ]
    
    # 搜尋腳本檔案
    script_patterns = [
        "*.py",
        "*.ps1",
        "*.sh",
        "*.bat"
    ]
    
    # 搜尋 Odoo 模組
    module_patterns = [
        "*__manifest__.py",
        "*addons*"
    ]
    
    # 搜尋 Docker 相關
    docker_patterns = [
        "*Dockerfile*",
        "*docker-compose*"
    ]
    
    try:
        # 搜尋憑證檔案
        for pattern in credential_patterns:
            for file_path in Z_DRIVE.rglob(pattern):
                if file_path.is_file():
                    necessary_files["credentials"].append(file_path)
        
        # 搜尋配置檔案
        for pattern in config_patterns:
            for file_path in Z_DRIVE.rglob(pattern):
                if file_path.is_file():
                    necessary_files["configs"].append(file_path)
        
        # 搜尋腳本檔案
        for pattern in script_patterns:
            for file_path in Z_DRIVE.rglob(pattern):
                if file_path.is_file():
                    necessary_files["scripts"].append(file_path)
        
        # 搜尋 Odoo 模組
        for pattern in module_patterns:
            for file_path in Z_DRIVE.rglob(pattern):
                if file_path.is_file():
                    necessary_files["modules"].append(file_path)
        
        # 搜尋 Docker 檔案
        for pattern in docker_patterns:
            for file_path in Z_DRIVE.rglob(pattern):
                if file_path.is_file():
                    necessary_files["docker"].append(file_path)
        
    except Exception as e:
        log(f"搜尋檔案時發生錯誤: {e}", "ERROR")
    
    return necessary_files

def sync_file(source: Path, target: Path, category: str) -> bool:
    """同步檔案"""
    try:
        # 確保目標目錄存在
        target.parent.mkdir(parents=True, exist_ok=True)
        
        # 如果目標檔案已存在，先備份
        if target.exists():
            backup_path = target.with_suffix(f"{target.suffix}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            shutil.copy2(target, backup_path)
            log(f"  備份現有檔案: {backup_path.name}", "INFO")
        
        # 複製檔案
        shutil.copy2(source, target)
        log(f"  ✓ 已同步: {source.name} -> {target.relative_to(BASE_DIR)}", "OK")
        return True
    except Exception as e:
        log(f"  ✗ 同步失敗: {source.name} - {e}", "ERROR")
        return False

def sync_necessary_files(found_files: Dict[str, List[Path]]) -> Dict[str, int]:
    """同步必要檔案到系統目錄"""
    log("同步必要檔案到系統目錄...", "PROGRESS")
    
    sync_results = {
        "credentials": 0,
        "configs": 0,
        "scripts": 0,
        "modules": 0,
        "docker": 0
    }
    
    # 同步憑證檔案
    if found_files["credentials"]:
        log("同步憑證檔案...", "INFO")
        for source_file in found_files["credentials"]:
            # 根據檔案類型決定目標位置
            if "google" in source_file.name.lower() or "credentials" in source_file.name.lower():
                target = BASE_DIR / source_file.name
            elif "sa" in source_file.name.lower() or "service" in source_file.name.lower():
                target = BASE_DIR / "config" / "gcp" / source_file.name
            else:
                target = BASE_DIR / "config" / source_file.name
            
            if sync_file(source_file, target, "credentials"):
                sync_results["credentials"] += 1
    
    # 同步配置檔案
    if found_files["configs"]:
        log("同步配置檔案...", "INFO")
        for source_file in found_files["configs"]:
            if "docker-compose" in source_file.name.lower():
                target = BASE_DIR / source_file.name
            elif "cloudflared" in source_file.name.lower() or "cloudflare" in source_file.name.lower():
                target = BASE_DIR / "cloudflared" / source_file.name
            elif source_file.name.endswith(".env"):
                target = BASE_DIR / source_file.name
            else:
                target = BASE_DIR / "config" / source_file.name
            
            if sync_file(source_file, target, "configs"):
                sync_results["configs"] += 1
    
    # 同步腳本檔案
    if found_files["scripts"]:
        log("同步腳本檔案...", "INFO")
        for source_file in found_files["scripts"]:
            target = BASE_DIR / "scripts" / source_file.name
            if sync_file(source_file, target, "scripts"):
                sync_results["scripts"] += 1
    
    # 同步 Odoo 模組
    if found_files["modules"]:
        log("同步 Odoo 模組...", "INFO")
        for source_file in found_files["modules"]:
            # 嘗試找到模組根目錄
            module_root = source_file.parent
            while module_root.name != "addons" and module_root != Z_DRIVE:
                module_root = module_root.parent
            
            if module_root.name == "addons":
                module_name = source_file.parent.name if "__manifest__.py" in source_file.name else source_file.parent.parent.name
                relative_path = source_file.relative_to(module_root.parent)
                target = BASE_DIR / "wuchang_os" / "addons" / relative_path
                
                if sync_file(source_file, target, "modules"):
                    sync_results["modules"] += 1
    
    # 同步 Docker 檔案
    if found_files["docker"]:
        log("同步 Docker 檔案...", "INFO")
        for source_file in found_files["docker"]:
            target = BASE_DIR / source_file.name
            if sync_file(source_file, target, "docker"):
                sync_results["docker"] += 1
    
    return sync_results

def generate_sync_report(found_files: Dict[str, List[Path]], sync_results: Dict[str, int]) -> str:
    """產生同步報告"""
    report_lines = [
        "# Z_drive 必要檔案搜尋與同步報告",
        "",
        f"**執行時間：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 📁 搜尋結果",
        "",
    ]
    
    total_found = sum(len(files) for files in found_files.values())
    report_lines.append(f"**總計找到：** {total_found} 個檔案")
    report_lines.append("")
    
    for category, files in found_files.items():
        if files:
            report_lines.append(f"### {category} ({len(files)} 個)")
            for file_path in files[:10]:  # 顯示前10個
                report_lines.append(f"- `{file_path.relative_to(Z_DRIVE)}`")
            if len(files) > 10:
                report_lines.append(f"- ... 還有 {len(files) - 10} 個檔案")
            report_lines.append("")
    
    report_lines.extend([
        "## 📊 同步結果",
        "",
        "### 同步統計",
        "",
        f"- **憑證檔案：** {sync_results['credentials']} 個",
        f"- **配置檔案：** {sync_results['configs']} 個",
        f"- **腳本檔案：** {sync_results['scripts']} 個",
        f"- **Odoo 模組：** {sync_results['modules']} 個",
        f"- **Docker 檔案：** {sync_results['docker']} 個",
        "",
        "## 📝 注意事項",
        "",
        "1. 已同步的檔案會覆蓋現有檔案（自動備份原檔案）",
        "2. 憑證檔案請檢查權限設定",
        "3. 配置檔案請確認路徑和環境變數",
        "4. Odoo 模組需要更新應用程式清單後才能使用",
    ])
    
    return "\n".join(report_lines)

def main():
    """主函數"""
    print("=" * 70)
    print("從 Z_drive 搜尋並同步必要檔案")
    print("權限等級：🔐 最高權限")
    print("=" * 70)
    print()
    
    if log_manager:
        log_manager.log_work(
            work_type="檔案同步",
            work_content="從 Z_drive 搜尋並同步必要檔案",
            agent="little_j",
            status="進行中",
            permission_level="最高權限"
        )
    
    # 檢查 Z_drive
    if not check_z_drive():
        log("無法繼續，Z_drive 不存在", "ERROR")
        return 1
    
    # 搜尋必要檔案
    found_files = search_necessary_files()
    
    # 顯示搜尋結果
    print()
    log("搜尋結果:", "INFO")
    total_found = sum(len(files) for files in found_files.values())
    log(f"總計找到 {total_found} 個可能相關的檔案", "INFO")
    for category, files in found_files.items():
        if files:
            log(f"  {category}: {len(files)} 個", "INFO")
    
    # 同步檔案
    if total_found > 0:
        print()
        sync_results = sync_necessary_files(found_files)
        
        # 顯示同步結果
        print()
        log("同步結果:", "INFO")
        for category, count in sync_results.items():
            if count > 0:
                log(f"  {category}: {count} 個檔案已同步", "OK")
    else:
        sync_results = {"credentials": 0, "configs": 0, "scripts": 0, "modules": 0, "docker": 0}
        log("未找到需要同步的檔案", "INFO")
    
    # 產生報告
    report = generate_sync_report(found_files, sync_results)
    report_file = BASE_DIR / "reports" / f"Z_DRIVE_SYNC_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_file.write_text(report, encoding='utf-8')
    log(f"✓ 同步報告已儲存: {report_file}", "OK")
    
    # 記錄完成
    if log_manager:
        result_summary = (
            f"找到 {total_found} 個檔案, "
            f"同步: 憑證{sync_results['credentials']}個, "
            f"配置{sync_results['configs']}個, "
            f"腳本{sync_results['scripts']}個, "
            f"模組{sync_results['modules']}個"
        )
        
        log_manager.log_work(
            work_type="檔案同步",
            work_content="從 Z_drive 搜尋並同步必要檔案",
            agent="little_j",
            status="完成",
            result=result_summary,
            related_files=[str(report_file)],
            permission_level="最高權限"
        )
    
    log("✅ Z_drive 檔案搜尋與同步完成", "OK")
    return 0

if __name__ == "__main__":
    sys.exit(main())
