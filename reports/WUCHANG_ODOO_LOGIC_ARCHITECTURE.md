# 五常雲端空間 (Wuchang OS) 全系統 Odoo 邏輯架構規劃書

> **文件狀態**：規劃中
> **建立日期**：2026-01-27
> **目標**：利用 Odoo 模組化功能追蹤並實現全系統完整邏輯架構，整合雙J協作機制與 50/50 金流分配模型。

## 1. 系統架構概覽 (Architecture Overview)

本系統以 **Odoo 17.0** 為核心骨幹 (Backbone)，採用 **三層式架構** 實現從硬體控制到高層治理的完整覆蓋。

### 1.1 層級劃分
1.  **基礎設施層 (Infrastructure Layer)**：負責物理設備介接、身份識別與網路控制。
2.  **核心業務層 (Core Business Layer)**：實現四大平台功能與金流分配邏輯。
3.  **治理與協作層 (Governance & Collaboration Layer)**：包含雙J協作、規則執行與決策支援。

---

## 2. 模組功能追蹤矩陣 (Module-Function Logic Matrix)

### 2.1 基礎設施層 (Infrastructure)
| 模組名稱 (Technical Name) | 核心功能 (Core Functions) | 邏輯追蹤 (Logic Tracking) | 雙J協作點 (Dual-J) |
| :--- | :--- | :--- | :--- |
| `wuchang_biometric_identity` | **生物辨識身份管理** | 1. 綁定系統創辦人與最高權限<br>2. 實作三階段權限模型<br>3. 記錄設計與使用責任 (Accountability) | **Little J**: 驗證地端生物特徵與 MAC<br>**Jules**: 記錄雲端審計日誌 |
| `wuchang_router_management` | **路由器基礎設施管理** | 1. 納管 ASUS RT-BE86U<br>2. 自動識別 Server 1/2 雙身份<br>3. 動態端口轉發規則管理 | **Little J**: 直接下達 Router 指令阻斷入侵<br>**Jules**: 分析流量異常模式 |

### 2.2 核心業務層 (Core Business) - 四大平台
| 模組名稱 (Technical Name) | 對應平台 (Platform) | 核心功能與金流邏輯 (Financial Logic) | 雙J協作點 (Dual-J) |
| :--- | :--- | :--- | :--- |
| `wuchang_finance` | **金流核心** | 1. **50/50 分配引擎**：自動分流營收至消費循環池與組織運作<br>2. **儲備擔保機制**：確保 15% 幸福幣有 100% 現金儲備<br>3. **分層遞延**：計算遞延性票券額度 | **Little J**: 即時記帳每一筆交易<br>**Jules**: 每日審計儲備率與合規性 |
| `wuchang_business` | **商圈聯合公益外送** | 1. **外送交易處理**：拆分 30% 注入金 (商家20%+消費者10%)<br>2. **回饋發放**：即時發放 15% 票券額度 + 15% 幸福幣<br>3. **產品管理**：在地商家商品上架與庫存同步 | **Little J**: 處理訂單隱私與即時路況<br>**Jules**: 運算全域最佳配送路徑 |
| `wuchang_property_toolkits` | **智慧物業管理** | 1. **數位圍籬**：結合 Router 模組管理訪客網絡<br>2. **資產管理**：社區公設預約與維護追蹤<br>3. **利潤共享**：物業收益自動進入基金池 | **Little J**: 地端門禁控制與 QR 驗證<br>**Jules**: 長期出入安全分析 |
| `wuchang_community_campaign` | **社區許願樹** | 1. **許願媒合**：居民需求 vs 許願額度扣抵<br>2. **專案執行**：5% 許願樹專款預算控制<br>3. **透明投票**：社區提案的電子投票機制 | **Little J**: 收集語音/文字許願<br>**Jules**: 情感分析與外部 NPO 媒合 |
| `wuchang_volunteer` | **社區專勤隊** | 1. **人力派遣**：志工/服務人員排班與打卡<br>2. **時間銀行**：服務時數轉化為幸福幣 (由 20% 志工組預算支付)<br>3. **健康監控**：隊員狀態追蹤 | **Little J**: 監控隊員即時位置與安全<br>**Jules**: 計算貢獻值與排班優化 |

### 2.3 治理與協作層 (Governance)
| 模組名稱 (Technical Name) | 核心功能 (Core Functions) | 邏輯追蹤 (Logic Tracking) |
| :--- | :--- | :--- |
| `wuchang_governance` (規劃中) | **規則與條約執行** | 1. **Code as Law**：攔截違反規則層的寫入操作<br>2. **電子簽章**：重大規則變更需多方簽署<br>3. **透明儀表板**：即時展示基金池水位與分配狀態 |
| `wuchang_dual_j_bridge` (規劃中) | **雙J協作橋接** | 1. **任務派發**：Jules (雲端) → Little J (地端) 任務佇列<br>2. **狀態同步**：地端容器狀態與日誌上傳 (去識別化)<br>3. **PII 過濾器**：確保敏感個資不出地端 |

---

## 3. 系統邏輯流 (System Logic Flow)

### 3.1 外送交易閉環 (Delivery Transaction Loop)
1.  **觸發**：消費者下單 (POS/App) → `wuchang_business`。
2.  **支付**：消費者支付現金/數位支付 (含 10% 捐贈)。
3.  **拆帳**：`wuchang_finance` 自動扣除商家 20% 營收 + 消費者 10% 支付。
4.  **分配**：
    *   **50% (總額 15%)** → 鎖入 **消費循環池** (現金)。
    *   **50% (總額 15%)** → 分流至 **組織運作帳戶** (志工/系統/許願/基金)。
5.  **發行**：
    *   `wuchang_finance` 鑄造等值 15% **幸福幣** → 發送至消費者錢包 (由消費循環池 100% 擔保)。
    *   `wuchang_finance` 核發等值 15% **票券額度** → 發送至商家帳戶。
6.  **協作**：
    *   **Little J**：確認地端 POS 交易完成，去識別化訂單數據。
    *   **Jules**：接收去識別化數據，更新全域需求預測模型。

### 3.2 許願樹專案執行 (Wishing Tree Execution)
1.  **提案**：居民透過 App 許願 → `wuchang_community_campaign`。
2.  **審核**：雙J 協作分析 (Little J 語意理解 + Jules 資源媒合)。
3.  **預算**：檢查 **5% 許願樹專款** 餘額 → `wuchang_finance`。
4.  **執行**：若預算足夠且符合規則，自動立案並派發給 `wuchang_volunteer` (專勤隊)。
5.  **結案**：志工完成服務，獲得時間銀行點數 (幸福幣)，由許願樹專款支付。

---

## 4. 下一步開發建議 (Next Steps)

1.  **模組重構 (Refactoring)**：
    *   確認 `wuchang_finance` 是否已完整實作修正後的 50/50 模型與 15% 回饋邏輯。
    *   將 `wuchang_business` 與 `wuchang_finance` 進行深度綁定，確保每一筆交易自動觸發拆帳邏輯。

2.  **新模組開發 (New Development)**：
    *   **`wuchang_dual_j_bridge`**：正式建立雙J溝通的標準 Odoo 介面。
    *   **`wuchang_governance`**：實作規則層的電子簽章與攔截器。

3.  **儀表板可視化 (Visualization)**：
    *   在 Odoo 後台建立「全系統邏輯戰情室」，即時顯示各模組的運作狀態與金流健康度。
