# 五常社區服務系統 v5.1.0 - 統一架構藍圖

**系統定位**: 獨資社區服務平台（非單純商業 POS）  
**路由器角色**: 社區基礎設施核心節點  
**服務對象**: 五常社區全體居民與服務單位  
**創辦人視角**: 上帝視角 (God's Eye View) - 系統全局掌控
**系統所在地**: 192.168.50.84 (伺服器) & 192.168.50.1 (路由器) = 所有服務入口
**財務結構**: 自給自足的資金循環系統

---

## 🏛️ 系統總覽

### 核心理念

五常社區服務系統是一個**以人為本的數位社區基礎設施**，整合了：

-   🏠 物業管理
-   🛒 商業服務
-   ❤️ 照護系統
-   ♻️ 環保永續
-   👥 志願服務
-   💰 社區金融
-   🎯 社區競選
-   📚 知識管理
-   🤖 AI 協作

---

## 📊 系統模組總覽 (70+ 功能模組)

### 🎯 核心平台層 (Core Platform)

#### 1. **Wuchang Core** - 社區作業系統核心

```
模組路徑: wuchang_os/addons/wuchang_core/
功能範圍:
- 社區超級應用 (Community Super App)
- POS 延伸功能
- 背景服務管理
- 多租戶架構
- 角色權限系統 (RBAC)
```

#### 2. **Wuchang Design System** - 統一設計語言

```
模組路徑: wuchang_os/addons/wuchang_design_system/
功能範圍:
- UI 元件庫
- 主題系統
- 響應式佈局
- 無障礙設計
- 品牌識別系統
```

#### 3. **MuK Backend Theme** - 後台主題

```
模組路徑: wuchang_os/addons/muk_web/
功能範圍:
- 現代化後台介面
- 應用搜尋
- 應用欄
- 自訂樣式系統
```

---

### 🏠 物業管理模組 (Property Management)

#### 4. **Wuchang Property Toolkits**

```
模組路徑: wuchang_os/addons/wuchang_property_toolkits/
功能範圍:
- HOA (Home Owner Association) 網站
- 社區公告
- 設施預約
- 維修報修
- 繳費管理
- 住戶資料
```

---

### 🛒 商業服務模組 (Business Services)

#### 5. **Wuchang Business** - 商業引擎

```
模組路徑: wuchang_os/addons/wuchang_business/
功能範圍:
- POS 收銀系統
- 庫存管理
- 會員系統
- 優惠券/折扣
- 銷售報表
- 供應鏈管理
```

#### 6. **Wuchang Finance** - 財務管理

```
模組路徑: wuchang_os/addons/wuchang_finance/
功能範圍:
- 配額管理 (Quota System)
- 收支記錄
- 預算控制
- 財務報表
- 補助申請
- 審計追蹤
```

---

### ❤️ 照護與志工模組 (Care & Volunteer)

#### 7. **Wuchang Life** - 生活服務

```
模組路徑: wuchang_os/addons/wuchang_life/
功能範圍:
- 生活記錄
- 健康追蹤
- 照護排程
- 緊急聯絡
- 活動參與
```

#### 8. **Wuchang Volunteer** - 志工系統

```
模組路徑: wuchang_os/addons/wuchang_volunteer/
功能範圍:
- 志工招募
- 任務分派
- 時間銀行 (Time Bank)
- 巡邏路線規劃 (Topology Patrol)
- 服務時數統計
- 志工認證
```

#### 9. **Wuchang Award Coach** - 獎勵教練

```
模組路徑: wuchang_os/addons/wuchang_award_coach/
功能範圍:
- 成就系統
- 積分獎勵
- 遊戲化激勵
- 排行榜
- 徽章系統
```

---

### 🎯 社區民主模組 (Community Democracy)

#### 10. **Wuchang Community Campaign** - 社區競選

```
模組路徑: wuchang_os/addons/wuchang_community_campaign/
功能範圍:
- 許願樹 (Wish Tree)
- 投票系統
- 提案管理
- 民意調查
- 社區決策
- 小j AI Hub
```

---

### 🌐 Web 介面模組 (Web Portals)

#### 11. **Wuchang Web Portal** - 社區入口網

```
模組路徑: wuchang_os/addons/wuchang_web_portal/
功能範圍:
- 首頁
- 服務導覽
- 公告佈告欄
- 線上申請
- 會員中心
```

---

### 🛡️ 監督與合規模組 (Guardian & Compliance)

#### 12. **Wuchang Guardian** - 社區守護者

```
模組路徑: wuchang_os/addons/wuchang_guardian/
功能範圍:
- AI 監督機制
- 決策審查
- 倫理檢查
- 異常偵測
- 社區 AI Council
```

#### 13. **Wuchang UI Compliance** - 介面合規

```
模組路徑: wuchang_os/addons/wuchang_ui_compliance/
功能範圍:
- 無障礙檢查
- WCAG 合規
- 響應式驗證
- 跨瀏覽器測試
```

---

## 🤖 AI 與智慧服務層

### 14. **小 j 雙角色智慧核心**

```
檔案: vm_fastapi_main_dual_role.py
功能:
- 店家/架構師雙角色系統
- 語音交互 (STT/TTS)
- 決策日誌系統
- 本地 LLM (Ollama)
- 雲端備援 (Vertex AI)
- RBAC 權限控制
```

### 15. **學習與成長系統**

```
檔案群:
- sister_learning_engine.py (經驗記錄器)
- sister_growth_dashboard.py (成長追蹤)
- sister_ai_learning_integration.py (AI 邏輯整合)
- initialize_learning_system.py (系統初始化)

功能:
- 經驗記錄 (Experience Recorder)
- 知識庫 (Knowledge Base)
- 反饋收集 (Feedback Collector)
- 學習引擎 (Learning Engine)
- 成長儀表板 (Growth Dashboard)
- 性能評估 (Performance Evaluator)
```

### 16. **AI 記憶系統**

```
目錄: memory_store/
結構:
- experiences/ (經驗)
- knowledge/ (知識)
- feedback/ (反饋)
- evaluations/ (評估)
- growth_metrics/ (成長指標)
```

---

## 🌐 網路與基礎設施層

### 17. **路由器管理系統**

```
檔案: router_manager.py
功能:
- ASUS RT-BE86U 管理
- DHCP 租約管理
- 裝置上線偵測
- QoS 優化
- Wi-Fi 6E 配置
- 網路拓撲管理
- 頻寬監控
```

### 18. **網路服務**

```
路由器資訊:
- 型號: ASUS RT-BE86U
- IP: 192.168.50.1
- 網域: wuchang.life
- 主機名: RT-BE86U-7428.wuchang.life

服務:
- DHCP Server
- DNS Server
- NAT Gateway
- Firewall
- VPN Server (可選)
```

---

## 🖥️ 平台介面總覽

### Web 平台介面

#### 1. **社區入口網站**

```html
檔案: wuchang_homepage_google_style.html, wuchang_homepage_hq.html URL:
http://192.168.50.84:8080/ 功能: 社區首頁、服務導覽、公告
```

#### 2. **控制中心**

```html
檔案: control_center.html URL: /control_center 功能: 系統管理、監控儀表板
```

#### 3. **AI 介紹頁**

```html
檔案: ai_intro.html 功能: 小j AI 功能介紹、互動演示
```

#### 4. **雲端相簿**

```html
檔案: cloud_gallery.html 功能: 社區照片分享、活動記錄
```

#### 5. **桌面環境**

```html
檔案: desktop.html 功能: Web 桌面、應用快捷方式
```

#### 6. **翻譯工具**

```html
檔案: translator.html 功能: 多語言翻譯、無障礙溝通
```

#### 7. **數位看板**

```html
檔案: signage.html 功能: 公共資訊顯示、公告輪播
```

#### 8. **行程管理**

```html
檔案: schedule.html 功能: 社區活動排程、預約系統
```

#### 9. **動畫工作室**

```html
檔案: animation_studio.html 功能: 社區創作平台
```

---

### USB 啟動系統介面

```
目錄: USB_DRIVE_NEW/SYSTEM/
功能: 離線可攜式社區服務系統

包含:
- boot.html (啟動介面)
- desktop.html (桌面環境)
- control_center.html (控制中心)
- ai_intro.html (AI 服務)
- cloud_gallery.html (本地相簿)
- usb_view.html (USB 檔案瀏覽)
- translator.html (離線翻譯)
```

---

## 🔧 開發與部署工具

### 19. **部署管理器**

```python
檔案: workshop_deploy/deploy_manager.py
功能:
- 整合 VM 專案
- 非營利合規檢查
- 部署命令生成
- 環境配置
```

### 20. **VPN 自動化**

```python
檔案: vpn_automation/connect_vpn.py
功能:
- VPNGate 連接
- 自動重連
- IP 驗證
- 連線日誌
```

### 21. **知識同步代理**

```python
檔案: vm_deploy/knowledge_sync_agent.py
功能:
- Wuchang Guardian 思維生成
- 知識庫同步
- Vertex AI 整合
```

---

## 🗄️ 資料庫與儲存層

### 22. **PostgreSQL 資料庫**

```yaml
服務: Docker Compose
容器名: wuchangv510-db-1
埠: 5432
用途:
    - Odoo 資料庫
    - 社區資料
    - 交易記錄
    - 使用者資料
```

### 23. **本地檔案儲存**

```
結構:
五常社區服務系統/
├── 行政/ (公文、會議記錄)
├── 物業/ (設施、維修)
├── 商業/ (銷售、庫存)
├── 照護/ (健康、照護記錄)
├── 環保/ (回收、永續專案)
├── 個人文件資訊/ (居民私人檔案)
└── 相機上傳/ (社區活動照片)
```

---

## 🚀 API 端點總覽 (40+ 端點)

### 核心 API (vm_fastapi_main_dual_role.py)

#### 認證與授權

```
POST /auth/token - Token 生成
GET  /          - 健康檢查
```

#### LLM 與對話

```
POST /llm/chat  - 角色特定對話
```

#### 語音交互

```
POST /voice/recognize   - STT (語音轉文字)
POST /voice/synthesize  - TTS (文字轉語音)
POST /voice/command     - 完整語音流程
```

#### 裝置管理

```
GET  /devices           - 列出裝置
POST /devices/register  - 註冊裝置
POST /devices/heartbeat - 心跳檢測
```

#### 決策與審計

```
GET  /admin/decisions   - 決策日誌 (架構師)
GET  /admin/audit       - 審計報告 (架構師)
```

#### 路由器管理 (NEW)

```
GET  /router/status     - 路由器狀態
GET  /router/devices    - 連線裝置
GET  /router/topology   - 網路拓撲 (架構師)
POST /router/optimize   - 網路優化 (架構師)
```

#### 監控與儀表板

```
GET  /events            - SSE 事件流
GET  /dashboard         - 實時儀表板
```

---

### 技能與服務 API (vm_fastapi_main_new.py)

```
GET  /skills            - 列出可用技能
POST /skills/execute    - 執行技能

可用技能:
- translate (翻譯)
- summarize_form (表單摘要)
- compose_announcement (撰寫公告)
- triage (事件分流)
```

---

### 證書與認證 API

```
POST /certificate/issue - 發行證書
POST /visiting_card     - 接收名片
```

---

### 網路掃描 API

```
GET  /network/arp       - ARP 掃描
```

---

### 日誌與匯出 API

```
GET  /events/download   - 下載事件日誌 (JSON)
GET  /events/csv        - 匯出 CSV
```

---

## 🏗️ 系統架構分層

```
┌──────────────────────────────────────────────────────────────────┐
│                  創辦人上帝視角 (God's Eye View)                  │
│         掌控所有層級、決策所有重要事項、管理所有資金流             │
└──────────────────────────────────────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────────┐
│                     使用者介面層                                  │
│   Web Portal | POS | 行動 App | USB 系統 | 數位看板             │
│              (所有介面的數據流向創辦人位置)                       │
└──────────────────────────────────────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────────┐
│                     API 服務層                                   │
│  FastAPI (8080) | Odoo (8069) | 路由器 API                      │
│     位置: 192.168.50.84 (伺服器) - 所有服務交匯點               │
└──────────────────────────────────────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────────┐
│                     業務邏輯層                                   │
│  13 個 Odoo 模組 | AI 學習引擎 | 路由器管理器                    │
│        (地端供應者入口、資金自循環、AI 決策)                     │
└──────────────────────────────────────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────────┐
│                     AI 智慧層                                    │
│  Ollama (本地) | Vertex AI (雲端) | 小j 學習系統                 │
│    (創辦人策略驅動、決策審批層)                                  │
└──────────────────────────────────────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────────┐
│                     資料層                                       │
│  PostgreSQL | Memory Store | 社區檔案系統                        │
│    (完整數據記錄、創辦人決策依據)                                 │
└──────────────────────────────────────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────────┐
│                     基礎設施層                                   │
│   路由器 (192.168.50.1) 核心  |  伺服器 (192.168.50.84) 樞紐    │
│      (創辦人的網路邊界 & 地端供應者接入點)                        │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🌐 網路拓撲 (已納管)

```
                    ┌──────────────────┐
                    │   Internet /     │
                    │   外部網路       │
                    │ (雲端備援Vertex) │
                    └────────┬─────────┘
                             │
                    ┌────────▼──────────────┐
                    │ ASUS RT-BE86U         │
                    │ 192.168.50.1          │
                    │ 創辦人網路邊界        │
                    │ wuchang.life DNS      │
                    │ DHCP | NAT | FW | QoS │
                    └────────┬──────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼──────────┐ ┌▼─────────┐ ┌─▼──────┐
     │ 主伺服器          │ │ POS      │ │ 客顯   │
     │ 192.168.50.84     │ │.50.11    │ │.50.21  │
     │ FastAPI + Odoo    │ │          │ │        │
     │ AI 小j Core       │ │(受創辦人)│ │(受創)  │
     │ 決策執行樞紐      │ │掌控)     │ │        │
     │ 地端供應入口      │ │          │ │        │
     │ 資金流核心        │ │          │ │        │
     └───────────────────┘ └──────────┘ └────────┘
