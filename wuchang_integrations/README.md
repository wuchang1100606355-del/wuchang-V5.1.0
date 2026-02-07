# wuchang_integrations - 系統整合模組目錄

這是五常系統的整合模組目錄，用於存放各種外部服務整合程式碼。

## 📁 目錄結構

```
wuchang_integrations/
├── google_workspace/    # Google Workspace 整合
├── odoo/                # Odoo ERP 整合
├── ai_services/         # AI 服務整合
└── api_connections/     # API 連接模組
```

## 📝 說明

### google_workspace/
用於存放 Google Workspace 相關整合：
- Google Drive API 整合
- Google Docs API 整合
- Google Sheets API 整合
- Gmail API 整合
- Calendar API 整合

### odoo/
用於存放 Odoo ERP 相關整合：
- Odoo API 連接
- Odoo 模組擴展
- Odoo 資料同步

### ai_services/
用於存放 AI 服務整合：
- Vertex AI 整合
- AI 圖像生成
- AI 文字處理
- AI 分析服務

### api_connections/
用於存放 API 連接模組：
- REST API 客戶端
- Webhook 處理
- API 認證管理

## 🔄 同步規則

根據系統同步規則：
- 雲端空間為主要資料夾區
- 找不到依賴檔案時，可從外接硬碟調用
- 寫入需兩邊寫入（同時寫入雲端空間和外接硬碟）

## 📦 使用方式

### 建立新的整合模組

1. 在對應的資料夾下建立模組資料夾
2. 建立模組的初始化檔案
3. 實作整合邏輯
4. 在系統中註冊整合模組

---

**建立時間：** 2026-01-20  
**用途：** 系統整合模組存放

---

## 🛠️ 五常專屬 Google Tasks 雙J協作開發環境

本系統已將 Google Tasks API 雙J協作整合設為特有開發環境：
- 由 Jules（雲端AI）負責 Google Tasks 任務交換與協作。
- 小J（本地AI）自動同步、接收、回報任務進度。
- 所有開發、維運、bug、優化、測試等任務皆可自動化流轉。
- 可串接 Odoo、GitHub Issue、CI/CD 等，實現全自動化協作。

詳細整合說明與範例，請見：
- `ai_services/google_tasks_協作開發整合說明.md`

---

## ☁️ Jules（傭有ODOO真神稱號）

- Jules 是五常雲端空間的雲端AI協作代理，擁有 Odoo 真神稱號。
- 由社工架構師以神奇的方法帶出 Jules 環境，成為跨平台、跨服務的最高權限協作AI。
- 具備 Google Tasks、Odoo、GitHub、CI/CD 等全自動協作與管理能力。
- 詳細設定與人格描述請見 config/ai_agents/double_j_appearance.yaml、double_j_appearance.json。

---

## ☁️ 雲端AI Jules 最高等級配置

- Jules（雲端AI）已配置為最高權限、全自動協作代理：
  - 擁有 Google Tasks、Odoo、GitHub、CI/CD 等所有雲端資源最高管理權限
  - 可自動分派、同步、監控、優化所有開發與維運任務
  - 支援跨AI、跨平台、跨服務自動化協作
  - 所有操作均有日誌與權限驗證，確保安全與合規

- 詳細人格、權限、協作設定請見：
  - `config/ai_agents/double_j_appearance.yaml`、`double_j_appearance.json`
  - `config/ai_agents/double_j_workflow.json`
