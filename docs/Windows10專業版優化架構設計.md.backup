# Windows 10 專業版優化架構設計

**設計日期**：2026-01-11  
**系統版本**：Windows 10 專業版  
**合規要求**：符合 Google 非營利組織合規要求

---

## 📊 系統掃描結果

### 已啟用的 Windows 功能

✅ **核心功能**：
- **WSL (Windows Subsystem for Linux)** - 已啟用
- **VirtualMachinePlatform** - 已啟用（支持 WSL2 和 Hyper-V）
- **OpenSSH Client** - 已安裝
- **OpenSSH Server** - 已安裝
- **RSAT 工具套件** - 已安裝（遠程服務器管理工具）

✅ **Docker 環境**：
- Docker Desktop 29.1.3 運行中
- WSL2 後端（docker-desktop）
- 8 CPU 核心
- 3.772 GiB 總內存

### Google 非營利組織資源

✅ **Google Workspace 非營利版**（免費）：
- 每位使用者 5 TB 儲存空間
- 無限制使用者數量
- 專業電子郵件服務（@wuchang.life）
- Google Meet、文件、日曆等協作工具

✅ **Google Grants 廣告計劃**（免費）：
- 每月 $10,000 USD 廣告額度
- 用於推廣社區活動和志工招募

✅ **Google Cloud Platform**（免費額度）：
- Always Free 層級服務
- Compute Engine、Cloud Storage、Cloud Functions 等
- 需申請補助計劃以獲得額外信用額度

📋 **詳細資訊**：請參考 `docs/Google非營利組織資源整合設計.md`

---

## 🏗️ 優化架構設計

### 架構層次

```
┌─────────────────────────────────────────────────────────┐
│  應用層 (Application Layer)                              │
│  - Odoo Web (wuchang-web)                               │
│  - Caddy 反向代理                                        │
│  - 監控服務 (Uptime Kuma, Portainer)                    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  容器編排層 (Orchestration Layer)                        │
│  - Docker Compose (統一管理)                             │
│  - WSL2 後端 (穩定運行環境)                              │
│  - 健康檢查和自動重啟                                    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  自動化層 (Automation Layer)                            │
│  - Windows 任務計劃程序 (定時任務)                       │
│  - PowerShell 自動化腳本                                 │
│  - 系統服務監控                                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  基礎設施層 (Infrastructure Layer)                       │
│  - Windows 10 專業版                                     │
│  - WSL2 (Linux 容器運行環境)                             │
│  - Docker Desktop                                        │
│  - OpenSSH (遠程管理)                                     │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 核心優化方案

### 1. 利用 WSL2 優化容器運行

#### 優勢
- ✅ **性能提升**：WSL2 使用真正的 Linux 內核，性能接近原生 Linux
- ✅ **資源隔離**：更好的資源管理和隔離
- ✅ **穩定性**：減少 Windows 和 Linux 之間的兼容性問題

#### 實施方案

**優化 Docker Compose 配置**：
- 使用 WSL2 作為 Docker 後端（已配置）
- 優化卷掛載路徑（使用 WSL2 路徑）
- 配置資源限制

**創建 WSL2 優化配置**：

```yaml
# docker-compose.optimized.yml
version: '3.8'

services:
  wuchang-web:
    # ... 現有配置 ...
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 2G
        reservations:
          cpus: '2'
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8069/web/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

### 2. Windows 服務層自動化

#### 利用 Windows 任務計劃程序

**統一任務管理架構**：

```
任務層次結構：
├─ 系統級任務（每小時）
│  ├─ WuchangAutoComplianceCheck（合規檢查）
│  ├─ WuchangHourlyDeploymentCheck（部署檢查）
│  └─ WuchangHealthMonitor（健康監控）
│
├─ 維護級任務（每日）
│  ├─ DNSDailyCheck（DNS 檢查）
│  ├─ IntegrityDailyCheck（完整性檢查）
│  └─ BackupDaily（每日備份）
│
└─ 監控級任務（每 15 分鐘）
   └─ DNSHealMonitor（DNS 修復監控）
```

