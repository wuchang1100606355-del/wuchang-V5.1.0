#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_multimedia_text_image_features.py

根據授權文件設定本系統圖文功能

功能：
- 設定 Google OAuth 憑證（根據 LITTLE_J_CREDENTIALS_SETUP.md）
- 設定圖文功能（根據 MULTIMEDIA_AI_FEATURES.md）
  - 圖片上傳功能
  - AI 圖像生成（Vertex AI Imagen）
  - 圖片分析（Vertex AI Vision）
  - 文字處理功能
  - Google Workspace 整合
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, Optional

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

# 必要檔案路徑
GOOGLE_CREDENTIALS = BASE_DIR / "google_credentials.json"
GOOGLE_TOKEN = BASE_DIR / "google_token.json"
SERVICE_ACCOUNT_KEY = BASE_DIR / "config" / "gcp" / "littlej-sa.json"
UPLOADS_DIR = BASE_DIR / "uploads"
CONTAINERS_UPLOADS = BASE_DIR / "containers" / "uploads"


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


def check_authorization_documents():
    """檢查授權文件"""
    log("檢查授權文件...", "STEP")
    print()
    
    results = {
        "doc1": False,
        "doc2": False
    }
    
    if AUTH_DOC_1.exists():
        log(f"✓ 授權文件 1 存在: {AUTH_DOC_1.name}", "OK")
        results["doc1"] = True
    else:
        log(f"✗ 授權文件 1 缺失: {AUTH_DOC_1.name}", "ERROR")
    
    if AUTH_DOC_2.exists():
        log(f"✓ 授權文件 2 存在: {AUTH_DOC_2.name}", "OK")
        results["doc2"] = True
    else:
        log(f"✗ 授權文件 2 缺失: {AUTH_DOC_2.name}", "ERROR")
    
    print()
    return all(results.values())


def setup_google_credentials():
    """設定 Google OAuth 憑證（根據 LITTLE_J_CREDENTIALS_SETUP.md）"""
    log("設定 Google OAuth 憑證...", "STEP")
    print()
    
    # 檢查憑證檔案
    if GOOGLE_CREDENTIALS.exists():
        log(f"✓ Google 憑證檔案已存在: {GOOGLE_CREDENTIALS}", "OK")
        try:
            with open(GOOGLE_CREDENTIALS, 'r', encoding='utf-8') as f:
                creds = json.load(f)
                if "installed" in creds or "web" in creds:
                    log("✓ 憑證格式正確", "OK")
                    return True
                else:
                    log("⚠ 憑證格式可能有問題", "WARN")
        except Exception as e:
            log(f"✗ 讀取憑證檔案失敗: {e}", "ERROR")
            return False
    else:
        log(f"⚠ Google 憑證檔案不存在: {GOOGLE_CREDENTIALS}", "WARN")
        log("需要從 Google Cloud Console 下載憑證檔案", "INFO")
        log("OAuth 用戶端 ID: Wuchang-life", "INFO")
        log("客戶端 ID: 581281764864-4eg0icu55pkmbcirheflhp7fgt7gk499.apps.googleusercontent.com", "INFO")
        log("下載後請複製到專案根目錄並命名為: google_credentials.json", "INFO")
        return False
    
    print()


def setup_service_account():
    """設定服務帳戶（用於 Google Workspace APIs）"""
    log("檢查服務帳戶設定...", "STEP")
    print()
    
    # 建立 config/gcp 目錄
    service_account_dir = SERVICE_ACCOUNT_KEY.parent
    service_account_dir.mkdir(parents=True, exist_ok=True)
    log(f"✓ 服務帳戶目錄已建立: {service_account_dir}", "OK")
    
    if SERVICE_ACCOUNT_KEY.exists():
        log(f"✓ 服務帳戶金鑰已存在: {SERVICE_ACCOUNT_KEY}", "OK")
        return True
    else:
        log(f"⚠ 服務帳戶金鑰不存在: {SERVICE_ACCOUNT_KEY}", "WARN")
        log("需要從 GCP Console 下載服務帳戶金鑰", "INFO")
        log("服務帳戶名稱: littlej-sa", "INFO")
        log("下載後請儲存到: config/gcp/littlej-sa.json", "INFO")
        return False
    
    print()


