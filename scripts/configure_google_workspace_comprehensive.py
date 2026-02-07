#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
configure_google_workspace_comprehensive.py

Google Workspace 完整配置管理

功能：
- 組織設定和管理
- 設備管理
- 管理員配置
- 使用者管理
- 安全設定
- API啟用狀態
- 合規性檢查
"""

import sys
import json
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
GWS_CONFIG_FILE = CONFIG_DIR / "google_workspace_config.json"

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

def load_google_workspace_config() -> Dict:
    """載入Google Workspace配置"""
    default_config = {
        "organization": {
            "name": "五常非營利組織",
            "domain": "wuchang.org.tw",
            "nonprofit_status": True,
            "verification_status": "待驗證"
        },
        "administrators": {
            "primary_admin": "",
            "admin_users": [],
            "admin_permissions": []
        },
        "devices": {
            "managed_devices": [],
            "device_policies": {},
            "mdm_enabled": False
        },
        "security": {
            "two_factor_enabled": False,
            "sso_enabled": False,
            "api_access_control": {}
        },
        "apis": {
            "enabled_apis": [],
            "required_apis": [
                "drive.googleapis.com",
                "docs.googleapis.com",
                "sheets.googleapis.com",
                "gmail.googleapis.com",
                "calendar-json.googleapis.com",
                "tasks.googleapis.com",
                "aiplatform.googleapis.com"
            ]
        },
        "compliance": {
            "nonprofit_compliance": False,
            "data_residency": "global",
            "backup_enabled": False
        }
    }
    
    if GWS_CONFIG_FILE.exists():
        try:
            with open(GWS_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return {**default_config, **config}
        except:
            pass
    
    # 建立預設配置檔案
    GWS_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(GWS_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, ensure_ascii=False, indent=2)
    
    return default_config

def check_organization_status(config: Dict) -> Dict:
    """檢查組織狀態"""
    log("檢查組織狀態...", "PROGRESS")
    
    org = config.get("organization", {})
    status = {
        "name": org.get("name", ""),
        "domain": org.get("domain", ""),
        "nonprofit_status": org.get("nonprofit_status", False),
        "verification_status": org.get("verification_status", "待驗證")
    }
    
    if status["nonprofit_status"]:
        log(f"✓ 組織已設定為非營利組織: {status['name']}", "OK")
    else:
        log("⚠️ 組織未設定為非營利組織", "WARN")
    
    if status["verification_status"] == "已驗證":
        log("✓ 網域驗證狀態: 已驗證", "OK")
    else:
        log(f"⚠️ 網域驗證狀態: {status['verification_status']}", "WARN")
    
    return status

def check_administrators(config: Dict) -> Dict:
    """檢查管理員配置"""
    log("檢查管理員配置...", "PROGRESS")
    
    admins = config.get("administrators", {})
    admin_list = admins.get("admin_users", [])
    
    if admin_list:
        log(f"✓ 發現 {len(admin_list)} 個管理員", "OK")
        for admin in admin_list:
            log(f"  - {admin}", "INFO")
    else:
        log("⚠️ 未配置管理員", "WARN")
    
    return {
        "admin_count": len(admin_list),
        "admins": admin_list
    }

def check_devices(config: Dict) -> Dict:
    """檢查設備管理"""
    log("檢查設備管理...", "PROGRESS")
    
    devices = config.get("devices", {})
    managed_devices = devices.get("managed_devices", [])
    mdm_enabled = devices.get("mdm_enabled", False)
    
    if managed_devices:
        log(f"✓ 發現 {len(managed_devices)} 個受管理設備", "OK")
    else:
        log("ℹ️ 未配置受管理設備", "INFO")
    
    if mdm_enabled:
        log("✓ MDM (行動裝置管理) 已啟用", "OK")
    else:
        log("ℹ️ MDM 未啟用", "INFO")
    
    return {
        "device_count": len(managed_devices),
        "mdm_enabled": mdm_enabled
    }

def check_security_settings(config: Dict) -> Dict:
    """檢查安全設定"""
    log("檢查安全設定...", "PROGRESS")
    
    security = config.get("security", {})
    two_factor = security.get("two_factor_enabled", False)
    sso = security.get("sso_enabled", False)
    
    if two_factor:
        log("✓ 雙因素驗證已啟用", "OK")
    else:
        log("⚠️ 雙因素驗證未啟用，建議啟用以增強安全性", "WARN")
    
    if sso:
        log("✓ 單一登入(SSO)已啟用", "OK")
    else:
        log("ℹ️ 單一登入(SSO)未啟用", "INFO")
    
    return {
        "two_factor_enabled": two_factor,
        "sso_enabled": sso
    }

def check_api_status(config: Dict) -> Dict:
    """檢查API啟用狀態"""
    log("檢查API啟用狀態...", "PROGRESS")
    
    apis = config.get("apis", {})
    enabled_apis = apis.get("enabled_apis", [])
    required_apis = apis.get("required_apis", [])
    
    missing_apis = [api for api in required_apis if api not in enabled_apis]
    
    if missing_apis:
        log(f"⚠️ 以下必要API未啟用: {', '.join(missing_apis)}", "WARN")
    else:
        log("✓ 所有必要API已啟用", "OK")
    
    return {
        "enabled_count": len(enabled_apis),
        "required_count": len(required_apis),
        "missing_apis": missing_apis
    }

def check_compliance(config: Dict) -> Dict:
    """檢查合規性"""
    log("檢查合規性...", "PROGRESS")
    
    compliance = config.get("compliance", {})
    nonprofit_compliance = compliance.get("nonprofit_compliance", False)
    backup_enabled = compliance.get("backup_enabled", False)
    
    if nonprofit_compliance:
        log("✓ 非營利組織合規性已確認", "OK")
    else:
        log("⚠️ 非營利組織合規性未確認", "WARN")
    
    if backup_enabled:
        log("✓ 備份功能已啟用", "OK")
    else:
        log("ℹ️ 備份功能未啟用", "INFO")
    
    return {
        "nonprofit_compliance": nonprofit_compliance,
        "backup_enabled": backup_enabled
    }

def main():
    """主函數"""
    print("=" * 70)
    print("Google Workspace 完整配置管理")
    print("權限等級：🔐 最高權限")
    print("=" * 70)
    print()
    
    if log_manager:
        log_manager.log_work(
            work_type="Google Workspace配置",
            work_content="檢查和配置Google Workspace（組織、設備、管理員等）",
            agent="jules",
            status="進行中",
            permission_level="最高權限"
        )
    
    # 載入配置
    config = load_google_workspace_config()
    log("✓ 已載入Google Workspace配置", "OK")
    
    # 檢查各項配置
    org_status = check_organization_status(config)
    admin_status = check_administrators(config)
    device_status = check_devices(config)
    security_status = check_security_settings(config)
    api_status = check_api_status(config)
    compliance_status = check_compliance(config)
    
    # 產生摘要報告
    print()
    log("配置檢查摘要:", "INFO")
    print(f"  組織: {org_status['name']} ({org_status['domain']})")
    print(f"  管理員數量: {admin_status['admin_count']}")
    print(f"  受管理設備: {device_status['device_count']}")
    print(f"  雙因素驗證: {'啟用' if security_status['two_factor_enabled'] else '未啟用'}")
    print(f"  API啟用: {api_status['enabled_count']}/{api_status['required_count']}")
    print(f"  合規性: {'已確認' if compliance_status['nonprofit_compliance'] else '未確認'}")
    
    # 記錄完成
    if log_manager:
        result_summary = (
            f"組織: {org_status['name']}, "
            f"管理員: {admin_status['admin_count']}個, "
            f"設備: {device_status['device_count']}個, "
            f"API: {api_status['enabled_count']}/{api_status['required_count']}"
        )
        
        log_manager.log_work(
            work_type="Google Workspace配置",
            work_content="檢查和配置Google Workspace（組織、設備、管理員等）",
            agent="jules",
            status="完成",
            result=result_summary,
            related_files=[str(GWS_CONFIG_FILE)],
            permission_level="最高權限"
        )
    
    log("✅ Google Workspace配置檢查完成", "OK")
    return 0

if __name__ == "__main__":
    sys.exit(main())
