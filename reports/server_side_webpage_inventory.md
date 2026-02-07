# 伺服器端網頁檔案清單

**更新時間**：2026-01-15  
**搜尋範圍**：伺服器端應用程式、API 路由、文檔提及的伺服器端網頁

---

## 一、伺服器端應用程式分析

### 1.1 本機中控台（Local Control Center）

**檔案**：`local_control_center.py`  
**類型**：HTTP 伺服器（BaseHTTPRequestHandler）  
**綁定**：`127.0.0.1:8788`（僅本機訪問）

**提供的 HTML 頁面**：
- ✅ `wuchang_control_center.html` - 本機中控台 UI
  - **路由**：`GET /`
  - **用途**：兩機（本機/伺服器）互動狀態監控
  - **狀態**：✅ 存在於地端

**API 端點**（JSON，非 HTML）：
- `/api/local/health` - 本機健康檢查
- `/api/server/health` - 伺服器健康檢查
- `/api/dns/expected` - DNS 預期值
- `/api/dns/acme_status` - ACME 驗證狀態
- 等多個 API 端點...

---

### 1.2 小 J Hub 伺服器（Little J Hub Server）

**檔案**：`little_j_hub_server.py`  
**類型**：HTTP 伺服器（BaseHTTPRequestHandler）  
**綁定**：`127.0.0.1:8799`（預設）

**提供的 HTML 頁面**：
- ❌ **無 HTML 頁面**（純 API 伺服器）

**API 端點**（JSON）：
- `GET /health` - 健康檢查
- `GET /api/hub/server/info` - 伺服器資訊
- `GET /api/hub/server/architecture` - 系統架構
- `GET /api/hub/jobs/list` - 工作列表
- `GET /api/hub/jobs/get` - 取得工作
- `POST /api/hub/jobs/submit` - 提交工作
- `POST /api/hub/jobs/confirm` - 確認工作
- `POST /api/hub/jobs/archive` - 歸檔工作
- `POST /api/hub/server/reports/generate` - 生成伺服器報告

---

### 1.3 社區數據 API（Community Data API）

**檔案**：`api_community_data.py`  
**類型**：Flask Blueprint  
**狀態**：需掛載到主 Flask 應用程式

**提供的 HTML 頁面**：
- ❌ **無 HTML 頁面**（純 API）

**API 端點**（JSON）：
- `/api/community/demographics` - 人口結構數據
- `/api/community/commercial` - 商業生態數據
- `/api/community/transportation` - 交通物流數據
- `/api/community/happiness-coin` - 幸福幣配置
- `/api/community/optimization` - 系統優化建議
- `/api/community/location` - 地理邊界和街道
- `/api/community/insights` - 關鍵洞察
- `/api/community/summary` - 社區數據摘要
- `/api/community/knowledge-base` - 知識庫原始 JSON
- `/api/community/knowledge/index` - 知識庫索引
- `/api/community/knowledge/search` - 知識庫搜尋

**備註**：此 Blueprint 需要掛載到主 Flask 應用程式（如 `web_ui.py`）才能使用。

---

### 1.4 示範安全確認伺服器（Demo Security ACK Server）

**檔案**：`demo_security_ack_server.py`  
**類型**：HTTP 伺服器（示範用）

**提供的 HTML 頁面**：
- ⚠️ **可能提供 HTML**（需檢查完整檔案）

**狀態**：示範用途，可能不適合生產環境

---

## 二、文檔提及但未找到的伺服器端檔案

### 2.1 `web_ui.py` ❌

**提及位置**：
- `MAP_3D_INTEGRATION.md` - 提到需要在此檔案中註冊路由
- `WUCHANG_COMMUNITY_ANALYSIS.md` - 提到 `/wuchang-community` 路由
- `SYSTEM_INVENTORY.md` - 提到主系統在其他 repo/主機

**預期功能**：
- Flask 主應用程式
- 註冊 Blueprint（`api_community_data.py`、`map_api_routes.py` 等）
- 提供 HTML 頁面路由：
  - `/wuchang-community` - 社區分析儀表板
  - `/map-3d-viewer` - 3D 地圖查看器

**狀態**：❌ 未找到（可能在其他 repo 或主機）

---

### 2.2 `map_api_routes.py` ❌

**提及位置**：`MAP_3D_INTEGRATION.md`

**預期功能**：
- Flask Blueprint
- 地圖 API 路由：
  - `POST /api/map/download` - 下載地圖瓦片
  - `GET /api/map/query` - 查詢地圖
  - `POST /api/map/clear-cache` - 清除緩存

**狀態**：❌ 未找到

---

### 2.3 `map_3d_viewer.html` ❌

**提及位置**：
- `MAP_3D_INTEGRATION.md` - 3D 地圖查看器
- `WUCHANG_COMMUNITY_ANALYSIS.md` - 地圖查看器

**預期路由**：`/map-3d-viewer`（由 `web_ui.py` 提供）

**狀態**：❌ 未找到（可能在其他位置或需要創建）

---

### 2.4 `responsive_ui_module.py` ❌

**提及位置**：`MAP_3D_INTEGRATION.md`

**預期功能**：
- 響應式 UI 模組
- 三顯示器模式支援
- 中間顯示器包含 3D 地圖查看器

**狀態**：❌ 未找到

---

## 三、伺服器端網頁路由推測

