#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
search_system_data_and_assets.py

搜尋系統資料夾內的各單位資料與網站素材

功能：
- 搜尋系統資料夾內的資料
- 索引各單位資料
- 查找網站素材
- 建立資料索引
"""

import sys
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

def search_system_folders() -> Dict[str, List[Path]]:
    """搜尋系統資料夾"""
    log("搜尋系統資料夾...", "PROGRESS")
    
    system_folders = {
        "containers_data": [],
        "uploads": [],
        "downloads": [],
        "wuchang_os": [],
        "website_assets": [],
        "config": [],
        "reports": []
    }
    
    # 搜尋容器資料夾
    containers_dir = BASE_DIR / "containers"
    if containers_dir.exists():
        for item in containers_dir.rglob("*"):
            if item.is_file() and not item.name.startswith('.'):
                system_folders["containers_data"].append(item)
    
    # 搜尋上傳資料夾
    uploads_dir = BASE_DIR / "uploads"
    if uploads_dir.exists():
        for item in uploads_dir.rglob("*"):
            if item.is_file() and not item.name.startswith('.'):
                system_folders["uploads"].append(item)
                # 檢查是否為網站素材
                if item.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.css', '.js', '.html']:
                    system_folders["website_assets"].append(item)
    
    # 搜尋下載資料夾
    downloads_dir = BASE_DIR / "downloads"
    if downloads_dir.exists():
        for item in downloads_dir.rglob("*"):
            if item.is_file() and not item.name.startswith('.'):
                system_folders["downloads"].append(item)
                # 檢查是否為網站素材
                if item.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.css', '.js', '.html']:
                    system_folders["website_assets"].append(item)
    
    # 搜尋 wuchang_os 資料夾
    wuchang_os_dir = BASE_DIR / "wuchang_os"
    if wuchang_os_dir.exists():
        for item in wuchang_os_dir.rglob("*"):
            if item.is_file() and not item.name.startswith('.'):
                system_folders["wuchang_os"].append(item)
                # 檢查是否為網站素材
                if item.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.css', '.js', '.html']:
                    system_folders["website_assets"].append(item)
    
    # 搜尋配置資料夾
    config_dir = BASE_DIR / "config"
    if config_dir.exists():
        for item in config_dir.rglob("*"):
            if item.is_file() and not item.name.startswith('.'):
                system_folders["config"].append(item)
    
    # 搜尋報告資料夾
    reports_dir = BASE_DIR / "reports"
    if reports_dir.exists():
        for item in reports_dir.rglob("*"):
            if item.is_file() and not item.name.startswith('.'):
                system_folders["reports"].append(item)
    
    return system_folders

def index_data_by_type(folders: Dict[str, List[Path]]) -> Dict[str, Dict]:
    """按類型索引資料"""
    log("建立資料索引...", "PROGRESS")
    
    index = {
        "images": [],
        "documents": [],
        "configs": [],
        "scripts": [],
        "data_files": []
    }
    
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp', '.ico']
    doc_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.md']
    config_extensions = ['.json', '.yaml', '.yml', '.xml', '.env', '.ini', '.conf']
    script_extensions = ['.py', '.ps1', '.sh', '.bat', '.js']
    
    all_files = []
    for file_list in folders.values():
        all_files.extend(file_list)
    
    for file_path in all_files:
        ext = file_path.suffix.lower()
        relative_path = file_path.relative_to(BASE_DIR)
        
        if ext in image_extensions:
            index["images"].append({
                "path": str(relative_path),
                "full_path": str(file_path),
                "size": file_path.stat().st_size if file_path.exists() else 0
            })
        elif ext in doc_extensions:
            index["documents"].append({
                "path": str(relative_path),
                "full_path": str(file_path),
                "size": file_path.stat().st_size if file_path.exists() else 0
            })
        elif ext in config_extensions:
            index["configs"].append({
                "path": str(relative_path),
                "full_path": str(file_path),
                "size": file_path.stat().st_size if file_path.exists() else 0
            })
        elif ext in script_extensions:
            index["scripts"].append({
                "path": str(relative_path),
                "full_path": str(file_path),
                "size": file_path.stat().st_size if file_path.exists() else 0
            })
        else:
            index["data_files"].append({
                "path": str(relative_path),
                "full_path": str(file_path),
                "size": file_path.stat().st_size if file_path.exists() else 0
            })
    
    return index

def generate_index_report(folders: Dict[str, List[Path]], index: Dict[str, Dict]) -> str:
    """產生索引報告"""
    report_lines = [
        "# 系統資料與網站素材索引報告",
        "",
        f"**生成時間：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 📁 資料夾統計",
        "",
    ]
    
    for folder_type, files in folders.items():
        report_lines.append(f"### {folder_type}")
        report_lines.append(f"- **檔案數量：** {len(files)}")
        if files:
            report_lines.append("- **範例檔案：**")
            for file_path in files[:5]:  # 顯示前5個
                relative_path = file_path.relative_to(BASE_DIR)
                report_lines.append(f"  - `{relative_path}`")
            if len(files) > 5:
                report_lines.append(f"  - ... 還有 {len(files) - 5} 個檔案")
        report_lines.append("")
    
    report_lines.extend([
        "## 📊 資料類型索引",
        "",
        "### 圖片檔案",
        f"- **數量：** {len(index['images'])}",
        ""
    ])
    
    if index["images"]:
        report_lines.append("**網站素材圖片：**")
        for img in index["images"][:10]:
            report_lines.append(f"- `{img['path']}` ({img['size']} bytes)")
        report_lines.append("")
    
    report_lines.extend([
        "### 文件檔案",
        f"- **數量：** {len(index['documents'])}",
        "",
        "### 配置檔案",
        f"- **數量：** {len(index['configs'])}",
        "",
        "### 腳本檔案",
        f"- **數量：** {len(index['scripts'])}",
        "",
        "## 🎨 網站素材位置",
        "",
        "**主要位置：**",
        "- `uploads/` - 上傳的網站素材",
        "- `downloads/` - 下載的素材檔案",
        "- `wuchang_os/` - Odoo 相關素材",
        "",
        f"**總計網站素材檔案：** {len(folders['website_assets'])} 個",
    ])
    
    return "\n".join(report_lines)

def main():
    """主函數"""
    print("=" * 70)
    print("搜尋系統資料夾內的各單位資料與網站素材")
    print("權限等級：🔐 最高權限")
    print("=" * 70)
    print()
    
    if log_manager:
        log_manager.log_work(
            work_type="系統資料搜尋",
            work_content="搜尋系統資料夾內的各單位資料與網站素材",
            agent="little_j",
            status="進行中",
            permission_level="最高權限"
        )
    
    # 搜尋系統資料夾
    folders = search_system_folders()
    
    # 顯示統計
    log("資料夾統計:", "INFO")
    for folder_type, files in folders.items():
        log(f"  {folder_type}: {len(files)} 個檔案", "INFO")
    
    # 建立索引
    index = index_data_by_type(folders)
    
    # 顯示索引統計
    print()
    log("資料類型索引:", "INFO")
    for data_type, items in index.items():
        log(f"  {data_type}: {len(items)} 個檔案", "INFO")
    
    # 產生報告
    report = generate_index_report(folders, index)
    report_file = BASE_DIR / "reports" / f"SYSTEM_DATA_INDEX_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_file.write_text(report, encoding='utf-8')
    log(f"✓ 索引報告已儲存: {report_file}", "OK")
    
    # 記錄完成
    if log_manager:
        result_summary = (
            f"找到 {sum(len(files) for files in folders.values())} 個檔案, "
            f"網站素材: {len(folders['website_assets'])} 個"
        )
        
        log_manager.log_work(
            work_type="系統資料搜尋",
            work_content="搜尋系統資料夾內的各單位資料與網站素材",
            agent="little_j",
            status="完成",
            result=result_summary,
            related_files=[str(report_file)],
            permission_level="最高權限"
        )
    
    log("✅ 系統資料搜尋完成", "OK")
    return 0

if __name__ == "__main__":
    sys.exit(main())
