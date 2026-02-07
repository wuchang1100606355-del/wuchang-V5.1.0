#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
configure_odoo_modules_and_company.py

Odoo 模組與公司資訊配置管理

功能：
- 檢查已安裝模組
- 配置公司資訊
- 管理組織結構
- 設定使用者權限
- 配置業務功能
"""

import sys
import json
import subprocess
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
CONFIG_DIR = BASE_DIR / "config"
ODOO_CONFIG_FILE = CONFIG_DIR / "odoo_config.json"

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

def search_company_data_from_system_folders() -> Dict:
    """從系統資料夾搜尋公司相關資料"""
    log("從系統資料夾搜尋公司資料...", "PROGRESS")
    
    # 匯入搜尋功能
    sys.path.insert(0, str(BASE_DIR / "scripts"))
    try:
        from search_system_data_and_assets import search_system_folders
        folders = search_system_folders()
        
        # 搜尋公司相關檔案
        company_data = {
            "logos": [],
            "documents": [],
            "configs": []
        }
        
        # 搜尋logo
        for file_list in [folders.get("uploads", []), folders.get("downloads", []), folders.get("wuchang_os", [])]:
            for file_path in file_list:
                if "logo" in file_path.name.lower() or "company" in file_path.name.lower():
                    if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.svg']:
                        company_data["logos"].append(str(file_path.relative_to(BASE_DIR)))
        
        # 搜尋公司文件
        for file_list in [folders.get("containers_data", []), folders.get("uploads", [])]:
            for file_path in file_list:
                if any(keyword in file_path.name.lower() for keyword in ["company", "organization", "company", "組織", "公司"]):
                    company_data["documents"].append(str(file_path.relative_to(BASE_DIR)))
        
        if company_data["logos"] or company_data["documents"]:
            log(f"✓ 找到 {len(company_data['logos'])} 個logo，{len(company_data['documents'])} 個文件", "OK")
        
        return company_data
    except Exception as e:
        log(f"✗ 搜尋公司資料時發生錯誤: {e}", "ERROR")
        return {"logos": [], "documents": [], "configs": []}

def load_odoo_config() -> Dict:
    """載入Odoo配置"""
    default_config = {
        "database": {
            "name": "admin",
            "host": "localhost",
            "port": 5432,
            "user": "odoo"
        },
        "company": {
            "name": "五常非營利組織",
            "name_en": "Wuchang Nonprofit Organization",
            "vat": "",
            "website": "www.wuchang.life",
            "email": "",
            "phone": "",
            "street": "",
            "city": "",
            "country": "台灣",
            "logo": ""
        },
        "modules": {
            "installed_modules": [],
            "required_modules": [
                "base",
                "web",
                "website",
                "sale",
                "purchase",
            ],
            "custom_modules": [
                "wuchang_credits_management"
            ]
        },
        "users": {
            "admin_users": [],
            "default_language": "zh_TW"
        },
        "features": {
            "multi_company": False,
            "multi_currency": False,
            "ecommerce": False,
            "project_management": True,
            "hr_management": False,
            "crm_enabled": True
        }
    }
    
    if ODOO_CONFIG_FILE.exists():
        try:
            with open(ODOO_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return {**default_config, **config}
        except:
            pass
    
    # 建立預設配置檔案
    ODOO_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ODOO_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, ensure_ascii=False, indent=2)
    
    return default_config

def check_odoo_container() -> Optional[str]:
    """檢查Odoo容器狀態"""
    log("檢查Odoo容器狀態...", "PROGRESS")
    
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=odoo", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            container_name = result.stdout.strip().split('\n')[0]
            log(f"✓ 找到Odoo容器: {container_name}", "OK")
            return container_name
        else:
            # 嘗試其他可能的容器名稱
            result2 = subprocess.run(
                ["docker", "ps", "--filter", "ancestor=odoo", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result2.returncode == 0 and result2.stdout.strip():
                container_name = result2.stdout.strip().split('\n')[0]
                log(f"✓ 找到Odoo容器: {container_name}", "OK")
                return container_name
        
        log("⚠️ 未找到運行中的Odoo容器", "WARN")
        return None
    except Exception as e:
        log(f"✗ 檢查容器時發生錯誤: {e}", "ERROR")
        return None

def check_installed_modules(container_name: str, db_name: str) -> List[str]:
    """檢查已安裝的模組"""
    log("檢查已安裝模組...", "PROGRESS")
    
    try:
        # 通過資料庫查詢已安裝模組
        cmd = [
            "docker", "exec", container_name,
            "psql", "-U", "odoo", "-d", db_name,
            "-t", "-c",
            "SELECT name FROM ir_module_module WHERE state='installed' ORDER BY name;"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            modules = [m.strip() for m in result.stdout.strip().split('\n') if m.strip()]
            log(f"✓ 發現 {len(modules)} 個已安裝模組", "OK")
            return modules
        else:
            log(f"✗ 查詢模組失敗: {result.stderr}", "ERROR")
            return []
    except Exception as e:
        log(f"✗ 檢查模組時發生錯誤: {e}", "ERROR")
        return []

def check_company_info(container_name: str, db_name: str) -> Dict:
    """檢查公司資訊"""
    log("檢查公司資訊...", "PROGRESS")
    
    try:
        cmd = [
            "docker", "exec", container_name,
            "psql", "-U", "odoo", "-d", db_name,
            "-t", "-c",
            "SELECT name, vat, website, email, phone, street, city FROM res_company LIMIT 1;"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            # 解析結果（簡化處理）
            log("✓ 找到公司資訊", "OK")
            return {"status": "已配置", "found": True}
        else:
            log("⚠️ 未找到公司資訊或查詢失敗", "WARN")
            return {"status": "未配置", "found": False}
    except Exception as e:
        log(f"✗ 檢查公司資訊時發生錯誤: {e}", "ERROR")
        return {"status": "檢查失敗", "error": str(e)}

def verify_custom_modules(config: Dict, installed_modules: List[str]) -> Dict:
    """驗證自訂模組"""
    log("驗證自訂模組...", "PROGRESS")
    
    custom_modules = config.get("modules", {}).get("custom_modules", [])
    results = {}
    
    for module in custom_modules:
        if module in installed_modules:
            results[module] = {"status": "已安裝", "installed": True}
            log(f"✓ 自訂模組已安裝: {module}", "OK")
        else:
            results[module] = {"status": "未安裝", "installed": False}
            log(f"⚠️ 自訂模組未安裝: {module}", "WARN")
    
    return results

def check_required_modules(config: Dict, installed_modules: List[str]) -> Dict:
    """檢查必要模組"""
    log("檢查必要模組...", "PROGRESS")
    
    required_modules = config.get("modules", {}).get("required_modules", [])
    missing_modules = [m for m in required_modules if m not in installed_modules]
    
    if missing_modules:
        log(f"⚠️ 以下必要模組未安裝: {', '.join(missing_modules)}", "WARN")
    else:
        log("✓ 所有必要模組已安裝", "OK")
    
    return {
        "required_count": len(required_modules),
        "installed_count": len(required_modules) - len(missing_modules),
        "missing_modules": missing_modules
    }

def generate_module_report(config: Dict, installed_modules: List[str], 
                           container_name: Optional[str], company_info: Dict) -> str:
    """產生模組與公司資訊報告"""
    report_lines = [
        "# Odoo 模組與公司資訊配置報告",
        "",
        f"**生成時間：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 容器狀態",
        f"- **容器名稱：** {container_name or '未找到'}",
        f"- **資料庫：** {config.get('database', {}).get('name', 'N/A')}",
        "",
        "## 模組狀態",
        f"- **已安裝模組總數：** {len(installed_modules)}",
        "",
        "### 必要模組",
    ]
    
    required_modules = config.get("modules", {}).get("required_modules", [])
    for module in required_modules:
        status = "✅ 已安裝" if module in installed_modules else "❌ 未安裝"
        report_lines.append(f"- {status} {module}")
    
    report_lines.extend([
        "",
        "### 自訂模組",
    ])
    
    custom_modules = config.get("modules", {}).get("custom_modules", [])
    for module in custom_modules:
        status = "✅ 已安裝" if module in installed_modules else "❌ 未安裝"
        report_lines.append(f"- {status} {module}")
    
    report_lines.extend([
        "",
        "## 公司資訊",
        f"- **狀態：** {company_info.get('status', 'N/A')}",
        f"- **配置名稱：** {config.get('company', {}).get('name', 'N/A')}",
        "",
        "## 功能啟用狀態",
    ])
    
    features = config.get("features", {})
    for feature, enabled in features.items():
        status = "✅ 啟用" if enabled else "❌ 未啟用"
        report_lines.append(f"- {status} {feature}")
    
    return "\n".join(report_lines)

def main():
    """主函數"""
    print("=" * 70)
    print("Odoo 模組與公司資訊配置管理")
    print("權限等級：🔐 最高權限")
    print("=" * 70)
    print()
    
    if log_manager:
        log_manager.log_work(
            work_type="Odoo配置",
            work_content="檢查和配置Odoo模組與公司資訊",
            agent="little_j",
            status="進行中",
            permission_level="最高權限"
        )
    
    # 載入配置
    config = load_odoo_config()
    log("✓ 已載入Odoo配置", "OK")
    
    # 從系統資料夾搜尋公司資料
    company_data = search_company_data_from_system_folders()
    if company_data["logos"]:
        # 更新配置中的logo路徑
        if not config.get("company", {}).get("logo"):
            config["company"]["logo"] = company_data["logos"][0]
            log(f"✓ 自動設定公司logo: {company_data['logos'][0]}", "OK")
    
    # 檢查容器
    container_name = check_odoo_container()
    
    if container_name:
        db_name = config.get("database", {}).get("name", "admin")
        
        # 檢查已安裝模組
        installed_modules = check_installed_modules(container_name, db_name)
        
        # 檢查公司資訊
        company_info = check_company_info(container_name, db_name)
        
        # 驗證自訂模組
        custom_modules_status = verify_custom_modules(config, installed_modules)
        
        # 檢查必要模組
        required_modules_status = check_required_modules(config, installed_modules)
        
        # 產生報告
        report = generate_module_report(config, installed_modules, container_name, company_info)
        
        # 儲存報告
        report_file = BASE_DIR / "reports" / f"ODOO_MODULES_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_file.write_text(report, encoding='utf-8')
        log(f"✓ 報告已儲存: {report_file}", "OK")
    else:
        log("⚠️ 無法執行完整檢查（容器未運行）", "WARN")
        installed_modules = []
        company_info = {"status": "無法檢查"}
        required_modules_status = {"required_count": 0, "missing_modules": []}
    
    # 產生摘要
    print()
    log("配置檢查摘要:", "INFO")
    print(f"  已安裝模組: {len(installed_modules)}")
    print(f"  必要模組: {required_modules_status.get('installed_count', 0)}/{required_modules_status.get('required_count', 0)}")
    print(f"  公司資訊: {company_info.get('status', 'N/A')}")
    
    # 記錄完成
    if log_manager:
        result_summary = (
            f"已安裝模組: {len(installed_modules)}個, "
            f"必要模組: {required_modules_status.get('installed_count', 0)}/{required_modules_status.get('required_count', 0)}, "
            f"公司資訊: {company_info.get('status', 'N/A')}"
        )
        
        log_manager.log_work(
            work_type="Odoo配置",
            work_content="檢查和配置Odoo模組與公司資訊",
            agent="little_j",
            status="完成",
            result=result_summary,
            related_files=[str(ODOO_CONFIG_FILE)],
            permission_level="最高權限"
        )
    
    log("✅ Odoo模組與公司資訊配置檢查完成", "OK")
    return 0

if __name__ == "__main__":
    sys.exit(main())
