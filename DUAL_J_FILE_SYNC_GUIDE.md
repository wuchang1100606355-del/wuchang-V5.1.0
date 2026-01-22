# 雙J協作檔案同步指南

## 📋 概述

雙J協作檔案同步系統用於將本機新增的檔案同步到伺服器，並自動將本機DNS替換為伺服器DNS。

## 🎯 核心功能

1. **自動識別新增檔案**：從 Git 狀態自動識別本機新增的檔案
2. **DNS自動替換**：將所有本機DNS替換為伺服器DNS
3. **安全同步**：使用 `safe_sync_push.py` 進行安全同步（包含健康檢查）
4. **雙J協作**：地端小J識別檔案，雲端小J執行同步
5. **工作日誌**：自動記錄雙J工作日誌

## 🔄 DNS 替換規則

### 基本替換
- `127.0.0.1` → `wuchang.life`
- `localhost` → `wuchang.life`
- `192.168.50.84` → `wuchang.life`

### HTTP/HTTPS 替換
- `http://127.0.0.1` → `https://wuchang.life`
- `http://localhost` → `https://wuchang.life`
- `https://127.0.0.1` → `https://wuchang.life`

### 端口替換（保留端口號）
- `127.0.0.1:8788` → `wuchang.life:8788`
- `localhost:5000` → `wuchang.life:5000`

### 特定服務對應
- `http://127.0.0.1:8788` → `https://admin.wuchang.life`
- `http://127.0.0.1:5000` → `https://ui.wuchang.life`
- `http://127.0.0.1:8069` → `https://odoo.wuchang.life`

## 💻 使用方式

### 基本使用（自動識別新增檔案）

```bash
python dual_j_file_sync_with_dns_replace.py
```

### 指定檔案列表

```bash
python dual_j_file_sync_with_dns_replace.py --files router_full_control.py property_management_router_integration.py
```

### 模擬執行（不實際同步）

```bash
python dual_j_file_sync_with_dns_replace.py --dry-run
```

### 指定伺服器目錄

```bash
python dual_j_file_sync_with_dns_replace.py --server-dir "\\\\SERVER\\share\\wuchang"
```

### 指定健康檢查 URL

```bash
python dual_j_file_sync_with_dns_replace.py --health-url "https://wuchang.life/health"
```

## 🔧 環境變數

- `WUCHANG_COPY_TO`：伺服器目錄（SMB 分享或掛載磁碟路徑）
- `WUCHANG_HEALTH_URL`：伺服器健康檢查 URL
- `WUCHANG_SERVER_URL`：伺服器 URL（預設：`https://wuchang.life`）

## 📡 API 使用

### 透過 local_control_center API

```bash
curl -X POST http://127.0.0.1:8788/api/dual_j/file_sync \
  -H "Content-Type: application/json" \
  -d '{
    "files": ["router_full_control.py", "property_management_router_integration.py"],
    "server_dir": "\\\\SERVER\\share\\wuchang",
    "health_url": "https://wuchang.life/health",
    "dry_run": false
  }'
```

## 📝 工作流程

1. **地端小J**：
   - 識別需要同步的檔案（從 Git 或指定列表）
   - 掃描檔案資訊（大小、雜湊值、修改時間）
   - 記錄工作日誌

2. **DNS替換**：
   - 讀取每個檔案內容
   - 根據替換規則替換DNS
   - 儲存到臨時目錄

3. **雲端小J**：
   - 使用 `safe_sync_push.py` 進行安全同步
   - 執行伺服器健康檢查
   - 推送檔案到伺服器
   - 記錄工作日誌

4. **報告生成**：
   - 生成同步報告（JSON 格式）
   - 記錄替換的DNS數量
   - 記錄成功/失敗的檔案

## 📊 同步報告

同步完成後會生成報告檔案：
- 檔案名稱：`dual_j_sync_report_YYYYMMDD_HHMMSS.json`
- 包含內容：
  - 同步時間
  - 檔案列表
  - DNS替換統計
  - 同步結果（成功/失敗）

## ⚠️ 注意事項

1. **排除檔案**：以下檔案和目錄會被自動排除：
   - `.git`, `__pycache__`, `.pyc`
   - `node_modules`, `.venv`, `venv`
   - `certs/`, `*.pem`, `*.key`
   - `google_credentials.json`, `google_token.json`
   - `router_config.json`

2. **安全檢查**：同步前會執行伺服器健康檢查，如果伺服器無回應會中止同步

3. **檔案類型**：只有特定類型的檔案會進行DNS替換：
   - `.py`, `.md`, `.html`, `.json`, `.txt`
   - `.yml`, `.yaml`, `.conf`, `.cfg`, `.ini`

4. **備份**：建議在同步前先備份伺服器檔案

## 🔗 相關檔案

- `dual_j_file_sync_with_dns_replace.py` - 主程式
- `safe_sync_push.py` - 安全同步工具
- `dual_j_work_log.py` - 工作日誌系統
- `local_control_center.py` - API 端點

## 📅 文檔建立日期

2026-01-22
