#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
google_nonprofit_tools_setup.py

Google Workspace 及 Google Cloud 非營利組織免費工具下載與配置工具

功能：
- 下載並配置 Google Workspace for Nonprofits 工具
- 下載並配置 Google Cloud 非營利組織免費服務
- 整合內部開發程式
- 記錄配置狀態和抵免額使用情況
"""

import sys
import json
import os
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "google_nonprofit_tools_config.json"
SETUP_LOG_FILE = BASE_DIR / "google_nonprofit_tools_setup.log"

# Google 非營利組織工具清單
GOOGLE_WORKSPACE_TOOLS = {
    "workspace_business_starter": {
        "name": "Google Workspace Business Starter",
        "description": "協會網域信箱、共用雲端文件、會議、管理控台",
        "url": "https://www.google.com/nonprofits/offerings/workspace/",
        "api_services": [
            "gmail",
            "drive",
            "docs",
            "sheets",
            "slides",
            "calendar",
            "meet",
            "admin_sdk"
        ],
        "python_packages": [
            "google-api-python-client",
            "google-auth",
            "google-auth-oauthlib",
            "google-auth-httplib2"
        ],
        "status": "available"
    },
    "ad_grants": {
        "name": "Google Ad Grants",
        "description": "搜尋廣告額度（每月上限 USD $10,000）",
        "url": "https://www.google.com/nonprofits/offerings/google-ad-grants/",
        "api_services": [
            "google_ads_api"
        ],
        "python_packages": [
            "google-ads"
        ],
        "status": "available"
    }
}

GOOGLE_CLOUD_TOOLS = {
    "maps_platform": {
        "name": "Google Maps Platform 公益方案",
        "description": "地圖 API 抵免（依公益方案與審核）",
        "url": "https://developers.google.com/maps/billing-and-pricing/public-programs",
        "api_services": [
            "maps",
            "places",
            "geocoding",
            "directions",
            "distance_matrix"
        ],
        "python_packages": [
            "googlemaps"
        ],
        "status": "available"
    },
    "cloud_credits": {
        "name": "Google Cloud Credits",
        "description": "專案型/申請型 credit 或 need-based grant",
        "url": "https://www.google.com/nonprofits/cloud/",
        "api_services": [
            "compute",
            "storage",
            "bigquery",
            "ai_platform",
            "vertex_ai"
        ],
        "python_packages": [
            "google-cloud-storage",
            "google-cloud-bigquery",
            "google-cloud-aiplatform"
        ],
        "status": "available"
    },
    "vertex_ai": {
        "name": "Vertex AI (Generative AI)",
        "description": "生成式 AI 服務（可用於地端小J學習功能）",
        "url": "https://cloud.google.com/vertex-ai",
        "api_services": [
            "vertex_ai",
            "generative_ai"
        ],
        "python_packages": [
            "google-cloud-aiplatform",
            "google-generativeai"
        ],
        "status": "available"
    }
}

# 內部開發程式清單
INTERNAL_PROGRAMS = {
    "google_workspace_writer": {
        "name": "Google Workspace Writer",
        "file": "google_workspace_writer.py",
        "description": "把中控/小J代理輸出寫入 Google Workspace",
        "status": "installed"
    },
    "google_tasks_integration": {
        "name": "Google Tasks Integration",
        "file": "google_tasks_integration.py",
        "description": "Google Tasks API 整合，用於雙J協作",
        "status": "installed"
    },
    "google_nonprofit_compliance_check": {
        "name": "Google Nonprofit Compliance Check",
        "file": "google_nonprofit_compliance_check.py",
        "description": "全系統 Google 非營利組織合規檢查",
        "status": "installed"
    }
}


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
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{icon} [{timestamp}] [{level}] {message}"
    print(log_entry)
    
    try:
        with open(SETUP_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{log_entry}\n")
    except:
        pass


def load_config() -> Dict[str, Any]:
    """載入配置檔案"""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            log(f"載入配置檔案失敗: {e}", "ERROR")
            return {}
    return {}


def save_config(config: Dict[str, Any]):
    """儲存配置檔案"""
    try:
        CONFIG_FILE.write_text(
            json.dumps(config, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        log("配置檔案已儲存", "OK")
    except Exception as e:
        log(f"儲存配置檔案失敗: {e}", "ERROR")


def check_python_package(package_name: str) -> bool:
    """檢查 Python 套件是否已安裝"""
    try:
        __import__(package_name.replace("-", "_"))
        return True
    except ImportError:
        return False


def install_python_package(package_name: str) -> bool:
    """安裝 Python 套件"""
    log(f"安裝 Python 套件: {package_name}", "PROGRESS")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            check=True,
            capture_output=True,
            text=True
        )
        log(f"已安裝: {package_name}", "OK")
        return True
    except subprocess.CalledProcessError as e:
        log(f"安裝失敗: {package_name} - {e}", "ERROR")
        return False


def setup_google_workspace_tools() -> Dict[str, Any]:
    """設定 Google Workspace 工具"""
    log("開始設定 Google Workspace 工具", "PROGRESS")
    results = {}
    
    for tool_id, tool_info in GOOGLE_WORKSPACE_TOOLS.items():
        log(f"處理工具: {tool_info['name']}", "INFO")
        tool_result = {
            "name": tool_info["name"],
            "status": "pending",
            "packages_installed": [],
            "packages_failed": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # 安裝 Python 套件
        for package in tool_info.get("python_packages", []):
            if check_python_package(package):
                log(f"套件已安裝: {package}", "OK")
                tool_result["packages_installed"].append(package)
            else:
                if install_python_package(package):
                    tool_result["packages_installed"].append(package)
                else:
                    tool_result["packages_failed"].append(package)
        
        if not tool_result["packages_failed"]:
            tool_result["status"] = "installed"
        else:
            tool_result["status"] = "partial"
        
        results[tool_id] = tool_result
    
    return results


def setup_google_cloud_tools() -> Dict[str, Any]:
    """設定 Google Cloud 工具"""
    log("開始設定 Google Cloud 工具", "PROGRESS")
    results = {}
    
    for tool_id, tool_info in GOOGLE_CLOUD_TOOLS.items():
        log(f"處理工具: {tool_info['name']}", "INFO")
        tool_result = {
            "name": tool_info["name"],
            "status": "pending",
            "packages_installed": [],
            "packages_failed": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # 安裝 Python 套件
        for package in tool_info.get("python_packages", []):
            if check_python_package(package):
                log(f"套件已安裝: {package}", "OK")
                tool_result["packages_installed"].append(package)
            else:
                if install_python_package(package):
                    tool_result["packages_installed"].append(package)
                else:
                    tool_result["packages_failed"].append(package)
        
        if not tool_result["packages_failed"]:
            tool_result["status"] = "installed"
        else:
            tool_result["status"] = "partial"
        
        results[tool_id] = tool_result
    
    return results


def verify_internal_programs() -> Dict[str, Any]:
    """驗證內部開發程式"""
    log("驗證內部開發程式", "PROGRESS")
    results = {}
    
    for program_id, program_info in INTERNAL_PROGRAMS.items():
        program_file = BASE_DIR / program_info["file"]
        program_result = {
            "name": program_info["name"],
            "file": program_info["file"],
            "status": "not_found",
            "timestamp": datetime.now().isoformat()
        }
        
        if program_file.exists():
            program_result["status"] = "found"
            log(f"找到內部程式: {program_info['name']}", "OK")
        else:
            log(f"未找到內部程式: {program_info['name']}", "WARN")
        
        results[program_id] = program_result
    
    return results


def generate_setup_report(workspace_results: Dict, cloud_results: Dict, internal_results: Dict) -> str:
    """生成設定報告"""
    report = []
    report.append("# Google 非營利組織工具設定報告")
    report.append(f"\n生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    report.append("## Google Workspace 工具")
    for tool_id, result in workspace_results.items():
        status_icon = "✅" if result["status"] == "installed" else "⚠️" if result["status"] == "partial" else "❌"
        report.append(f"\n### {status_icon} {result['name']}")
        report.append(f"- 狀態: {result['status']}")
        report.append(f"- 已安裝套件: {', '.join(result['packages_installed']) if result['packages_installed'] else '無'}")
        if result['packages_failed']:
            report.append(f"- 失敗套件: {', '.join(result['packages_failed'])}")
    
    report.append("\n## Google Cloud 工具")
    for tool_id, result in cloud_results.items():
        status_icon = "✅" if result["status"] == "installed" else "⚠️" if result["status"] == "partial" else "❌"
        report.append(f"\n### {status_icon} {result['name']}")
        report.append(f"- 狀態: {result['status']}")
        report.append(f"- 已安裝套件: {', '.join(result['packages_installed']) if result['packages_installed'] else '無'}")
        if result['packages_failed']:
            report.append(f"- 失敗套件: {', '.join(result['packages_failed'])}")
    
    report.append("\n## 內部開發程式")
    for program_id, result in internal_results.items():
        status_icon = "✅" if result["status"] == "found" else "❌"
        report.append(f"\n### {status_icon} {result['name']}")
        report.append(f"- 狀態: {result['status']}")
        report.append(f"- 檔案: {result['file']}")
    
    return "\n".join(report)


def main():
    """主函數"""
    log("開始 Google 非營利組織工具設定", "PROGRESS")
    
    # 載入現有配置
    config = load_config()
    config["last_setup"] = datetime.now().isoformat()
    
    # 設定 Google Workspace 工具
    workspace_results = setup_google_workspace_tools()
    config["google_workspace_tools"] = workspace_results
    
    # 設定 Google Cloud 工具
    cloud_results = setup_google_cloud_tools()
    config["google_cloud_tools"] = cloud_results
    
    # 驗證內部程式
    internal_results = verify_internal_programs()
    config["internal_programs"] = internal_results
    
    # 儲存配置
    save_config(config)
    
    # 生成報告
    report = generate_setup_report(workspace_results, cloud_results, internal_results)
    report_file = BASE_DIR / f"google_nonprofit_tools_setup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_file.write_text(report, encoding="utf-8")
    log(f"報告已儲存: {report_file.name}", "OK")
    
    print("\n" + "="*60)
    print(report)
    print("="*60)
    
    log("Google 非營利組織工具設定完成", "OK")


if __name__ == "__main__":
    main()