```

**網路邊界的含義**：

-   🚪 創辦人通過路由器掌控所有設備連接
-   💳 伺服器位置 = 所有社區服務的入口與出口
-   🔐 QoS 優先級完全由創辦人決定
-   🌐 外部網絡訪問權受創辦人管控

---

## 🔐 安全與權限架構

### 角色定義

#### 1. **店家 (MERCHANT)**

```
Token: merchant-demo-001, merchant-demo-002
權限:
- POS 營業操作
- 庫存查詢
- 銷售報表
- 會員管理
- 語音查詢
- 基本路由器狀態
```

#### 2. **架構師 (ARCHITECT)**

```
Token: architect-demo-001
權限:
- 全系統存取
- 決策審查
- 網路拓撲
- 路由器優化
- 系統配置
- AI 訓練管理
- 社區政策設計
```

#### 3. **居民 (RESIDENT)** - 待實作

```
權限:
- 社區公告瀏覽
- 設施預約
- 報修申請
- 活動報名
- 投票參與
```

#### 4. **志工 (VOLUNTEER)** - 待實作

```
權限:
- 任務查看
- 時數記錄
- 巡邏路線
- 活動簽到
```

---

## 📦 Docker 服務清單

```yaml
服務:
    - db (PostgreSQL 16)
    - web (Odoo 18)
    - ai_core (FastAPI)
    - ollama (本地 LLM)
    - nginx (反向代理 - 可選)