def setup_uploads_directory():
    """設定上傳資料夾（圖片、文字檔案）"""
    log("設定上傳資料夾...", "STEP")
    print()
    
    # 建立主要上傳資料夾
    if not UPLOADS_DIR.exists():
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        log(f"✓ 已建立上傳資料夾: {UPLOADS_DIR}", "OK")
    else:
        log(f"✓ 上傳資料夾已存在: {UPLOADS_DIR}", "OK")
    
    # 建立子資料夾
    subdirs = ["images", "text", "generated"]
    for subdir in subdirs:
        subdir_path = UPLOADS_DIR / subdir
        if not subdir_path.exists():
            subdir_path.mkdir(parents=True, exist_ok=True)
            log(f"✓ 已建立子資料夾: {subdir_path.name}", "OK")
    
    # 建立容器上傳資料夾
    if not CONTAINERS_UPLOADS.exists():
        CONTAINERS_UPLOADS.mkdir(parents=True, exist_ok=True)
        log(f"✓ 已建立容器上傳資料夾: {CONTAINERS_UPLOADS}", "OK")
    
    print()
    return True


def check_python_packages():
    """檢查必要的 Python 套件"""
    log("檢查 Python 套件...", "STEP")
    print()
    
    required_packages = {
        "google.oauth2": "google-auth",
        "google_auth_oauthlib": "google-auth-oauthlib",
        "googleapiclient": "google-api-python-client",
        "vertexai": "google-cloud-aiplatform"
    }
    
    missing_packages = []
    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
            log(f"✓ {package_name} - 已安裝", "OK")
        except ImportError:
            log(f"✗ {package_name} - 未安裝", "ERROR")
            missing_packages.append(package_name)
    
    if missing_packages:
        log("", "WARN")
        log("缺少以下套件，請執行安裝：", "WARN")
        log(f"pip install {' '.join(missing_packages)}", "INFO")
        print()
        return False
    
    print()
    return True


def create_image_text_config():
    """建立圖文功能配置檔案"""
    log("建立圖文功能配置檔案...", "STEP")
    print()
    
    config = {
        "version": "5.1.0",
        "features": {
            "image_upload": {
                "enabled": True,
                "supported_formats": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
                "max_size_mb": 10,
                "upload_directory": str(UPLOADS_DIR / "images"),
                "vertex_ai_vision": {
                    "enabled": True,
                    "model": "imagetext@001"
                }
            },
            "text_upload": {
                "enabled": True,
                "supported_formats": [".txt", ".pdf", ".docx"],
                "upload_directory": str(UPLOADS_DIR / "text")
            },
            "ai_image_generation": {
                "enabled": True,
                "model": "imagegeneration@006",
                "output_directory": str(UPLOADS_DIR / "generated"),
                "default_format": "png"
            },
            "google_workspace": {
                "enabled": True,
                "services": {
                    "drive": {
                        "enabled": True,
                        "api_version": "v3"
                    },
                    "docs": {
                        "enabled": True,
                        "api_version": "v1"
                    },
                    "sheets": {
                        "enabled": True,
                        "api_version": "v4"
                    }
                }
            }
        },
        "authorization": {
            "authorized_by": "江政隆 F1247717117",
            "organization": "五常非營利組織",
            "google_for_nonprofits": True
        }
    }
    
    config_file = BASE_DIR / "config" / "multimedia_text_image_config.json"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        log(f"✓ 配置檔案已建立: {config_file}", "OK")
        print()
        return True
    except Exception as e:
        log(f"✗ 建立配置檔案失敗: {e}", "ERROR")
        print()
        return False