#### 創建統一任務管理器

**`scripts/wuchang_task_manager.ps1`**：
- 統一管理所有定時任務
- 任務依賴關係管理
- 任務執行狀態監控
- 自動故障恢復

---

### 3. 系統服務監控和自動恢復

#### 利用 Windows 服務監控

**創建 Windows 服務監控腳本**：

監控以下服務：
- Docker Desktop 服務
- WSL 服務
- OpenSSH 服務（如啟用）

**自動恢復機制**：
- 檢測服務停止 → 自動啟動
- 檢測容器停止 → 自動重啟
- 檢測網絡問題 → 自動修復

---

### 4. 利用 OpenSSH 進行遠程管理

#### 配置 OpenSSH Server

**優勢**：
- ✅ 安全的遠程訪問
- ✅ 跨平台兼容
- ✅ 無需額外軟件

**實施方案**：
- 配置 OpenSSH Server
- 設置密鑰認證
- 配置防火牆規則
- 創建遠程管理腳本

---

### 5. 利用 RSAT 工具進行系統管理

#### 可用的 RSAT 工具

**網絡管理**：
- DNS 管理工具
- DHCP 管理工具
- 網絡負載平衡工具

**系統管理**：
- Active Directory 工具
- 群組原則管理
- 遠程桌面服務

**實施方案**：
- 創建 DNS 自動配置腳本
- 利用 DHCP 工具進行 IP 管理
- 配置群組原則進行安全設置

---

### 6. 店內固定IP與路由器功能整合

#### 架構概述

整合店內固定IP管理和路由器功能，實現統一的網絡管理系統。

**網絡架構**：
```
┌─────────────────────────────────────────────────────────┐
│  路由器層 (Router Layer)                                 │
│  - 路由器 IP: 192.168.50.1                              │
│  - DHCP 服務                                              │
│  - 端口轉發管理                                           │
│  - NAT 功能                                              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  固定IP設備層 (Static IP Devices)                        │
│  ├─ 主機 (LUNGsMSI): 192.168.50.84                      │
│  ├─ POS設備 (POS-PC): 192.168.50.88                     │
│  └─ 服務器 (Server): 192.168.50.249                     │
└─────────────────────────────────────────────────────────┘
```

#### 固定IP配置管理

**店內設備固定IP分配**：

| 設備名稱 | IP地址 | 用途 | 配置方式 |
|---------|--------|------|---------|
| LUNGsMSI | 192.168.50.84 | 主機工作站 | PowerShell腳本 |
| POS-PC | 192.168.50.88 | POS終端設備 | PowerShell腳本 |
| Server | 192.168.50.249 | 服務器主機 | PowerShell腳本 |
| Router | 192.168.50.1 | 路由器閘道 | 設備默認 |

**固定IP配置腳本**：
- `scripts/set_static_ip_50_84.ps1` - 主機IP配置
- `scripts/set_fixed_ip.ps1` - 通用固定IP配置

#### 路由器功能整合

**路由器管理功能**：

1. **狀態監控**：
   - 路由器連線狀態檢查
   - 端口可用性檢測
   - Web管理界面訪問
   - DNS解析功能檢查
   - 實施腳本：`scripts/audit_router_status.ps1`

2. **端口轉發管理**：
   - HTTP (80) → 192.168.50.249:80
   - HTTPS (443) → 192.168.50.249:443
   - Odoo (8069) → 192.168.50.249:8069 (可選)
   - 實施腳本：`scripts/router_relay_handshake.py`

3. **DHCP綁定建議**：
   - MAC地址與IP綁定（防止IP衝突）
   - DHCP保留配置
   - 設備自動發現和登記

4. **中繼功能**：
   - 路由器中繼握手
   - 外網訪問通道
   - 實施腳本：`scripts/router_relay_handshake.py`

#### 整合實施方案

**統一管理腳本架構**：

