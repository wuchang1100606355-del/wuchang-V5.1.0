#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_local_system.py

重新掃描地端庫系統

功能：
- 掃描所有目錄結構
- 檢查必要檔案
- 檢查系統狀態
- 生成完整掃描報告
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent

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

def scan_directory_structure() -> Dict:
    """掃描目錄結構"""
    log("掃描目錄結構...", "PROGRESS")
    
    key_directories = {
        "containers": ["config", "data", "logs", "uploads"],
        "backups": ["database", "system", "migration"],
        "local_storage": ["data", "database"],
        "wuchang_os": ["addons"],
        "cloudflared": [],
        "scripts": [],
        "reports": [],
        "config": ["ai_agents", "gcp"],
        "uploads": []
    }
    
    results = {}
    
    for base_dir, subdirs in key_directories.items():
        dir_path = BASE_DIR / base_dir
        if dir_path.exists():
            results[base_dir] = {
                "exists": True,
                "path": str(dir_path),
                "files": [],
                "subdirs": {}
            }
            
            # 掃描檔案
            try:
                for item in dir_path.iterdir():
                    if item.is_file():
                        results[base_dir]["files"].append({
                            "name": item.name,
                            "size": item.stat().st_size,
                            "modified": datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                        })
            except Exception as e:
                log(f"掃描 {base_dir} 時發生錯誤: {e}", "WARN")
            
            # 掃描子目錄
            for subdir in subdirs:
                subdir_path = dir_path / subdir
                if subdir_path.exists():
                    results[base_dir]["subdirs"][subdir] = True
                else:
                    results[base_dir]["subdirs"][subdir] = False
        else:
            results[base_dir] = {"exists": False}
    
    return results

