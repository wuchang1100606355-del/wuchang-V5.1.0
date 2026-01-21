## 資產盤點（可交接/可稽核/可估值）
更新時間：2026-01-15

> 定義：凡可支撐系統運作、可取得資源、可形成合規/治理能力、或可轉換為外部補助與合作籌碼者，均列為資產。

---

## A. 組織/合規資產（高層）
- **協會主體**：新北市三重區五常社區發展協會（基金/規則/治理的法定主體）
- **基金池載體**：仁義店會計系統（獨立基金池、無資本利得、不得私領、依規定支出）
- **贊助方（重新店）**：只出不進（基礎設施/人力/費用贊助，不得回流核銷）

---

## B. 網域與 DNS 資產
### B1. 主網域
- **`wuchang.life`**（根域 + 多子網域）

### B2. DNS 記錄（證據）
- 來源：`dns_records.json`
- 解析摘要：
  - `wuchang.life` → `35.185.167.23`, `220.135.21.74`
  - `www/shop/ui.wuchang.life` → `220.135.21.74`
  - `odoo.wuchang.life` → `35.185.167.23`
  - `core/admin/verify/butler/ft/vs.wuchang.life` → `35.201.170.114`
  - `pos/pm/hj/housing.wuchang.life` → `104.199.144.93`
  - `_acme-challenge*` TXT（Let’s Encrypt 驗證用）

---

## C. 主機/IP/網路資產
### C1. 公網 IP/主機分佈（由 DNS 推定）
- `220.135.21.74`：路由器/店內側（含 `www/shop/ui` 指向）
- `35.185.167.23`：Google Cloud（含 `odoo`）
- `35.201.170.114`：Google Cloud（含 `core/admin/verify/...`）
- `104.199.144.93`：Google Cloud（含 `pos/...`）

### C2. 路由器與 DDNS
- **路由器**：ASUS RT-BE86U
- **遠端管理**：`https://CoffeeLoge.asuscomm.com:8443`（DDNS 解析至 `220.135.21.74`）
- **設備所有權**：重新店（設備捐助）
- **購入日期**：2025-05-01
- **購入金額**：7,950 元（對應重新店捐款）
- **網路服務**：中華電信 1G 光纖網路
- **月費**：1,399 元/月（對應重新店捐款）
- **會計記錄**：`association_operational_files/financial/設備購入記錄_路由器.json`

### C3. 本機入口層（重要：會影響你對「部署狀態」的判讀）
- 證據：`C:\Windows\System32\drivers\etc\hosts`
  - `wuchang.life` 等多個子網域被覆寫到 `127.0.0.1`
- 目前本機 80/443 listener 證據（摘要）：Docker Desktop (`com.docker.backend.exe`) + WSL relay + `iphlpsvc`
- 詳細盤點：`SYSTEM_INVENTORY.md`

---

## D. 系統/應用資產（本 workspace 可直接掌控的部分）
### D1. 程式與模組
- **社區資料 API（Blueprint）**：`api_community_data.py`
- **頭像上傳 API（Blueprint）**：`upload_avatar_api.py`
- **知識庫/索引**：`ai_knowledge_base.py`、`community_kb_indexer.py`、`wuchang_community_knowledge_index.json`
- **社區分析資料**：`wuchang_community_analysis.json`
- **UI/展示頁**：`system_architecture.html`、`wuchang_community_dashboard.html`
- **路由器/連線診斷工具**：`router_connection.py`、`login_router.py`、`diagnose_connection.py`、`test_local_connection.py`
- **工作憲法**：`AGENT_CONSTITUTION.md`（降低反覆解釋成本）

### D2. 資料資產（可重用/可稽核/可衍生）
- 五常生活圈分析：人口/交通/商業/幸福幣機制/策略建議（`wuchang_community_analysis.json`）
- 知識庫（原始 + 索引）：`wuchang_community_knowledge_base.json`、`wuchang_community_knowledge_index.json`

---

## E. 外部資源資產（Google for Nonprofits）
> 前提：協會已完成 Google for Nonprofits 驗證（此項視為永久事實）

### E1. Google Workspace for Nonprofits
- 可用於：協會網域信箱、共用雲端文件、會議、管理控台、稽核留存（依方案）
- 參考：`https://www.google.com/nonprofits/offerings/workspace/`

### E2. Google Ad Grants
- 資產型態：搜尋廣告額度（常見上限為每月 USD $10,000）
- 可用於：招募商家/志工、公益活動曝光、服務導流至 `wuchang.life`
- 參考：`https://www.google.com/nonprofits/offerings/google-ad-grants/`