創建 `scripts/wuchang_network_manager.ps1`：
- 統一管理所有固定IP配置
- 路由器狀態監控和診斷
- 端口轉發規則管理
- DHCP綁定建議生成
- 網絡拓撲圖生成

**配置文件**：

```
config/
├─ network/
│  ├─ static_ips.json（固定IP配置）
│  ├─ router_config.json（路由器配置）
│  └─ port_forwarding.json（端口轉發規則）
```

**固定IP配置範例** (`config/network/static_ips.json`)：

```json
{
  "devices": [
    {
      "name": "LUNGsMSI",
      "ip": "192.168.50.84",
      "subnet": "24",
      "gateway": "192.168.50.1",
      "dns": ["192.168.50.1", "8.8.8.8"],
      "interface": "Wi-Fi",
      "purpose": "主機工作站"
    },
    {
      "name": "POS-PC",
      "ip": "192.168.50.88",
      "subnet": "24",
      "gateway": "192.168.50.1",
      "dns": ["192.168.50.1", "8.8.8.8"],
      "purpose": "POS終端設備"
    },
    {
      "name": "Server",
      "ip": "192.168.50.249",
      "subnet": "24",
      "gateway": "192.168.50.1",
      "dns": ["192.168.50.1", "8.8.8.8"],
      "purpose": "服務器主機"
    }
  ]
}
```

**路由器配置範例** (`config/network/router_config.json`)：

```json
{
  "router": {
    "ip": "192.168.50.1",
    "admin_port": 80,
    "admin_port_https": 8443,
    "username": "admin",
    "type": "ASUS"
  },
  "port_forwarding": [
    {
      "name": "HTTP",
      "external_port": 80,
      "internal_ip": "192.168.50.249",
      "internal_port": 80,
      "protocol": "TCP",
      "enabled": true
    },
    {
      "name": "HTTPS",
      "external_port": 443,
      "internal_ip": "192.168.50.249",
      "internal_port": 443,
      "protocol": "TCP",
      "enabled": true
    }
  ]
}
```

#### 優勢

**統一管理**：
- ✅ 所有網絡配置集中管理
- ✅ 固定IP配置標準化
- ✅ 路由器功能統一控制

**自動化**：
- ✅ IP配置自動化腳本
- ✅ 路由器狀態自動監控
- ✅ 網絡拓撲自動發現

**穩定性**：
- ✅ 固定IP防止地址衝突
- ✅ DHCP綁定確保設備穩定
- ✅ 路由器狀態監控及時發現問題

---

### 7. 容器健康監控和自動恢復

#### 增強的健康檢查

**多層次健康檢查**：

1. **容器級別**：
   - Docker 健康檢查
   - 容器狀態監控
   - 自動重啟機制

2. **應用級別**：
   - HTTP 健康檢查端點
   - 數據庫連接檢查
   - 服務依賴檢查

3. **系統級別**：
   - Windows 服務狀態
   - 資源使用監控
   - 網絡連接檢查

---

### 8. Google Workspace 深度整合與運用

#### 架構概述

將所有設定與 Google Workspace 高度對齊，運用 Google 非營利組織提供的免費資源，讓「五常小J智慧五常社區雲系統」具備強大功能。

**整合架構**：
```
┌─────────────────────────────────────────────────────────┐
│  Odoo 應用層                                              │
│  ├─ 會議管理系統 → Google Meet                           │
│  ├─ 公文系統 → Google 表單 + AI 生成                     │
│  └─ 產品圖管理 → Canva 非營利版                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Google Workspace API 整合層                             │
│  ├─ Google Calendar API (會議排程)                       │
│  ├─ Google Meet API (視訊會議)                           │
│  ├─ Google Forms API (表單系統)                          │
│  └─ Google Drive API (文件儲存)                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Google 非營利組織資源層                                  │
│  ├─ Google Workspace 非營利版（免費）                    │
│  ├─ Google Meet（100人/24小時）                          │
│  ├─ Google 雲端硬碟（5TB/使用者）                        │
│  └─ Canva 非營利版（設計工具）                            │
└─────────────────────────────────────────────────────────┘
```

