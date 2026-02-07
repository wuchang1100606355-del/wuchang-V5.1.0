#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_google_cloud_nonprofit_credits.py

Google Cloud 非營利帳號抵免額開通

功能：
- 檢查 Google for Nonprofits 狀態
- 檢查 Google Cloud 帳戶狀態
- 協助申請非營利組織抵免額
- 驗證抵免額開通狀態
"""

import sys
import os
import json
import webbrowser
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent

# Google Cloud 配置
PROJECT_ID = "my-j-483304"
ORGANIZATION_NAME = "五常非營利組織"
COUNTRY = "台灣"

# 非營利相關 URL
GOOGLE_NONPROFITS_URL = "https://www.google.com/nonprofits"
GOOGLE_CLOUD_CREDITS_URL = "https://cloud.google.com/apply-for-nonprofit-credits"
GOOGLE_CLOUD_CONSOLE = f"https://console.cloud.google.com/billing?project={PROJECT_ID}"


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌",
        "STEP": "📋",
        "LINK": "🔗"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")


def check_google_nonprofits_status() -> Dict:
    """檢查 Google for Nonprofits 狀態"""
    log("檢查 Google for Nonprofits 狀態...", "STEP")
    print()
    
    status = {
        "verified": False,
        "notes": []
    }
    
    log("Google for Nonprofits 驗證狀態：需要手動檢查", "WARN")
    log(f"組織名稱：{ORGANIZATION_NAME}", "INFO")
    log(f"國家：{COUNTRY}", "INFO")
    
    status["notes"].append({
        "check": "Google for Nonprofits 驗證",
        "action": "前往 https://www.google.com/nonprofits 檢查驗證狀態",
        "required_documents": [
            "台灣內政部立案證明",
            "組織章程",
            "最近年度財務報表"
        ]
    })
    
    print()
    return status


def check_billing_account() -> Dict:
    """檢查 Google Cloud 帳單帳戶"""
    log("檢查 Google Cloud 帳單帳戶...", "STEP")
    print()
    
    billing_status = {
        "has_billing": False,
        "credits_applied": False,
        "notes": []
    }
    
    log("帳單帳戶狀態：需要手動檢查", "WARN")
    log(f"專案 ID：{PROJECT_ID}", "INFO")
    
    billing_status["notes"].append({
        "check": "Google Cloud 帳單帳戶",
        "action": f"前往 {GOOGLE_CLOUD_CONSOLE} 檢查帳單設定",
        "requirements": [
            "需要連結帳單帳戶",
            "申請非營利組織抵免額",
            "驗證組織身分"
        ]
    })
    
    print()
    return billing_status


def generate_nonprofit_application_guide() -> str:
    """產生非營利組織抵免額申請指南"""
    guide = f"""
# Google Cloud 非營利帳號抵免額開通指南

## 📋 申請資格

**組織資訊：**
- 組織名稱：{ORGANIZATION_NAME}
- 國家：{COUNTRY}
- 專案 ID：{PROJECT_ID}

**申請資格要求：**
1. ✅ 必須是合法的非營利組織
2. ✅ 必須通過 Google for Nonprofits 驗證
3. ✅ 必須有內政部立案證明（台灣）
4. ✅ 必須符合 Google Cloud 非營利組織政策

---

## 🚀 開通步驟

### 步驟 1：確認 Google for Nonprofits 狀態

1. **前往 Google for Nonprofits**
   - 網址：{GOOGLE_NONPROFITS_URL}
   - 檢查組織驗證狀態
   - 確認已通過驗證

2. **驗證所需文件**
   - ✅ 台灣內政部立案證明
   - ✅ 組織章程
   - ✅ 最近年度財務報表
   - ✅ 稅務登記證（如適用）

### 步驟 2：申請 Google Cloud 非營利組織抵免額

1. **前往申請頁面**
   - 網址：{GOOGLE_CLOUD_CREDITS_URL}
   - 或：https://support.google.com/nonprofits/answer/10266332

2. **填寫申請表單**
   - 組織名稱：{ORGANIZATION_NAME}
   - 組織類型：非營利組織
   - 國家/地區：台灣
   - Google Cloud 專案 ID：{PROJECT_ID}
   - 說明使用目的

3. **提交驗證文件**
   - 上傳內政部立案證明
   - 上傳組織章程
   - 上傳其他必要文件

### 步驟 3：連結帳單帳戶

1. **前往 Google Cloud Console**
   - 網址：{GOOGLE_CLOUD_CONSOLE}
   - 登入 Google Cloud Console

2. **設定帳單帳戶**
   - 前往：帳單 > 連結帳單帳戶
   - 建立或連結帳單帳戶
   - 選擇付款方式

3. **申請抵免額**
   - 前往：帳單 > 帳單帳戶 > 抵免額
   - 申請非營利組織抵免額
   - 提供組織驗證資訊

### 步驟 4：等待審核

- **審核時間：** 通常 7-14 個工作天
- **審核通知：** 會透過電子郵件通知
- **審核結果：** 可前往 Google Cloud Console 查看

### 步驟 5：驗證抵免額開通

1. **檢查抵免額狀態**
   - 前往：Google Cloud Console > 帳單 > 帳單帳戶
   - 查看抵免額狀態

2. **確認抵免額金額**
   - 非營利組織每月可獲得 $350 美元抵免額
   - 可用於 Google Cloud 服務

---

## 💰 抵免額詳情

### Google Cloud 非營利組織抵免額

- **每月抵免額：** $350 美元
- **適用服務：** 所有 Google Cloud 服務
- **使用期限：** 每月更新
- **累積限制：** 不累積，每月重置

### 可使用抵免額的服務