### E3. Google Maps Platform 公益方案（抵免）
- 資產型態：地圖 API 抵免（依公益方案與審核）
- 可用於：商家/服務點地圖、影響力可視化、社區資源定位
- 參考：`https://developers.google.com/maps/billing-and-pricing/public-programs`

### E4. Google Cloud（專案型/申請型資源）
- 資產型態：多為計畫/專案型 credit 或 need-based grant（非保證固定月額）
- 可用於：資料分析、生成式 AI、系統擴展（依計畫核准）

---

## F. 知識產權/技術資產（可用於補助/合作籌碼）
### F1. 新型專利技術（你方持有）
- 資產型態：新型專利與對應的可驗證技術能力（含「驗證」能力）
- 用途：
  - 對外合作/授權談判籌碼
  - 重大補助申請的技術核心（例如 SBIR）

#### F1.1 新型專利證書（證據：已取得）
- **專利類別**：新型
- **專利號**：`M663678`（證書上格式：新型第 `M663678` 號）
- **新型名稱**：整合式物業管理系統
- **專利權人**：江政隆、蔣明彥
- **新型創作人**：江政隆、蔣明彥
- **專利權期間**：自 2024 年 12 月 1 日至 2034 年 6 月 25 日止
- **證書日期**：中華民國 113 年 12 月 1 日
- **PDF 內建欄位（metadata）**：
  - `/ApplicationNo`：`113206785`
  - `/CertificateNo`：`M663678`
  - `/CreationDate`：`20241112011433+08'00'`
- **來源（可稽核）**：
  - `C:\Users\o0930\Dropbox\公司資料室\五常社區服務系統\行政\商業法人組織\智財\專利\877-24-0046.UTW_證書.PDF`

#### F1.2 新型技術文件（中文本 / 摘要 / 說明書 / 請求項 / 圖式）
> 用途：把「專利權利範圍」落到「系統模組/資料/介面」的可追溯對照（避免只剩宣稱、無法驗收）。

- **來源（可稽核）**：
  - `C:\Users\o0930\OneDrive\文件\Downloads\877-24-0046.UTW-中文本.pdf`
  - `J:\我的雲端硬碟\Bound\Downloads\877-24-0046.UTW-核准處分書.pdf`
- **文件要點（節錄）**：
  - **安全管理系統**：控制模組 + 臉部辨識門禁；無人保全（攝影機/感測器/資料處理）；依警告派遣「菁英保全網路」並透過行動 App 協調。
  - **社區支援與電商**：中央資料庫（居民/商家）、社區參與介面（行動裝置）、交易子系統；並描述「基於區塊鏈的貨幣模組」以確保交易安全/透明（依場景可公/私鏈）。
  - **整合營運/物業管理**：中央管理子系統 + 資料分析元件（含追蹤節省成本、優化資源配置）；商業整合與本地供應商網路支援線上訂購/配送；溝通介面提供即時資料。
  - **附加整合**：郵件接收註冊通知（包裹收發/通知/住戶確認）；線上會議（行事曆/通知/會議協作/文件共享等）。
  - **圖式**：圖 1～圖 4（整體/安全管理/社區+電商/商業營運+物業整合）。

#### F1.3 專利技術 vs 現行系統（證據對照）
> 對照範圍：以你目前在 Z 槽的 `wuchang_os`（Odoo 模組 + 前端資源）與其 Docker 服務為主。

