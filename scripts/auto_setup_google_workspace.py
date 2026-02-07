#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_setup_google_workspace.py

全自動設定 Google Workspace 應用軟體

根據授權文件自動設定：
- Google OAuth 憑證
- Google Workspace APIs
- 服務帳戶配置
- API 啟用狀態檢查
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional, List

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent

# 授權文件路徑
AUTH_DOC_1 = BASE_DIR / "LITTLE_J_CREDENTIALS_SETUP.md"
AUTH_DOC_2 = BASE_DIR / "MULTIMEDIA_AI_FEATURES.md"

# Google 配置路徑
GOOGLE_CREDENTIALS = BASE_DIR / "google_credentials.json"
GOOGLE_TOKEN = BASE_DIR / "google_token.json"
SERVICE_ACCOUNT_KEY = BASE_DIR / "config" / "gcp" / "littlej-sa.json"
CONFIG_DIR = BASE_DIR / "config" / "gcp"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Google Workspace 配置
OAUTH_CLIENT_ID = "581281764864-4eg0icu55pkmbcirheflhp7fgt7gk499.apps.googleusercontent.com"
OAUTH_APP_NAME = "Wuchang-life"
PROJECT_ID = "my-j-483304"
SERVICE_ACCOUNT_EMAIL = "littlej-sa@my-j-483304.iam.gserviceaccount.com"

# 需要啟用的 API
REQUIRED_APIS = [
    "drive.googleapis.com",
    "docs.googleapis.com",
    "sheets.googleapis.com",
    "gmail.googleapis.com",
    "calendar-json.googleapis.com",
    "aiplatform.googleapis.com",
    "cloudbuild.googleapis.com"
]


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌",
        "STEP": "📋"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")


def check_authorization_documents() -> bool:
    """檢查授權文件"""
    log("檢查授權文件...", "STEP")
    
    if not AUTH_DOC_1.exists():
        log(f"✗ 授權文件 1 不存在: {AUTH_DOC_1.name}", "ERROR")
        return False
    
    if not AUTH_DOC_2.exists():
        log(f"✗ 授權文件 2 不存在: {AUTH_DOC_2.name}", "ERROR")
        return False
    
    log("✓ 授權文件完整", "OK")
    return True


def check_google_credentials() -> bool:
    """檢查 Google OAuth 憑證"""
    log("檢查 Google OAuth 憑證...", "STEP")
    
    if GOOGLE_CREDENTIALS.exists():
        try:
            with open(GOOGLE_CREDENTIALS, 'r', encoding='utf-8') as f:
                creds = json.load(f)
                if "installed" in creds or "web" in creds:
                    log("✓ Google OAuth 憑證已存在且格式正確", "OK")
                    return True
                else:
                    log("⚠ Google OAuth 憑證格式可能有問題", "WARN")
        except Exception as e:
            log(f"✗ 讀取憑證失敗: {e}", "ERROR")
    else:
        log("⚠ Google OAuth 憑證不存在", "WARN")
        log("需要從 Google Cloud Console 下載憑證", "INFO")
        log(f"OAuth 用戶端 ID: {OAUTH_APP_NAME}", "INFO")
        log(f"客戶端 ID: {OAUTH_CLIENT_ID}", "INFO")
        log("下載連結: https://console.cloud.google.com/apis/credentials", "INFO")
    
    return False


def check_service_account() -> bool:
    """檢查服務帳戶"""
    log("檢查服務帳戶...", "STEP")
    
    if SERVICE_ACCOUNT_KEY.exists():
        try:
            with open(SERVICE_ACCOUNT_KEY, 'r', encoding='utf-8') as f:
                sa_data = json.load(f)
                if "type" in sa_data and sa_data["type"] == "service_account":
                    log("✓ 服務帳戶金鑰已存在", "OK")
                    return True
        except Exception as e:
            log(f"✗ 讀取服務帳戶失敗: {e}", "ERROR")
    else:
        log("⚠ 服務帳戶金鑰不存在", "WARN")
        log("需要從 GCP Console 下載服務帳戶金鑰", "INFO")
        log(f"服務帳戶: {SERVICE_ACCOUNT_EMAIL}", "INFO")
        log("下載連結: https://console.cloud.google.com/iam-admin/serviceaccounts", "INFO")
    
    return False


def check_python_packages() -> bool:
    """檢查 Python 套件"""
    log("檢查 Python 套件...", "STEP")
    
    required_packages = {
        "google.auth": "google-auth",
        "google_auth_oauthlib": "google-auth-oauthlib",
        "googleapiclient": "google-api-python-client",
        "vertexai": "google-cloud-aiplatform"
    }
    
    missing = []
    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
            log(f"✓ {package_name} - 已安裝", "OK")
        except ImportError:
            log(f"✗ {package_name} - 未安裝", "ERROR")
            missing.append(package_name)
    
    if missing:
        log("需要安裝缺少的套件:", "WARN")
        log(f"pip install {' '.join(missing)}", "INFO")
        return False
    
    return True


