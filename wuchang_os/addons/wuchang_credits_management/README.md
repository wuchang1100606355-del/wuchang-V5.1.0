# Wuchang Credits Management Module

雙J協作機制 - Google Cloud 抵免額管理模組

## 功能特色

- ✅ 管理 Google Cloud Platform 抵免額
- ✅ 雙J協作配置（小J + Jules）
- ✅ 自動化抵免額應用
- ✅ 使用量監控和報告
- ✅ 到期提醒和警告
- ✅ Odoo 專案整合（my-j-483304）

## 安裝

1. 將模組放置在 `wuchang_os/addons/` 目錄下
2. 更新應用程式清單
3. 安裝模組

## 使用方式

1. 進入「抵免額管理」選單
2. 查看現有的抵免額記錄（已預設三個記錄）
3. 點擊「使用雙J協作配置」按鈕
4. 小J和Jules會協作完成配置任務

## 模組結構

```
wuchang_credits_management/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── gcp_credits.py          # 抵免額管理模型
│   └── double_j_collaboration.py # 雙J協作任務模型
├── views/
│   ├── credits_management_views.xml
│   └── menu_items.xml
├── security/
│   └── ir.model.access.csv
├── data/
│   └── double_j_collaboration_data.xml  # 預設抵免額數據
├── controllers/
│   ├── __init__.py
│   └── main.py
└── README.md
```

## 預設數據

模組安裝時會自動建立三個抵免額記錄：

1. **免費試用抵免額** - $8,334.55（6天後到期）⚠️
2. **Google Maps Platform** - $7,851/月（至 2027/02/01）
3. **Google Cloud 非營利** - $350/月（待審核）

所有記錄都與 Odoo 專案（my-j-483304）整合。

## 雙J協作機制

- **小J（本地）**：處理本地配置和驗證
- **Jules（雲端）**：處理雲端部署和整合
- **協作流程**：自動建立協作任務，共同完成配置

## 相關文檔

- `reports/ODOO_CREDITS_MODULE_INSTALLATION.md` - 完整安裝指南
- `reports/CREDITS_IDENTIFICATION_AND_USAGE_PLAN.md` - 抵免額使用策略