def scan_necessary_files() -> Dict:
    """掃描必要檔案"""
    log("掃描必要檔案...", "PROGRESS")
    
    necessary_files = {
        "docker_compose": [
            "docker-compose.unified.yml",
            "docker-compose.cloud.yml"
        ],
        "config_files": [
            "containers/config/example.env",
            ".env",
            "cloudflared/config.yml",
            "ai_router.json",
            "router_secrets.json"
        ],
        "certificates": [
            "cloudflared/cert.pem",
            "cloudflared/key.pem",
            "cloudflared/cert_key.tar"
        ],
        "scripts": [
            "scripts/check_module_installation.py",
            "scripts/search_system_data_and_assets.py",
            "scripts/configure_odoo_modules_and_company.py"
        ],
        "documentation": [
            "README.md",
            "reports/SYSTEM_WORK_LOGS.md"
        ]
    }
    
    results = {}
    
    for category, files in necessary_files.items():
        results[category] = {}
        for file_path in files:
            full_path = BASE_DIR / file_path
            if full_path.exists():
                stat = full_path.stat()
                results[category][file_path] = {
                    "exists": True,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                results[category][file_path] = {"exists": False}
    
    return results

def scan_odoo_modules() -> Dict:
    """掃描 Odoo 模組"""
    log("掃描 Odoo 模組...", "PROGRESS")
    
    modules_dir = BASE_DIR / "wuchang_os" / "addons"
    results = {
        "modules_dir_exists": modules_dir.exists(),
        "modules": []
    }
    
    if modules_dir.exists():
        try:
            for item in modules_dir.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    manifest_file = item / "__manifest__.py"
                    if manifest_file.exists():
                        results["modules"].append({
                            "name": item.name,
                            "path": str(item.relative_to(BASE_DIR)),
                            "has_manifest": True
                        })
        except Exception as e:
            log(f"掃描 Odoo 模組時發生錯誤: {e}", "WARN")
    
    return results

def scan_docker_containers() -> Dict:
    """掃描 Docker 容器狀態"""
    log("檢查 Docker 容器狀態...", "PROGRESS")
    
    import subprocess
    
    results = {
        "docker_available": False,
        "containers": []
    }
    
    try:
        # 檢查 Docker 是否可用
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            results["docker_available"] = True
            for line in result.stdout.strip().split("\n"):
                if line:
                    try:
                        container_info = json.loads(line)
                        results["containers"].append({
                            "name": container_info.get("Names", ""),
                            "status": container_info.get("Status", ""),
                            "image": container_info.get("Image", "")
                        })
                    except:
                        pass
    except Exception as e:
        log(f"檢查 Docker 容器時發生錯誤: {e}", "WARN")
    
    return results

def generate_scan_report(dir_structure: Dict, necessary_files: Dict, odoo_modules: Dict, docker_containers: Dict) -> str:
    """生成掃描報告"""
    
    report_lines = [
        "# 地端庫系統掃描報告",
        "",
        f"**掃描時間：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 📁 目錄結構掃描",
        "",
    ]
    
    # 目錄結構
    for dir_name, dir_info in dir_structure.items():
        if dir_info.get("exists"):
            report_lines.append(f"### {dir_name}/")
            report_lines.append(f"- ✅ 存在: {dir_info['path']}")
            
            # 子目錄
            if "subdirs" in dir_info:
                for subdir, exists in dir_info["subdirs"].items():
                    status = "✅" if exists else "❌"
                    report_lines.append(f"  - {status} {subdir}/")
            
            # 檔案數量
            if "files" in dir_info:
                file_count = len(dir_info["files"])
                if file_count > 0:
                    report_lines.append(f"- 📄 檔案數: {file_count}")
                    # 顯示前5個檔案
                    for file_info in dir_info["files"][:5]:
                        size_kb = file_info["size"] / 1024
                        report_lines.append(f"  - `{file_info['name']}` ({size_kb:.2f} KB)")
                    if file_count > 5:
                        report_lines.append(f"  - ... 還有 {file_count - 5} 個檔案")
            report_lines.append("")
        else:
            report_lines.append(f"### {dir_name}/")
            report_lines.append(f"- ❌ 不存在")
            report_lines.append("")
    
    # 必要檔案
    report_lines.extend([
        "## 📄 必要檔案掃描",
        "",
    ])
    
    for category, files in necessary_files.items():
        report_lines.append(f"### {category}")
        for file_path, file_info in files.items():
            if file_info.get("exists"):
                size_kb = file_info["size"] / 1024
                report_lines.append(f"- ✅ `{file_path}` ({size_kb:.2f} KB, 修改時間: {file_info['modified']})")
            else:
                report_lines.append(f"- ❌ `{file_path}` (不存在)")
        report_lines.append("")
    
    # Odoo 模組
    report_lines.extend([
        "## 🔌 Odoo 模組掃描",
        "",
    ])
    
    if odoo_modules.get("modules_dir_exists"):
        report_lines.append("✅ Odoo 模組目錄存在")
        modules = odoo_modules.get("modules", [])
        if modules:
            report_lines.append(f"找到 {len(modules)} 個模組：")
            for module in modules:
                report_lines.append(f"- ✅ `{module['name']}` - {module['path']}")
        else:
            report_lines.append("⚠️ 未找到模組")
        report_lines.append("")
    else:
        report_lines.append("❌ Odoo 模組目錄不存在")
        report_lines.append("")
    
    # Docker 容器
    report_lines.extend([
        "## 🐳 Docker 容器狀態",
        "",
    ])
    
    if docker_containers.get("docker_available"):
        report_lines.append("✅ Docker 可用")
        containers = docker_containers.get("containers", [])
        if containers:
            report_lines.append(f"找到 {len(containers)} 個容器：")
            for container in containers:
                status_icon = "✅" if "Up" in container.get("status", "") else "⏸️"
                report_lines.append(f"- {status_icon} `{container['name']}` - {container['status']}")
        else:
            report_lines.append("ℹ️ 未找到容器")
        report_lines.append("")
    else:
        report_lines.append("⚠️ Docker 不可用或未安裝")
        report_lines.append("")
    
    # 統計
    report_lines.extend([
        "## 📊 掃描統計",
        "",
    ])
    
    total_dirs = sum(1 for d in dir_structure.values() if d.get("exists"))
    total_files = sum(len(d.get("files", [])) for d in dir_structure.values() if d.get("exists"))
    total_modules = len(odoo_modules.get("modules", []))
    total_containers = len(docker_containers.get("containers", []))
    
    report_lines.append(f"- **目錄總數：** {total_dirs}")
    report_lines.append(f"- **檔案總數：** {total_files}")
    report_lines.append(f"- **Odoo 模組：** {total_modules}")
    report_lines.append(f"- **Docker 容器：** {total_containers}")
    report_lines.append("")
    
    return "\n".join(report_lines)

def main():
    """主函數"""
    print("=" * 70)
    print("地端庫系統掃描")
    print("權限等級：🔐 最高權限")
    print("=" * 70)
    print()
    
    if log_manager:
        log_manager.log_work(
            work_type="系統掃描",
            work_content="重新掃描地端庫系統",
            agent="little_j",
            status="進行中",
            permission_level="最高權限"
        )
    
    # 掃描各個部分
    dir_structure = scan_directory_structure()
    necessary_files = scan_necessary_files()
    odoo_modules = scan_odoo_modules()
    docker_containers = scan_docker_containers()
    
    # 生成報告
    report = generate_scan_report(dir_structure, necessary_files, odoo_modules, docker_containers)
    report_file = BASE_DIR / "reports" / f"LOCAL_SYSTEM_SCAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_file.write_text(report, encoding='utf-8')
    
    log(f"✅ 掃描報告已儲存: {report_file}", "OK")
    
    # 記錄完成
    if log_manager:
        log_manager.log_work(
            work_type="系統掃描",
            work_content="重新掃描地端庫系統",
            agent="little_j",
            status="完成",
            result=f"生成掃描報告: {report_file.name}",
            related_files=[str(report_file)],
            permission_level="最高權限"
        )
    
    print()
    log("✅ 地端庫系統掃描完成", "OK")
    print()
    log(f"📄 掃描報告: {report_file.relative_to(BASE_DIR)}", "INFO")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