def setup_google_workspace_config() -> bool:
    """建立 Google Workspace 配置檔案"""
    log("建立 Google Workspace 配置檔案...", "STEP")
    
    config = {
        "version": "5.1.0",
        "project_id": PROJECT_ID,
        "oauth": {
            "client_id": OAUTH_CLIENT_ID,
            "app_name": OAUTH_APP_NAME,
            "credentials_file": str(GOOGLE_CREDENTIALS.relative_to(BASE_DIR)),
            "token_file": str(GOOGLE_TOKEN.relative_to(BASE_DIR)),
            "scopes": [
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/documents",
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/gmail.send",
                "https://www.googleapis.com/auth/calendar"
            ]
        },
        "service_account": {
            "email": SERVICE_ACCOUNT_EMAIL,
            "key_file": str(SERVICE_ACCOUNT_KEY.relative_to(BASE_DIR))
        },
        "apis": {
            "enabled": REQUIRED_APIS,
            "drive": {
                "api_version": "v3",
                "enabled": True
            },
            "docs": {
                "api_version": "v1",
                "enabled": True
            },
            "sheets": {
                "api_version": "v4",
                "enabled": True
            },
            "gmail": {
                "api_version": "v1",
                "enabled": True
            },
            "calendar": {
                "api_version": "v3",
                "enabled": True
            },
            "vertex_ai": {
                "enabled": True,
                "region": "us-central1"
            }
        },
        "authorization": {
            "authorized_by": "江政隆 F1247717117",
            "organization": "五常非營利組織",
            "google_for_nonprofits": True
        },
        "features": {
            "image_upload": True,
            "ai_image_generation": True,
            "image_analysis": True,
            "text_processing": True,
            "google_workspace_integration": True
        }
    }
    
    config_file = BASE_DIR / "config" / "google_workspace_config.json"
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        log(f"✓ 配置檔案已建立: {config_file}", "OK")
        return True
    except Exception as e:
        log(f"✗ 建立配置檔案失敗: {e}", "ERROR")
        return False


def create_oauth_setup_script() -> bool:
    """建立 OAuth 設定腳本"""
    log("建立 OAuth 設定腳本...", "STEP")
    
    script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
complete_authorization_and_setup.py

執行 Google OAuth 授權流程
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
GOOGLE_CREDENTIALS = BASE_DIR / "google_credentials.json"
GOOGLE_TOKEN = BASE_DIR / "google_token.json"

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
except ImportError:
    print("❌ 缺少必要的 Google API 套件")
    print("請執行: pip install google-auth google-auth-oauthlib")
    sys.exit(1)

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar'
]

def main():
    print("=" * 70)
    print("Google Workspace OAuth 授權流程")
    print("=" * 70)
    print()
    
    if not GOOGLE_CREDENTIALS.exists():
        print(f"❌ 憑證檔案不存在: {{GOOGLE_CREDENTIALS}}")
        print("請先從 Google Cloud Console 下載憑證檔案")
        return
    
    creds = None
    
    # 檢查是否有已儲存的 token
    if GOOGLE_TOKEN.exists():
        try:
            with open(GOOGLE_TOKEN, 'r', encoding='utf-8') as token:
                creds = Credentials.from_authorized_user_info(
                    json.load(token), SCOPES)
            print("✓ 已載入儲存的認證資訊")
        except:
            pass
    
    # 如果沒有有效的認證，進行 OAuth 流程
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("✓ 已重新整理認證資訊")
            except:
                creds = None
        
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(GOOGLE_CREDENTIALS), SCOPES)
            creds = flow.run_local_server(port=0)
            print("✓ OAuth 認證成功")
        
        # 儲存認證資訊
        with open(GOOGLE_TOKEN, 'w', encoding='utf-8') as token:
            token.write(creds.to_json())
        print("✓ 已儲存認證資訊")
    
    print()
    print("✅ 授權完成！")

if __name__ == "__main__":
    import json
    main()
'''
    
    script_file = BASE_DIR / "scripts" / "complete_authorization_and_setup.py"
    
    try:
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        log(f"✓ OAuth 設定腳本已建立: {script_file}", "OK")
        return True
    except Exception as e:
        log(f"✗ 建立腳本失敗: {e}", "ERROR")
        return False


def create_api_check_script() -> bool:
    """建立 API 狀態檢查腳本"""
    log("建立 API 狀態檢查腳本...", "STEP")
    
    script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_google_apis_status.py

檢查 Google Workspace APIs 啟用狀態
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

REQUIRED_APIS = {json.dumps(REQUIRED_APIS, indent=2, ensure_ascii=False)}

def check_api_status():
    """檢查 API 啟用狀態"""
    print("=" * 70)
    print("Google Workspace APIs 狀態檢查")
    print("=" * 70)
    print()
    
    print("需要啟用的 API:")
    for api in REQUIRED_APIS:
        print(f"  - {{api}}")
    
    print()
    print("檢查方式:")
    print("1. 前往: https://console.cloud.google.com/apis/library")
    print("2. 搜尋每個 API 名稱")
    print("3. 確認是否已啟用")
    print()
    print("或使用 gcloud CLI:")
    for api in REQUIRED_APIS:
        print(f"  gcloud services enable {{api}}")

if __name__ == "__main__":
    check_api_status()
'''
    
    script_file = BASE_DIR / "scripts" / "check_google_apis_status.py"
    
    try:
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        log(f"✓ API 檢查腳本已建立: {script_file}", "OK")
        return True
    except Exception as e:
        log(f"✗ 建立腳本失敗: {e}", "ERROR")
        return False