```

---

## 🎯 系統整合目標

### 短期目標 (1-2 週)

1. ✅ 路由器納管完成
2. ✅ 雙角色 API 整合完成
3. ⏳ Wi-Fi 優化為類乙太網路模式
4. ⏳ 所有 13 個 Odoo 模組測試
5. ⏳ AI 學習系統啟動

### 中期目標 (1-3 個月)

1. 完整部署到生產環境
2. 居民與志工角色上線
3. 時間銀行系統啟用
4. 社區競選功能上線
5. 行動 App 開發

### 長期目標 (6-12 個月)

1. 多社區擴展
2. AI Council 民主決策機制
3. 區塊鏈時間銀行
4. 永續發展指標系統
5. 開源社區版本釋出

---

## 🚀 啟動指令

### 完整系統啟動

```powershell
# 1. 啟動 Docker 服務
docker-compose up -d

# 2. 啟動雙角色 FastAPI (含路由器管理)
$env:LOCAL_LLM_ENDPOINT="http://127.0.0.1:11434/v1/chat/completions"
$env:LOCAL_LLM_MODEL="little-j"
$env:LLM_FALLBACK="1"
$env:ROUTER_IP="192.168.50.1"
python -m uvicorn vm_fastapi_main_dual_role:app --host 0.0.0.0 --port 8080