#### 1. Odoo 會議系統與 Google Meet 整合

**功能設計**：

所有 Odoo 內建的會議功能都自動整合 Google Meet，利用 Google 非營利組織提供的免費視訊功能。

**整合功能**：

1. **自動建立 Google Meet 連結**：
   - 在 Odoo 建立會議時，自動呼叫 Google Calendar API 建立 Google Meet 連結
   - 會議連結自動加入會議記錄
   - 參與者可直接從 Odoo 一鍵加入視訊會議

2. **會議排程同步**：
   - Odoo 會議自動同步到 Google Calendar
   - 參與者會收到 Google Calendar 邀請
   - 支援會議提醒和通知

3. **會議記錄整合**：
   - Google Meet 錄製功能（15 GB 儲存空間）
   - 會議錄影自動儲存到 Google Drive
   - 在 Odoo 中可直接查看會議錄影連結

**實作模組**：

**`wuchang_os/addons/wuchang_google_integration/models/meeting_google_meet.py`**：
- 會議建立時自動呼叫 Google Calendar API
- 建立 Google Meet 連結
- 同步會議資訊到 Google Calendar

**配置範例**：
```python
# 會議模型整合
class WuchangMeeting(models.Model):
    _inherit = 'calendar.event'
    
    google_meet_link = fields.Char('Google Meet 連結')
    google_calendar_id = fields.Char('Google Calendar ID')
    auto_join_meet = fields.Boolean('自動加入 Meet', default=True)
    
    def action_create_google_meet(self):
        # 自動建立 Google Meet 連結
        google_service = self._get_google_service()
        meet_link = google_service.create_meet_link(self)
        self.write({'google_meet_link': meet_link})
```

**Google Meet 資源規格（非營利版）**：
- ✅ 每次會議最多 **100 位參與者**
- ✅ 會議時長：**24 小時**（無限制）
- ✅ 錄製功能：**15 GB** 儲存空間
- ✅ 完全免費，符合非營利組織資格

---

#### 2. AI 驅動的公文生成系統（基於 Google 表單）

**功能設計**：

運用 Google 非營利組織提供的 Google 表單功能，結合 AI 技術，建立智慧公文生成系統。

**系統架構**：

1. **問答式公文設計**：
   - 使用 Google 表單建立公文範本
   - AI 分析問答內容，自動生成正式公文
   - 支援多種公文類型（公告、通知、決議等）

2. **AI 公文生成流程**：
   ```
   使用者填寫 Google 表單 
   → AI 分析問答內容 
   → 套用公文範本 
   → 生成正式公文 
   → 儲存到 Google Drive 
   → 同步到 Odoo 公文系統
   ```

3. **智慧功能**：
   - AI 自動識別公文類型
   - 自動填入必要欄位
   - 智慧校對和格式調整
   - 多語言支援（繁體中文、英文）

**實作模組**：

**`wuchang_os/addons/wuchang_google_integration/models/document_ai.py`**：
- Google 表單回應處理
- AI 公文生成引擎
- Google Drive 文件管理

**配置範例**：
```python
class WuchangDocumentAI(models.Model):
    _name = 'wuchang.document.ai'
    
    google_form_id = fields.Char('Google 表單 ID')
    form_responses = fields.Text('表單回應')
    generated_document = fields.Many2one('documents.document', '生成文件')
    ai_prompt = fields.Text('AI 提示詞')
    
    def action_generate_document(self):
        # 1. 從 Google 表單取得回應
        responses = self._get_google_form_responses()
        
        # 2. AI 分析並生成公文
        document_content = self._ai_generate_document(responses)
        
        # 3. 儲存到 Google Drive
        google_doc = self._save_to_google_drive(document_content)
        
        # 4. 同步到 Odoo
        self._sync_to_odoo(google_doc)
```

**Google 表單資源規格（非營利版）**：
- ✅ 無限制表單數量
- ✅ 無限制回應數量
- ✅ 自動儲存到 Google 雲端硬碟（5TB/使用者）
- ✅ 完全免費