### 3.1 預期路由（基於文檔推測）

假設 `web_ui.py` 存在，預期提供以下路由：

| 路由 | 方法 | 用途 | HTML 檔案 |
|------|------|------|----------|
| `/` | GET | 首頁 | `index.html`（待創建） |
| `/wuchang-community` | GET | 社區分析儀表板 | `wuchang_community_dashboard.html` |
| `/map-3d-viewer` | GET | 3D 地圖查看器 | `map_3d_viewer.html`（未找到） |
| `/system-architecture` | GET | 系統架構圖 | `system_architecture.html` |

### 3.2 API 路由（已確認存在）

| 路由前綴 | Blueprint | 狀態 |
|---------|----------|------|
| `/api/community/*` | `api_community_data.py` | ✅ 存在（需掛載） |
| `/api/map/*` | `map_api_routes.py` | ❌ 未找到 |
| `/api/upload/avatar` | `upload_avatar_api.py` | ✅ 存在（需掛載） |

---

## 四、伺服器端架構推測

### 4.1 主系統位置

根據 `SYSTEM_INVENTORY.md` 和 `AGENT_CONSTITUTION.md`：

> 本 workspace 主要是 **UI/輔助模組、資料檔、說明文件、路由器/網路診斷工具**。  
> 目前未見完整後端主程式入口（例如 Flask 主 app、部署腳本、Dockerfile/compose、CI workflow 等）。  
> 若實際系統已部署，通常代表「主系統」在其他 repo/其他主機。

**推測**：
- 主 Flask 應用程式（`web_ui.py`）可能位於：
  - 其他 Git repository
  - 伺服器主機上（`220.135.21.74`、`35.185.167.23`、`35.201.170.114`、`104.199.144.93`）
  - Docker 容器內

### 4.2 部署架構推測

根據 DNS 記錄和系統架構：

```
wuchang.life (根域名)
├── 220.135.21.74 (路由器/店內側)
│   ├── www.wuchang.life
│   ├── shop.wuchang.life
│   └── ui.wuchang.life
├── 35.185.167.23 (Google Cloud)
│   └── odoo.wuchang.life
├── 35.201.170.114 (Google Cloud)
│   ├── core.wuchang.life
│   ├── admin.wuchang.life
│   └── verify.wuchang.life
└── 104.199.144.93 (Google Cloud)
    ├── pm.wuchang.life
    └── pos.wuchang.life
```

**推測的伺服器端網頁位置**：
- `www.wuchang.life` → 可能由 `220.135.21.74` 上的 Web 伺服器提供
- 各子網域可能由對應的 Google Cloud 實例提供

---

## 五、已確認的伺服器端網頁檔案

### 5.1 地端檔案（可部署到伺服器）

| 檔案 | 位置 | 用途 | 狀態 |
|------|------|------|------|
| `wuchang_community_dashboard.html` | 根目錄 | 社區分析儀表板 | ✅ 存在 |
| `system_architecture.html` | 根目錄 | 系統架構圖 | ✅ 存在 |
| `wuchang_control_center.html` | 根目錄 | 本機中控台 | ✅ 存在 |
| `static/little_j_white_hair_placeholder.html` | static/ | 頭像佔位符 | ✅ 存在 |

### 5.2 伺服器端程式碼提供的頁面

| 程式碼檔案 | 提供的 HTML | 路由 | 狀態 |
|-----------|------------|------|------|
| `local_control_center.py` | `wuchang_control_center.html` | `GET /` | ✅ 確認 |
| `web_ui.py` | 多個頁面 | 未知 | ❌ 未找到 |
| `little_j_hub_server.py` | 無 | - | ✅ 確認（純 API） |

---

## 六、伺服器端網頁檔案總結

### 6.1 已找到的伺服器端網頁

**本機伺服器**（`local_control_center.py`）：
- ✅ `wuchang_control_center.html` - 本機中控台

**地端檔案**（可部署到伺服器）：
- ✅ `wuchang_community_dashboard.html` - 社區儀表板
- ✅ `system_architecture.html` - 系統架構圖
- ✅ `static/little_j_white_hair_placeholder.html` - 頭像佔位符

### 6.2 未找到的伺服器端檔案

- ❌ `web_ui.py` - Flask 主應用程式
- ❌ `map_api_routes.py` - 地圖 API Blueprint
- ❌ `map_3d_viewer.html` - 3D 地圖查看器
- ❌ `responsive_ui_module.py` - 響應式 UI 模組
- ❌ `index.html` - 首頁（待創建）

### 6.3 伺服器端架構推測

**主系統位置**：可能在其他 repository 或伺服器主機上

**建議**：
1. 確認主 Flask 應用程式（`web_ui.py`）的位置
2. 確認伺服器端部署架構
3. 確認各子網域的 Web 伺服器配置
4. 如需創建首頁，可基於 `wuchang_community_dashboard.html` 改進

---

## 七、下一步建議

1. ✅ **已完成**：搜尋地端和本機伺服器端的網頁檔案
2. ⏳ **待確認**：確認主系統（`web_ui.py`）的位置
3. ⏳ **待確認**：檢查伺服器主機上的實際部署檔案
4. ⏳ **待執行**：如需創建首頁，可基於現有檔案改進

---

**備註**：本清單基於 workspace 內的檔案和文檔推測。實際伺服器端部署可能包含額外的檔案和配置。