1. ✅ **Compute Engine** - 虛擬機器
2. ✅ **Cloud Storage** - 雲端儲存
3. ✅ **Cloud SQL** - 資料庫服務
4. ✅ **Cloud Functions** - 無伺服器函數
5. ✅ **Vertex AI** - AI/ML 服務
6. ✅ **Cloud Run** - 容器服務
7. ✅ **其他 Google Cloud 服務**

---

## 📝 申請表單資訊

### 組織資訊

- **組織名稱：** {ORGANIZATION_NAME}
- **組織類型：** 非營利組織
- **國家/地區：** 台灣
- **立案機關：** 內政部
- **立案證書編號：** （請填入實際編號）

### Google Cloud 專案資訊

- **專案 ID：** {PROJECT_ID}
- **專案名稱：** 五常系統
- **主要用途：** 
  - Odoo ERP 系統
  - 資料庫服務
  - AI 服務整合
  - Google Workspace 整合

### 使用目的說明

本組織使用 Google Cloud 服務的目的：
- 運行 Odoo ERP 系統，管理組織日常營運
- 提供資料庫服務，儲存組織資料
- 使用 AI 服務，提升工作效率
- 整合 Google Workspace，優化協作流程
- 提供雲端儲存，確保資料安全

---

## ✅ 檢查清單

### 申請前檢查

- [ ] Google for Nonprofits 已通過驗證
- [ ] 已準備所有必要文件
- [ ] Google Cloud 專案已建立
- [ ] 帳單帳戶已設定

### 申請時需要

- [ ] 組織基本資訊
- [ ] Google Cloud 專案 ID
- [ ] 使用目的說明
- [ ] 驗證文件（已上傳）

### 申請後檢查

- [ ] 已收到申請確認郵件
- [ ] 定期檢查審核狀態
- [ ] 審核通過後驗證抵免額

---

## 🔗 相關連結

- **Google for Nonprofits：** {GOOGLE_NONPROFITS_URL}
- **抵免額申請：** {GOOGLE_CLOUD_CREDITS_URL}
- **Google Cloud Console：** {GOOGLE_CLOUD_CONSOLE}
- **帳單管理：** https://console.cloud.google.com/billing
- **支援文件：** https://support.google.com/nonprofits

---

## 📞 聯絡資訊

如有問題，可聯絡：
- Google for Nonprofits 支援：https://support.google.com/nonprofits
- Google Cloud 支援：https://cloud.google.com/support

---

**建立時間：** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**組織：** {ORGANIZATION_NAME}  
**專案：** {PROJECT_ID}

"""
    return guide


def open_application_links():
    """開啟申請相關連結"""
    log("準備開啟申請連結...", "STEP")
    print()
    
    links = [
        ("Google for Nonprofits", GOOGLE_NONPROFITS_URL),
        ("Google Cloud 抵免額申請", GOOGLE_CLOUD_CREDITS_URL),
        ("Google Cloud Console", GOOGLE_CLOUD_CONSOLE)
    ]
    
    log("將開啟以下連結：", "INFO")
    for name, url in links:
        log(f"  - {name}: {url}", "LINK")
    
    print()
    
    try:
        # 詢問是否開啟瀏覽器
        response = input("是否要開啟瀏覽器前往申請頁面？(y/n): ").strip().lower()
        if response == 'y':
            for name, url in links:
                log(f"正在開啟: {name}", "INFO")
                webbrowser.open(url)
                import time
                time.sleep(1)
            log("已開啟所有連結", "OK")
        else:
            log("已跳過自動開啟", "INFO")
            log("請手動前往申請頁面", "WARN")
    except Exception as e:
        log(f"無法自動開啟瀏覽器: {e}", "WARN")
        log("請手動前往申請頁面", "INFO")


def main():
    """主程式"""
    print("=" * 100)
    print("Google Cloud 非營利帳號抵免額開通")
    print("=" * 100)
    print()
    
    # 步驟 1: 檢查 Google for Nonprofits 狀態
    nonprofits_status = check_google_nonprofits_status()
    
    # 步驟 2: 檢查帳單帳戶
    billing_status = check_billing_account()
    
    # 步驟 3: 產生申請指南
    log("產生申請指南...", "STEP")
    guide = generate_nonprofit_application_guide()
    
    guide_file = BASE_DIR / "reports" / "GOOGLE_CLOUD_NONPROFIT_CREDITS_GUIDE.md"
    guide_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide)
        log(f"✓ 申請指南已產生: {guide_file}", "OK")
    except Exception as e:
        log(f"✗ 產生指南失敗: {e}", "ERROR")
    
    print()
    
    # 步驟 4: 開啟申請連結
    open_application_links()
    
    print()
    print("=" * 100)
    print("開通流程總結")
    print("=" * 100)
    print()
    
    log("需要完成的步驟：", "STEP")
    print()
    print("1. ✅ 確認 Google for Nonprofits 已通過驗證")
    print("2. ✅ 準備組織驗證文件")
    print("3. ✅ 前往申請頁面填寫表單")
    print("4. ✅ 連結 Google Cloud 帳單帳戶")
    print("5. ✅ 等待審核（7-14 個工作天）")
    print("6. ✅ 驗證抵免額開通")
    print()
    
    log("詳細申請指南已儲存至：", "INFO")
    log(f"  {guide_file}", "LINK")
    print()
    
    log("重要提醒：", "WARN")
    log("- 申請需要提供組織驗證文件", "INFO")
    log("- 審核時間約 7-14 個工作天", "INFO")
    log("- 每月可獲得 $350 美元抵免額", "INFO")
    log("- 抵免額不累積，每月重置", "INFO")


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