def generate_setup_report(results: Dict) -> bool:
    """產生設定報告"""
    log("產生設定報告...", "STEP")
    
    report = {
        "setup_time": str(Path(__file__).stat().st_mtime),
        "results": results,
        "next_steps": [],
        "status": "incomplete"
    }
    
    if results.get("authorization_docs"):
        report["next_steps"].append("✓ 授權文件已檢查")
    else:
        report["next_steps"].append("✗ 需要檢查授權文件")
    
    if results.get("credentials"):
        report["next_steps"].append("✓ Google OAuth 憑證已設定")
    else:
        report["next_steps"].append("⚠ 需要下載 Google OAuth 憑證")
    
    if results.get("service_account"):
        report["next_steps"].append("✓ 服務帳戶已設定")
    else:
        report["next_steps"].append("⚠ 需要下載服務帳戶金鑰")
    
    if results.get("python_packages"):
        report["next_steps"].append("✓ Python 套件已安裝")
    else:
        report["next_steps"].append("✗ 需要安裝 Python 套件")
    
    if results.get("config"):
        report["next_steps"].append("✓ 配置檔案已建立")
    else:
        report["next_steps"].append("✗ 配置檔案建立失敗")
    
    if all([results.get("authorization_docs"), 
            results.get("credentials", False) or results.get("config"),
            results.get("python_packages", False)]):
        report["status"] = "ready"
    
    report_file = BASE_DIR / "reports" / "google_workspace_auto_setup_report.json"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        log(f"✓ 設定報告已產生: {report_file}", "OK")
        return True
    except Exception as e:
        log(f"✗ 產生報告失敗: {e}", "ERROR")
        return False


def main():
    """主程式"""
    print("=" * 100)
    print("Google Workspace 應用軟體全自動設定工具")
    print("根據授權文件自動設定 Google Workspace 整合")
    print("=" * 100)
    print()
    
    results = {}
    
    # 步驟 1: 檢查授權文件
    results["authorization_docs"] = check_authorization_documents()
    print()
    
    # 步驟 2: 檢查 Python 套件
    results["python_packages"] = check_python_packages()
    print()
    
    # 步驟 3: 檢查 Google OAuth 憑證
    results["credentials"] = check_google_credentials()
    print()
    
    # 步驟 4: 檢查服務帳戶
    results["service_account"] = check_service_account()
    print()
    
    # 步驟 5: 建立配置檔案
    results["config"] = setup_google_workspace_config()
    print()
    
    # 步驟 6: 建立 OAuth 設定腳本
    results["oauth_script"] = create_oauth_setup_script()
    print()
    
    # 步驟 7: 建立 API 檢查腳本
    results["api_script"] = create_api_check_script()
    print()
    
    # 步驟 8: 產生設定報告
    results["report"] = generate_setup_report(results)
    print()
    
    # 總結
    print("=" * 100)
    print("設定總結")
    print("=" * 100)
    print()
    
    for name, status in results.items():
        icon = "✅" if status else "⚠️"
        print(f"{icon} {name}: {'完成' if status else '需要手動完成'}")
    
    print()
    
    # 下一步建議
    if not all(results.values()):
        log("部分設定需要手動完成，請參考以下建議：", "WARN")
        print()
        
        if not results.get("python_packages"):
            log("1. 安裝缺少的 Python 套件", "INFO")
            log("   pip install google-auth google-auth-oauthlib google-api-python-client google-cloud-aiplatform", "INFO")
            print()
        
        if not results.get("credentials"):
            log("2. 下載 Google OAuth 憑證", "INFO")
            log("   前往: https://console.cloud.google.com/apis/credentials", "INFO")
            log(f"   尋找: {OAUTH_APP_NAME}", "INFO")
            log(f"   客戶端 ID: {OAUTH_CLIENT_ID}", "INFO")
            log("   下載後儲存為: google_credentials.json", "INFO")
            print()
        
        if not results.get("service_account"):
            log("3. 下載服務帳戶金鑰", "INFO")
            log("   前往: https://console.cloud.google.com/iam-admin/serviceaccounts", "INFO")
            log(f"   服務帳戶: {SERVICE_ACCOUNT_EMAIL}", "INFO")
            log("   下載後儲存為: config/gcp/littlej-sa.json", "INFO")
            print()
        
        log("4. 執行 OAuth 授權流程", "INFO")
        log("   python scripts/complete_authorization_and_setup.py", "INFO")
        print()
    else:
        log("所有設定已完成！可以開始使用 Google Workspace 功能", "OK")
        print()
        log("下一步：執行 OAuth 授權流程", "INFO")
        log("python scripts/complete_authorization_and_setup.py", "INFO")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程式已中斷")
        sys.exit(0)
    except Exception as e:
        log(f"發生未預期的錯誤: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)