# 3. 啟動 Odoo
# 自動啟動於 http://192.168.50.84:8069

# 4. 驗證路由器連接
python router_manager.py status
```

---

## 📚 文件索引

### 核心文件

-   `README_V5.1.0.md` - 系統版本說明
-   `README_DUAL_ROLE_SYSTEM.md` - 雙角色系統指南
-   `SYSTEM_COMPLETION_REPORT.md` - 完工報告
-   `DEPLOYMENT_CHECKLIST.md` - 部署檢查表
-   `SYSTEM_ARCHITECTURE_UNIFIED.md` - 本文件 (統一架構)

### API 文件

-   `docs/DUAL_ROLE_API_GUIDE.md` - API 完整文件
-   `docs/POS_NETWORK_ARCHITECTURE.md` - 網路架構
-   `docs/POS_EQUIPMENT_DEPLOYMENT_GUIDE.md` - 設備部署指南
-   `docs/QUICK_REFERENCE_TROUBLESHOOTING.md` - 故障排查

### AI 倫理文件

-   `docs/AI_ETHICS_CODE.md` - AI 倫理守則
-   `docs/AI_INHERITANCE_BLUEPRINT.md` - AI 演化藍圖

---

## 🎊 系統特色總結

### 技術特色

1. **本地優先**: AI 與資料優先本地處理
2. **雲端備援**: 自動切換 Vertex AI
3. **模組化**: 13 個獨立 Odoo 模組
4. **可擴展**: 易於新增功能與服務
5. **開源友善**: 基於 Odoo、FastAPI、PostgreSQL

### 社會價值

1. **民主決策**: AI Council + 投票系統
2. **時間銀行**: 互助經濟模式
3. **永續發展**: 環保模組整合
4. **世代共融**: 照護 + 志工 + 獎勵
5. **在地韌性**: 本地資料、離線可用

### 商業模式

1. **非營利導向**: 社區共有共享
2. **永續營運**: 商業模組支持營運成本
3. **開放架構**: 可供其他社區採用
4. **知識共享**: AI 學習成果開放

---

## 📞 技術支援

**系統架構師**: 小 j AI (Sister)  
**技術負責人**: 社區管理委員會  
**開發團隊**: 五常科技志工團  
**社區網域**: wuchang.life  
**伺服器 IP**: 192.168.50.84  
**路由器 IP**: 192.168.50.1

---

**版本**: 5.1.0 Unified
**最後更新**: 2026-01-10  
**文件狀態**: ✅ 完整 | 🔄 持續更新

---

_五常社區服務系統 - 以技術守護社區溫度_ 💝