def generate_setup_summary():
    """產生設定摘要"""
    log("產生設定摘要...", "STEP")
    print()
    
    summary = {
        "setup_time": str(Path(__file__).stat().st_mtime),
        "authorization_documents": {
            "doc1": AUTH_DOC_1.exists(),
            "doc2": AUTH_DOC_2.exists()
        },
        "google_credentials": GOOGLE_CREDENTIALS.exists(),
        "service_account": SERVICE_ACCOUNT_KEY.exists(),
        "uploads_directory": UPLOADS_DIR.exists(),
        "config_file": (BASE_DIR / "config" / "multimedia_text_image_config.json").exists()
    }
    
    summary_file = BASE_DIR / "reports" / "multimedia_text_image_setup_summary.json"
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        log(f"✓ 設定摘要已儲存: {summary_file}", "OK")
        print()
        return True
    except Exception as e:
        log(f"✗ 儲存設定摘要失敗: {e}", "ERROR")
        print()
        return False


def main():
    """主程式"""
    print("=" * 100)
    print("本系統圖文功能設定工具")
    print("根據授權文件設定圖像與文字處理功能")
    print("=" * 100)
    print()
    
    # 檢查授權文件
    if not check_authorization_documents():
        log("授權文件不完整，無法繼續", "ERROR")
        return
    
    # 步驟 1: 檢查 Python 套件
    packages_ok = check_python_packages()
    
    # 步驟 2: 設定 Google OAuth 憑證
    credentials_ok = setup_google_credentials()
    
    # 步驟 3: 設定服務帳戶
    service_account_ok = setup_service_account()
    
    # 步驟 4: 設定上傳資料夾
    uploads_ok = setup_uploads_directory()
    
    # 步驟 5: 建立配置檔案
    config_ok = create_image_text_config()
    
    # 步驟 6: 產生設定摘要
    summary_ok = generate_setup_summary()
    
    # 總結
    print("=" * 100)
    print("設定總結")
    print("=" * 100)
    print()
    
    results = {
        "授權文件": True,
        "Python 套件": packages_ok,
        "Google OAuth 憑證": credentials_ok,
        "服務帳戶": service_account_ok,
        "上傳資料夾": uploads_ok,
        "配置檔案": config_ok,
        "設定摘要": summary_ok
    }
    
    for name, status in results.items():
        icon = "✅" if status else "⚠️"
        print(f"{icon} {name}: {'完成' if status else '需要手動設定'}")
    
    print()
    
    # 下一步建議
    if not all(results.values()):
        log("部分設定需要手動完成，請參考以下建議：", "WARN")
        print()
        
        if not packages_ok:
            log("1. 安裝缺少的 Python 套件", "INFO")
            log("   pip install google-auth google-auth-oauthlib google-api-python-client google-cloud-aiplatform", "INFO")
            print()
        
        if not credentials_ok:
            log("2. 下載 Google OAuth 憑證", "INFO")
            log("   前往: https://console.cloud.google.com/apis/credentials", "INFO")
            log("   下載 OAuth 用戶端 ID: Wuchang-life", "INFO")
            log("   儲存為: google_credentials.json", "INFO")
            print()
        
        if not service_account_ok:
            log("3. 下載服務帳戶金鑰", "INFO")
            log("   服務帳戶: littlej-sa", "INFO")
            log("   儲存為: config/gcp/littlej-sa.json", "INFO")
            print()
    else:
        log("所有設定已完成！可以開始使用圖文功能", "OK")
        print()
        log("功能說明：", "INFO")
        log("- 圖片上傳: 支援 .jpg, .png, .gif, .bmp 格式", "INFO")
        log("- AI 圖像生成: 使用 Vertex AI Imagen", "INFO")
        log("- 圖片分析: 使用 Vertex AI Vision", "INFO")
        log("- 文字處理: 支援 .txt, .pdf, .docx 格式", "INFO")
        log("- Google Workspace 整合: Drive, Docs, Sheets", "INFO")


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


---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:05:03
---