---

#### 3. 商家產品圖生成系統（基於 Canva 非營利版）

**功能設計**：

運用 Canva 非營利版提供的設計工具，為商家自動生成專業產品圖。

**系統架構**：

1. **產品圖自動生成**：
   - 商家上傳產品資訊（名稱、價格、描述等）
   - 系統自動呼叫 Canva API 生成產品圖
   - 支援多種設計範本（商品圖、促銷圖、海報等）

2. **AI 輔助設計**：
   - AI 自動選擇適合的設計範本
   - 自動調整文字大小和位置
   - 智慧配色建議
   - 品牌一致性管理

3. **批次處理**：
   - 支援大量產品批次生成
   - 自動優化圖片尺寸
   - 多格式匯出（PNG、JPG、PDF）

**實作模組**：

**`wuchang_os/addons/wuchang_canva_integration/models/product_image.py`**：
- Canva API 整合
- 產品圖生成引擎
- 圖片管理系統

**配置範例**：
```python
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    canva_design_id = fields.Char('Canva 設計 ID')
    product_images = fields.One2many('product.image.canva', 'product_id')
    
    def action_generate_canva_image(self):
        # 1. 準備產品資訊
        product_data = self._prepare_canva_data()
        
        # 2. 呼叫 Canva API 生成圖片
        canva_service = self._get_canva_service()
        design = canva_service.create_design(product_data)
        
        # 3. 下載並儲存圖片
        image_url = canva_service.export_design(design['id'])
        self._save_product_image(image_url)
```

**Canva 非營利版資源規格**：
- ✅ 專業設計工具完整功能
- ✅ 無限制設計範本
- ✅ 品牌套件管理
- ✅ 高解析度匯出
- ✅ 符合非營利組織資格即可申請

---

#### 4. 整合配置管理

**統一配置文件**：

```
config/
├─ google_workspace/
│  ├─ credentials.json（Google API 憑證）
│  ├─ meet_config.json（Google Meet 配置）
│  ├─ forms_config.json（Google 表單配置）
│  └─ calendar_config.json（Google Calendar 配置）
├─ canva/
│  ├─ api_key.json（Canva API 金鑰）
│  └─ templates.json（設計範本配置）
└─ ai/
   ├─ document_ai_config.json（公文生成 AI 配置）
   └─ image_ai_config.json（圖片生成 AI 配置）
```

**Google Workspace API 設定**：

需要啟用的 API：
- ✅ Google Calendar API
- ✅ Google Meet API
- ✅ Google Forms API
- ✅ Google Drive API
- ✅ Google Docs API

**API 憑證配置**：
```json
{
  "type": "service_account",
  "project_id": "wuchang-npo-core",
  "private_key_id": "...",
  "private_key": "...",
  "client_email": "service-account@wuchang-npo-core.iam.gserviceaccount.com",
  "scopes": [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/meetings.space.created",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents"
  ]
}
```

---

#### 優勢與效益

**資源優勢**：
- ✅ **完全免費**：所有 Google Workspace 功能對非營利組織免費
- ✅ **無限制使用**：Google Meet 24 小時無限制、Google 表單無限制
- ✅ **高品質服務**：企業級功能和穩定性
- ✅ **整合便利**：透過 API 輕鬆整合到 Odoo

**功能優勢**：
- ✅ **智慧化**：AI 輔助公文生成和圖片設計
- ✅ **自動化**：會議、公文、圖片生成全自動
- ✅ **專業化**：企業級工具確保專業品質
- ✅ **整合化**：所有功能統一整合到 Odoo 系統

**合規優勢**：
- ✅ **符合規範**：所有功能均符合 Google 非營利組織使用條款
- ✅ **合規使用**：僅用於非營利目的和社區服務
- ✅ **資源追蹤**：完整的使用記錄和監控

---

### 9. 統一配置管理

#### 集中化配置

