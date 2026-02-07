# 五常智慧社區雲 (Wuchang OS) 系統規格書
**版本**: 5.0.0 | **技術堆疊**: Odoo 16+, React 18, OWL, Python 3.10

---

## 1. 系統架構 (System Architecture)

本系統採用 **前後端分離 (Headless)** 與 **模組化 (Modular)** 的混合架構：

*   **Backend (核心層)**: 基於 Odoo 框架開發，負責資料庫管理、商業邏輯、權限控制與 API 服務。
*   **Frontend (應用層)**:
    *   **Web Client**: Odoo 原生 Web 介面，供深度管理使用。
    *   **Super App**: 基於 React.js 開發的單頁應用 (SPA)，嵌入於 Odoo Client Action 中，提供流暢的住戶體驗。
    *   **Public Website**: 基於 Odoo QWeb/Bootstrap 5 的響應式官網。

---

## 2. 資料模型設計 (Data Models)

### 2.1 志工模組 (`wuchang.volunteer`)
*   `wuchang.volunteer.task`: 任務定義 (名稱、獎勵、語音採集旗標)。
*   `wuchang.volunteer.signup`: 報名紀錄 (關聯 Partner)。
*   `wuchang.voice.sample`: AI 語音採集樣本 (Binary 音訊檔)。

### 2.2 財務模組 (`community.fund`)
*   `community.fund.pool`: 基金池主檔 (總金額、會計科目)。
*   `community.fund.log`: 資金流水帳 (收入/支出、來源類型)。
*   `community.sustainability.fund`: 年度永續基金結算。

### 2.3 外送與票券 (`wuchang.delivery`)
*   `wuchang.delivery.team`: 外送隊伍 (隊長、督導)。
*   `wuchang.delivery.order`: 訂單主檔 (整合 POS 與線上訂單，自動計算基金回饋)。
*   `wuchang.community.coin`: 幸福幣與票券帳本。

### 2.4 合作夥伴擴充 (`res.partner`)
*   擴充欄位：`whc_wallet_balance` (錢包餘額), `is_wuchang_resident` (住戶識別), `wuchang_shareholder_level` (股東等級)。

### 2.5 治理模組 (`wuchang.legal`)
*   `wuchang.legal.doc`: 法院公文紀錄 (數位簽章驗證)。
*   `res.users`: 擴充 `is_supreme_authority` (最高權限) 與 `bio_face_hash` (生物特徵)。

---

## 3. API 介面 (API Endpoints)

所有 API 位於 `/jules/api/v1/` 路徑下，採用 JSON-RPC 風格。

### 3.1 核心服務
*   `POST /jules/api/v1/get_resident_status`: 取得當前用戶的住戶狀態與錢包餘額。

### 3.2 商家與訂單
*   `POST /jules/api/v1/list_pos_stores`: 取得可用商家列表。
*   `POST /jules/api/v1/create_pos_online_order`: 建立新訂單 (支援外送/自取)。

### 3.3 志工與許願
*   `POST /jules/api/v1/list_volunteer_tasks`: 查詢可接單任務。
*   `POST /jules/api/v1/signup_volunteer`: 報名特定任務。
*   `POST /jules/api/v1/vote_wish`: 對許願樹提案進行投票 (扣除提案補助金)。

---

## 4. 前端組件 (Frontend Components)

### 4.1 CommunitySuperApp (React)
*   **路徑**: `static/src/js/community_super_app.jsx`
*   **功能**:
    *   **ResidentPortal**: 首頁、錢包、通知、個人中心。
    *   **HOAManagementDashboard**: 管委會戰情室 (基金、公文)。
    *   **MarketPlace**: 仿外送平台介面，支援購物車與結帳。
    *   **AiAssistant**: 懸浮聊天機器人 (小J)。

### 4.2 Delivery Interfaces (OWL)
*   **路徑**: `static/src/xml/delivery_interfaces.xml`
*   **模板**:
    *   `DeliveryRiderInterface`: 外送員接單 App。
    *   `DeliveryMerchantInterface`: 商家出餐看板 (Kanban)。
    *   `DeliveryCustomerInterface`: 訂單狀態追蹤條。
    *   `DeliveryCommandConsole`: 最高權限戰情室，即時監控全域訂單與專勤隊位置。

### 4.3 背景服務 (Background Service)
*   **路徑**: `static/src/js/background_service.js`
*   **功能**:
    *   **Notification Handling**: 監聽 Odoo Bus (`wuchang_delivery_dispatch`) 推播。
    *   **Alerts**: 播放提示音 (`alert.mp3`) 與瀏覽器原生通知。
    *   **Cooldown**: 任務完成後強制冷卻 15 分鐘機制。

---

## 5. 安全與權限 (Security)

*   **生物特徵綁定**: 最高權限操作需驗證 `bio_face_hash`。
*   **ACL**: 嚴格的 `ir.model.access.csv` 設定，區分 `group_resident`, `group_merchant`, `group_volunteer`, `group_system`。
*   **Kill Switch**: `_execute_takeover_protocol` 方法可由合規公文觸發，強制鎖定系統。