| 專利子系統 / 元件 | 現行系統狀態 | 證據（檔案/模組） |
| --- | --- | --- |
| **控制模組 + 臉部辨識門禁**（112） | **部分**：現有「生物特徵/影像辨識」用於「最高權限身份驗證」，但**未見**對接「門禁設備/出入口」的控制模組與白名單資料庫（偏向管理者驗證，不是物業門禁） | `Z:\wuchang_os\addons\wuchang_core\models\ai_guard.py`（`verify_brother_access()` / `analyze_image()`） |
| **無人保全子系統**（攝影機/感測器/資料處理） | **未見完整落地**：有設備納管/監控框架（device/iot/heartbeat/狀態檢查），但未見「影像串流 + AI 異常偵測/模式識別 + 自動警告」的資料管線 | `Z:\wuchang_os\addons\wuchang_core\models\infrastructure.py`、`Z:\wuchang_os\addons\wuchang_core\models\device_control_plan.py` |
| **菁英保全網路 + 行動 App**（132） | **部分**：有「社區 Super App」雛形（住戶/志工/市集/基金/錢包等 UI），可作為承載「緊急通報/派遣/導航」的介面基礎，但未見「保全派遣/巡邏」專用流程與權限模型 | `Z:\wuchang_os\addons\wuchang_core\static\src\js\community_super_app.jsx` |
| **社區支援 + 電商平台**（200） | **已落地/部分**：存在社區/棟別/戶號/住戶反映、包裹收發、公告；亦有外送訂單/商家/券與「許願額度」等模型；前端有市集/基金/錢包 UI | `Z:\wuchang_os\addons\wuchang_core\models\property_management.py`、`Z:\wuchang_os\addons\wuchang_core\models\delivery.py`、`Z:\wuchang_os\addons\wuchang_core\static\src\js\community_super_app.jsx` |
| **交易子系統 + 區塊鏈貨幣模組**（232） | **部分**：有「幸福幣交易紀錄（Blockchain-like Ledger）」與雜湊欄位，提供不可篡改軌跡的資料結構；但未見接上真正鏈（公/私鏈節點、共識、鏈上驗證） | `Z:\wuchang_os\addons\wuchang_core\models\finance.py`（`wuchang.coin.transaction.hash_signature`）、`Z:\wuchang_os\addons\wuchang_core\models\delivery.py`（`wuchang.community.coin`） |
| **中央管理子系統 + 資料分析元件**（312） | **部分/待補證據**：目前看到的是資料模型與 UI 看板雛形，尚未看到專利描述的「預測/規範分析、風險評估模型、成本節省追蹤」等專用分析元件 | `Z:\wuchang_os\addons\wuchang_core\models\property_management.py`（資料模型）、`Z:\wuchang_os\addons\wuchang_core\static\src\js\community_super_app.jsx`（看板雛形） |
| **溝通介面/通知**（330） | **部分**：有通知 API 入口（broadcast），亦有 Google Meet 整合模型/視圖（但 Calendar API 仍標示 TODO） | `Z:\wuchang_os\addons\wuchang_core\controllers\notification_controller.py`、`Z:\wuchang_os\addons\wuchang_google_integration\models\google_meet.py` |
| **郵件/包裹註冊通知系統** | **部分**：已有包裹資料模型與「領取確認」動作；未見自動通知到住戶（可用 Odoo chatter/email 或你現有的 notification broadcast 串接） | `Z:\wuchang_os\addons\wuchang_core\models\property_management.py`（`community.package`）、`Z:\wuchang_os\addons\wuchang_core\controllers\notification_controller.py` |
| **線上會議系統** | **部分**：有三方協作/AI 會議資料模型與預設資料；Google Meet 介面已建但 API 連線仍待補 | `Z:\wuchang_os\addons\wuchang_core\models\collab_meeting.py`、`Z:\wuchang_os\addons\wuchang_core\data\meeting_setup.xml`、`Z:\wuchang_os\addons\wuchang_google_integration\models\google_meet.py` |

### F2. SBIR 補助（可申請資源池）
- 資產型態：外部補助（鉅額補助，依國別/主管機關制度）
- 依你用語「SBIR」：可能對應
  - **台灣經濟部 SBIR（小型企業創新研發計畫）**，或
  - **美國 SBIR/STTR** 等
- 本盤點先將其列為「可申請外部資產」，後續在主系統盤點時，再把「申請主體/技術驗證材料/里程碑」對齊。

#### F2.1 SBIR 申請用「技術/智財證據摘要」（來自彙編）
- 彙編中自述之新型專利：`877-24-0046.UTW`《整合式物業管理系統》，並載明「專利授權號：第 663678 號」。
- **來源（可稽核）**：
  - `C:\Users\o0930\Dropbox\SBIR\江政隆_資料彙編_最終版.txt`

---

## G. 目前可直接引用的證據文件
- `AGENT_CONSTITUTION.md`：協作憲法（含 Google for Nonprofits 已驗證）
- `SYSTEM_INVENTORY.md`：系統/網路/本機入口層盤點（含 hosts 覆寫與 listener 證據）
- `dns_records.json` / `dns_audit_report.json`：DNS 資產與稽核摘要
- `C:\Users\o0930\Dropbox\公司資料室\五常社區服務系統\行政\商業法人組織\智財\專利\877-24-0046.UTW_證書.PDF`：新型專利證書（`M663678`）
- `C:\Users\o0930\OneDrive\文件\Downloads\877-24-0046.UTW-中文本.pdf`：新型技術文件（摘要/說明書/請求項/圖式）
- `J:\我的雲端硬碟\Bound\Downloads\877-24-0046.UTW-核准處分書.pdf`：核准處分書（官方文書）
- `C:\Users\o0930\Dropbox\SBIR\江政隆_資料彙編_最終版.txt`：SBIR 申請材料彙編（含智財與計畫摘要）