**配置層次**：
```
config/
├─ system/
│  ├─ docker-compose.yml（主配置）
│  ├─ docker-compose.optimized.yml（優化配置）
│  └─ caddy/
│     └─ Caddyfile
├─ automation/
│  ├─ tasks.json（任務配置）
│  └─ monitoring.json（監控配置）
└─ compliance/
   └─ google_nonprofit.json（合規配置）
```

---

## 📋 實施計劃

### 階段 1：基礎優化（立即實施）

1. ✅ **優化 Docker Compose 配置**
   - 添加資源限制
   - 添加健康檢查
   - 優化卷掛載

2. ✅ **統一任務管理**
   - 創建任務管理器腳本
   - 整合現有任務
   - 設置任務依賴

3. ✅ **增強監控**
   - 創建系統服務監控
   - 創建容器健康監控
   - 創建自動恢復機制

### 階段 2：進階優化（後續實施）

1. **WSL2 優化**
   - 優化 WSL2 配置
   - 配置資源分配
   - 優化網絡性能

2. **OpenSSH 配置**
   - 啟用 OpenSSH Server
   - 配置密鑰認證
   - 設置遠程管理

3. **RSAT 工具整合**
   - DNS 自動配置
   - 網絡管理自動化
   - 安全策略配置

4. ✅ **固定IP與路由器功能整合**
   - 創建統一網絡管理腳本
   - 配置固定IP管理系統
   - 路由器功能整合
   - 網絡配置集中管理

5. ✅ **Google Workspace 深度整合與運用**
   - Odoo 會議系統與 Google Meet 整合
   - AI 驅動的公文生成系統（基於 Google 表單）
   - 商家產品圖生成系統（基於 Canva 非營利版）
   - Google Workspace API 配置與整合

---

## 🔧 創建優化腳本

### 1. 統一任務管理器

**`scripts/wuchang_task_manager.ps1`**：
- 管理所有定時任務
- 任務狀態監控
- 自動故障恢復

### 2. 系統服務監控

**`scripts/wuchang_service_monitor.ps1`**：
- 監控 Docker 服務
- 監控 WSL 服務
- 自動恢復機制

### 3. 容器健康監控

**`scripts/wuchang_container_health.ps1`**：
- 容器狀態檢查
- 健康檢查執行
- 自動重啟機制

### 4. 優化 Docker Compose

**`docker-compose.optimized.yml`**：
- 資源限制配置
- 健康檢查配置
- 優化卷掛載

### 5. Google Workspace 整合模組

**`wuchang_os/addons/wuchang_google_integration/`**：
- Google Meet 會議整合
- Google Calendar 同步
- Google 表單處理
- Google Drive 文件管理

**`wuchang_os/addons/wuchang_canva_integration/`**：
- Canva API 整合
- 產品圖生成引擎
- 批次處理功能

**配置文件**：
- `config/google_workspace/credentials.json` - Google API 憑證
- `config/canva/api_key.json` - Canva API 金鑰
- `config/ai/document_ai_config.json` - 公文生成 AI 配置

---

## 📊 架構優勢

### 簡便性

- ✅ **統一管理**：所有任務通過一個管理器控制
- ✅ **自動化**：減少手動操作
- ✅ **標準化**：使用 Windows 標準工具

### 穩固性

- ✅ **多層次監控**：容器、應用、系統三層監控
- ✅ **自動恢復**：故障自動檢測和修復
- ✅ **資源管理**：防止資源耗盡
- ✅ **健康檢查**：主動發現問題

### 可擴展性

- ✅ **模組化設計**：易於添加新服務
- ✅ **配置驅動**：通過配置文件管理
- ✅ **標準接口**：使用標準協議和工具

---

## ✅ 合規聲明

**符合 Google 非營利組織合規要求**

- ✅ 所有優化均以合規為最高要件
- ✅ 僅使用必要的系統功能
- ✅ 保護系統穩定性和安全性
- ✅ 記錄所有操作以備審計

---

**下一步**：開始實施階段 1 的優化項目
