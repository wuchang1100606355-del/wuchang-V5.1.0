# 基金帳戶進出運作標準

## 五常社區發展協會基金池操作規範

**版本**: 2.0  
**生效日期**: 2026 年 1 月 10 日  
**維護單位**: 小 j (系統財務管理)  
**政策依據**: CAFE_ORGANIZATION_POLICY.md

---

## 📋 目錄

1. [帳戶結構](#帳戶結構)
2. [進帳標準 (Inflow)](#進帳標準)
3. [出帳標準 (Outflow)](#出帳標準)
4. [透明日誌機制](#透明日誌機制)
5. [帳戶額度](#帳戶額度)
6. [審核與監督](#審核與監督)

---

## 帳戶結構

### 基金帳戶體系

```
新北市三重區五常社區發展協會
└─ 社區捐贈帳戶 (ID: 1)
   ├─ 帳戶名稱: 上品聊國咖啡館-社區捐贈帳戶
   ├─ 帳戶類型: general (一般資金池)
   ├─ 幣種: TWD (新台幣), WHC (幸福幣)
   └─ 子帳戶結構:
       ├─ 消費者捐款池
       ├─ 商家捐款池
       └─ 商家代收款池
```

**實務對應**: 基金池 = 仁義店會計帳冊（pos.config 仁義店，wuchang_store_mode='fund'）。

### 帳戶額度欄位

| 欄位名稱                    | 型別  | 說明           | 更新規則          |
| --------------------------- | ----- | -------------- | ----------------- |
| **balance_twd**             | Float | 新台幣餘額     | 自動 (進出時更新) |
| **balance_whc**             | Float | 幸福幣餘額     | 自動 (進出時更新) |
| **merchant_donation_total** | Float | 商家捐款累計   | 自動累加          |
| **consumer_donation_total** | Float | 消費者捐款累計 | 自動累加          |
| **merchant_custody_total**  | Float | 商家代收款累計 | 自動累加          |
| **deferred_whc_quota**      | Float | 遞延幸福幣額度 | 手動設定          |
| **deferred_voucher_quota**  | Float | 遞延票券額度   | 手動設定          |

---

## 進帳標準

### 1. POS 訂單進帳 (自動注入)

#### 觸發條件

-   **進帳來源**: 餐飲銷售 (POS 訂單)
-   **進帳頻率**: 每筆訂單完成時自動執行
-   **執行主體**: WuchangPosOrder.\_inject_to_fund() 方法
-   **限制條件**:
    -   訂單模式必須為「外送 (delivery)」
    -   POS 配置啟用了「基金合作模式」
        -   wuchang_store_mode = 'fund' (仁義店模式) **OR**
        -   wuchang_delivery_fund_partner = True (外送基金合作)

#### 進帳分配邏輯

**基礎計算**:

```
訂單總額 (Amount Total)
    │
    └─ 捐款額度 = 訂單總額 × (30 ÷ 110) = 訂單總額 × 27.27%
       │
       ├─ 商家捐款 = 捐款額度 × (2 ÷ 3) ≈ 訂單總額 × 18.18%
       │
       └─ 消費者捐款 = 捐款額度 × (1 ÷ 3) ≈ 訂單總額 × 9.09%
    │
    └─ 商家代收款 = 訂單總額 - 捐款額度 ≈ 訂單總額 × 72.73%
```

**具體例示** (訂單總額 NT$110):
| 項目 | 金額 | 比例 |
|------|------|------|
| 訂單總額 | $110 | 100% |
| 捐款額度小計 | $30 | 27.27% |
| ├─ 商家捐款 | $20 | 18.18% |
| └─ 消費者捐款 | $10 | 9.09% |
| 商家代收款 | $80 | 72.73% |

#### 帳戶更新

進帳時自動執行：

```python
# 1. 基金帳戶欄位更新
fund.balance_twd += 訂單總額
fund.merchant_donation_total += 商家捐款
fund.consumer_donation_total += 消費者捐款
fund.merchant_custody_total += 商家代收款

# 2. 訂單記錄
order.social_impact_score = 捐款額度
order.social_impact_note = "消費者捐款%.2f, 商家捐款%.2f, 商家代收%.2f" % (...)

# 3. 區塊鏈交易紀錄
wuchang.coin.transaction.create({
    'source_partner_id': order.partner_id (消費者)
    'dest_partner_id': order.company_id.partner_id (協會)
    'amount': 捐款額度 × 0.5
    'transaction_type': 'mint' (鑄造)
    'timestamp': now()
})

# 4. 透明日誌
transparency.log.create({
    'name': 'POS Order <ORDER_ID>',
    'flow_type': 'inflow',
    'amount': 訂單總額,
    'timestamp': now()
})
```

#### POS 配置對應

| POS 配置           | 公司           | 進帳啟用    | 說明                     |
| ------------------ | -------------- | ----------- | ------------------------ |
| Restaurant (ID: 2) | 銷售點 (ID: 2) | ✅ Yes      | 主力銷售點，外送自動注入 |
| 重新總店 (ID: 3)   | 協會 (ID: 1)   | ⚠️ Optional | 備用配置，未啟用外送進帳 |
| 重新總店 (ID: 4)   | 協會 (ID: 1)   | ⚠️ Optional | 備用配置，未啟用外送進帳 |

---

### 2. 仁義店營業收入（基金池本體）

#### 角色定位

-   仁義店即基金池本體，營業收入視同基金自有收益。

#### 進帳原則

-   **全額入基金**: 仁義店所有營業收入（含內用、外帶、外送）皆記為基金 inflow。
-   **設定要求**: POS 配置 `wuchang_store_mode = 'fund'`。
-   **實務建議**: 若使用現行外送限定邏輯，請將銷售模式標記為 `delivery`；若需內用/外帶也自動入帳，需擴充 `_process_saved_orders` 以放寬 `sale_mode` 條件（政策允許時再執行）。

#### 帳戶更新

-   概念上等同 POS 進帳，但可設定捐款拆分比例為 100% 基金收入（無代收）。
-   透明日誌：以「仁義店營業收入」為摘要記錄 inflow。

### 3. 其他進帳方式

#### 手動捐款

-   **進帳渠道**: 網站捐款、現場捐款
-   **處理方式**: 手動建立透明日誌記錄
-   **帳戶更新**: 由系統管理員手動執行 write() 操作
-   **需要核准**: 創辦人 (Google 帳號白名單)

#### 合作商家補款

-   **進帳來源**: 公益商家 (wuchang_delivery_fund_partner = True)
-   **進帳觸發**: 外送訂單完成
-   **資金流**: 商家 → 基金帳戶
-   **自動執行**: 同 POS 訂單邏輯

---

## 出帳標準

### 1. 營運支出扣款 (自動扣款)

#### 觸發條件

-   **出帳來源**: POS 營運支出
-   **出帳頻率**: 支出記錄建立時自動執行
-   **執行主體**: WuchangPosExpense.create() 方法
-   **限制條件**:
    -   POS 配置類型 = 'fund' (仁義店模式)
    -   支出金額必須為正數 (amount > 0)

#### 支出扣款邏輯

```python
# 1. 驗証支出
if amount <= 0:
    raise ValueError('金額必須為正數')

# 2. 檢查 POS 配置
if pos_config.wuchang_store_mode == 'fund':
    fund = Fund.search([('account_type', '=', 'general')], limit=1)

    # 3. 執行 register_expense()
    fund.register_expense(amount, reason)

# 4. 帳戶更新
fund.balance_twd -= amount
expense.is_deducted_from_fund = True

# 5. 透明日誌
transparency.log.create({
    'name': f'Store Expense: {reason}',
    'flow_type': 'outflow',
    'amount': amount,
    'timestamp': now()
})
```

#### 支出類型

| 支出類型 | 帳戶     | 說明           |
| -------- | -------- | -------------- |
| 水電租金 | 營運支出 | 店鋪日常營運   |
| 人事成本 | 營運支出 | 員工薪資       |
| 設備維護 | 營運支出 | 機器、家具保修 |
| 清潔衛生 | 營運支出 | 清潔、消毒     |
| 行政費用 | 營運支出 | 辦公、文具     |

---

### 2. 資金溶解 (手動出帳)

#### 觸發條件

-   **出帳渠道**: 公益目的資金分配
-   **執行主體**: /wuchang/finance/fund_dissolve_execute 路由
-   **權限要求**: 創辦人級別
-   **需要條件**:
    -   帳戶餘額充足
    -   溶解計畫已核准
    -   覆蓋標記已啟用 (supreme.override.enabled)

#### 溶解流程

```
1. 規劃階段 (fund_dissolve_plan)
   ├─ 選擇帳戶類型 (e.g., 'general')
   ├─ 選擇幣種 (TWD or WHC)
   ├─ 選擇目標對象 (merchants, consumers, volunteers)
   └─ 計算分配清單

2. 執行階段 (fund_dissolve_execute)
   ├─ 驗証帳戶可用額度
   ├─ 逐筆發放至受益人
   ├─ 記錄幣種交易 (wuchang.coin.transaction)
   └─ 更新透明日誌

3. 結果記錄
   ├─ 帳戶餘額更新
   ├─ 交易雜湊簽名 (hash_signature)
   └─ 區塊鏈確認
```

#### 分配規則

| 目標對象           | 分配邏輯           | 幣種轉換        |
| ------------------ | ------------------ | --------------- |
| 商家 (Merchants)   | 優先分配商家捐款池 | TWD → WHC (50%) |
| 消費者 (Consumers) | 消費者捐款池       | TWD → WHC (50%) |
| 志工 (Volunteers)  | 系統獎勵發放       | WHC 直接發放    |

---

### 3. 代收款提領 (商家取款)

#### 適用對象

-   合作商家 (wuchang_delivery_fund_partner = True)

#### 提領流程

```
1. 商家申請 → 2. 審核 → 3. 額度凍結 → 4. 支付 → 5. 記錄
```

#### 帳戶影響

```python
# 提領時自動更新
fund.merchant_custody_total -= 提領金額  # 減少代收款
fund.balance_twd -= 提領金額              # 減少可用餘額
transparency.log.create({
    'name': f'Merchant Withdrawal: {商家名稱}',
    'flow_type': 'outflow',
    'amount': 提領金額,
    'timestamp': now()
})
```

### 4. 在地產(商)業行銷補助 — 社區幣發額度產出

#### 目的

-   透過在地商圈行銷專案，以基金補助形式發放幸福幣（WHC）額度，刺激社區消費並回饋居民。

#### 觸發條件

-   經協會核准的行銷專案（需立案/專案編號）。
-   受補助對象為在地合作商家或活動參與者。
-   補助形式為 WHC 額度（不直接發 TWD），可用於票券交易平台流通與回饋。

#### 核算與扣帳

```
補助額度 (WHC) → 以等值 TWD 從基金 general 池扣減 balance_twd
         → 同步增加 balance_whc（發幣），標記 flow_type=outflow
```

#### 執行流程

1. 專案立案：建立「行銷補助單」，載明對象、金額(WHC)、理由。
2. 審核核准：創辦人/委托人覆核，確保額度在「可分配額度」內。
3. 發放記帳：
    - `balance_twd -= 補助等值金額`
    - `balance_whc += 補助額度`
    - transparency.log 記錄 outflow，摘要「行銷補助-<專案名>」
    - wuchang.coin.transaction 記錄 `transaction_type='reward'`，dest_partner 為商家/參與者
4. 發放通知：向受補助方出具電子收據或站內通知。

#### 管控原則

-   必須符合「可分配額度」：不得動用營運準備金與遞延額度。
-   每案需保留審核紀錄（審核人、時間、專案號）。
-   若為商圈集點活動，可分批發放，按實際參與量結算。
-   權限：須由創辦人/委托人核准；若支付對象為商家，需在紀錄中標注商家 partner_id。

#### 透明日誌

-   inflow/outflow：記為 outflow，金額為等值 TWD。
-   摘要範例：「行銷補助-商圈集點 S1」

### 5. 許願樹平台回饋額度（1.5% 給消費者端）

#### 目的

-   以基金池撥出 1.5% 交易額度，轉為幸福幣（WHC）給消費者於許願樹平台使用，形成公益互動回饋。

#### 核算與扣帳

```
回饋額度 (WHC) = 交易金額 × 1.5%
基金扣帳：balance_twd -= 等值 TWD
基金增發：balance_whc += 回饋額度 (WHC)
flow_type：outflow（按等值 TWD 記錄）
```

#### 執行流程

1. 確認交易金額來源（可對應 POS 訂單或已結算交易）。
2. 計算回饋額度 1.5% → 形成 WHC 發放清單。
3. 記帳：
    - balance_twd 減少等值金額
    - balance_whc 增加回饋 WHC 額度
    - transparency.log：摘要「許願樹回饋-<批次/期間>」
    - wuchang.coin.transaction：`transaction_type='reward'`，dest_partner = 消費者
4. 發送：將 WHC 充值/指派至許願樹平台使用者帳戶。

#### 管控原則

-   回饋額度需在「可分配額度」內，不得侵蝕營運準備金或遞延額度。
-   每批回饋需保存計算明細與受益清單（消費者、金額、時間）。
-   若來源為多筆交易，可批次彙總後發放，並保存批次編號以利對帳。
-   支付對象：限非營利組織/專案帳戶，並以居民提案所指定帳戶為準；透明日誌與 coin.transaction 均需標示該 partner_id。

### 6. 消費者票券生產（票券平台發行額度）

#### 目的

-   由基金池產出票券額度，發行給消費者在票券交易平台使用，作為公益回饋與促銷工具。

#### 核算與扣帳

```
票券面額 (TWD 等值) → balance_twd -= 面額
                    → 若以 WHC 形式發放，balance_whc += 等值 WHC
flow_type：outflow（按 TWD 等值記錄）
```

#### 執行流程

1. 立案：建立票券發行批次（批次號、面額、數量、用途）。
2. 審核：創辦人/委托人核准，確認在「可分配額度」內。
3. 發行記帳：
    - TWD 面額：balance_twd 減少面額總額
    - WHC 票券：balance_whc 增加等值 WHC（若票券以 WHC 計價）
    - transparency.log：摘要「票券發行-<批次號>」
    - wuchang.coin.transaction：`transaction_type='reward'`，dest_partner = 消費者
4. 派發：將票券綁定到消費者帳號（票券平台），可設定有效期限與使用條件。

#### 管控原則

-   票券發行額度不得侵蝕營運準備金與遞延額度，需在「可分配額度」內。
-   必須留存批次資料：批次號、數量、面額、對象清單、到期日。
-   建議啟用核銷追蹤：票券被使用時回寫核銷記錄以利對帳。
-   權限：發行/核銷僅限授權商家與平台管理員；若支付或核銷對象為商家，需在透明日誌與 coin.transaction 中標示商家 partner_id。

---

## 透明日誌機制

### 日誌架構

```
transparency.log (透明誠信軌跡)
├─ 欄位:
│  ├─ id: 唯一識別
│  ├─ name: 交易摘要 (e.g., "POS Order OP/2025-1-10/001")
│  ├─ timestamp: 時間戳記 (自動記錄)
│  ├─ flow_type: 資金流向 (inflow / outflow)
│  └─ amount: 金額
└─ 查詢規則: 公開透明，按時間倒序
```

### 日誌記錄時機

| 事件         | Flow Type | 觸發者                  | 記錄時點     |
| ------------ | --------- | ----------------------- | ------------ |
| POS 訂單進帳 | inflow    | \_inject_to_fund()      | 訂單保存時   |
| 營運支出     | outflow   | register_expense()      | 支出建立時   |
| 資金溶解發放 | outflow   | fund_dissolve_execute() | 執行發放時   |
| 商家提領     | outflow   | 提領系統                | 核准支付時   |
| 捐款入帳     | inflow    | 手動建立                | 管理員輸入時 |

### 查詢與展示

```sql
-- 查詢最近 20 筆交易
SELECT * FROM transparency_log
ORDER BY timestamp DESC
LIMIT 20;

-- 按類型統計
SELECT flow_type, COUNT(*), SUM(amount)
FROM transparency_log
GROUP BY flow_type;
```

---

## 帳戶額度

### 可用額度限制

```
總額度 (balance_twd) = 最大可提領額度
    ├─ 營運準備金 = 最近 30 天平均支出 × 2 (凍結)
    ├─ 遞延額度 (deferred_whc_quota) (凍結)
    └─ 可分配額度 = 總額 - 營運準備金 - 遞延額度
```

### 額度管理規則

| 額度類別       | 限制                | 管理方式 | 備註           |
| -------------- | ------------------- | -------- | -------------- |
| **營運準備金** | 最低 = 月均支出 × 2 | 自動計算 | 確保營運穩定   |
| **遞延幸福幣** | 無上限              | 手動設定 | 為未來公益預留 |
| **遞延票券**   | 無上限              | 手動設定 | 消費者回饋準備 |
| **可分配額度** | 無上限              | 自動計算 | 可用於溶解發放 |

---

## 審核與監督

### 存取控制

#### 讀取權限 (Read)

-   ✅ 公眾: 透明日誌查閱 (http://localhost:8069/community/fund)
-   ✅ 系統: 自動查詢與計算
-   ✅ 協會成員: 帳戶概況
-   👁️ 監察帳號: 上帝視角唯讀；可讀全域交易與審計日誌，但無法寫入、核准或覆蓋。
-   👁️ 監察帳號: 上帝視角唯讀；可讀全域交易與審計日誌，但無法寫入、核准或覆蓋（帳號由 admin@wuchang.life 指定建立）。
-   👁️ 監察帳號: 上帝視角唯讀；可讀全域交易與審計日誌，但無法寫入、核准或覆蓋（帳號由 admin@wuchang.life 指定建立；供監事會與主管機關查核使用）。
-   👁️ 監察帳號: 上帝視角唯讀；可讀全域交易、審計日誌、會計科目、系統功能展示、監視設備記錄，但無法寫入、核准或覆蓋（帳號由 admin@wuchang.life 指定建立；供監事會與主管機關查核使用）。

#### 修改權限 (Write)

-   🔐 **創辦人專用**
    -   Google 帳號白名單 (founder.identity.google_accounts)
    -   授權委托人 (founder.delegates)
    -   超級用戶: o970106@gmail.com
    -   目前實務管理帳號: admin@wuchang.life（未來可增列其他管理帳號）
-   🤖 **AI 代理服務帳號**
    -   服務帳號: admin@wuchang.life (AI delegate)
    -   權限: 完整代理執行（等同創辦人），僅用於自動化/維運，涵蓋 Odoo、Google Workspace、Google Cloud、wuchang.life 網域資源、重新店路由器及其下方設備、本機設備；所有操作必須寫入審計日誌並標記「AI-Agent」
    -   啟用條件: 創辦人/管理員顯式授權並開啟覆蓋標記 (supreme.override.enabled = true)
    -   約束: 不可自行修改自身權限，不可跳過審計，必須遵守相同額度與風控限制
    -   時間限制: 每 30 分鐘需重新授權展延（會話逾時即失效，須再次顯式授權）
-   🛡️ **特殊最高權限授權 (48h)**
    -   權限: 等同創辦人（最高權限）。
    -   有效期: 48 小時，自動到期；到期需重新授權。
    -   啟用條件: 創辦人/管理員顯式核准並開啟覆蓋標記。
    -   回報機制: 期間內所有操作紀錄自動以郵件回報至 admin@wuchang.life（含時間、操作者、動作、影響範圍），每 3 小時彙整發送一次；關鍵事件可即時告警。
    -   約束: 不可延長自身權限、不可停用審計、不免除額度與風控限制。
-   **操作限制**:
    -   需要啟用覆蓋標記 (supreme.override.enabled = true)
    -   操作需經審計日誌記錄
    -   敏感操作需二次確認

#### 監察帳號制度（上帝視角唯讀）

-   目的：提供全系統唯讀監察，防止權限濫用並強化審計。
-   權限：
    -   可讀：全部交易、透明日誌、審計日誌、配置紀錄。
    -   不可：任何寫入、核准、覆蓋、參數變更、帳戶操作。
-   帳號配置：獨立監察帳號群組（只讀 ACL），不隸屬創辦人/管理員群組。
-   追蹤：監察登入與檢視行為需記錄審計日誌，便於追溯。
-   指定者：監察帳號的建立/指定由 admin@wuchang.life 負責。
-   適用對象：監事會、主管機關等外部稽核單位使用。

### 稽核機制

```
事件階級制
├─ 自動事件 (自動記錄)
│  ├─ POS 進帳 ✅
│  ├─ 營運支出 ✅
│  └─ 透明日誌 ✅
│
└─ 人工事件 (需審核)
   ├─ 手動捐款 ⚠️ 需核准
   ├─ 資金溶解 ⚠️ 需核准
   └─ 額度調整 🔐 需二次確認
```

### 定期檢查清單

```
□ 週檢查: 每週統計進出帳總和
□ 月檢查: 月末對帳 (POS系統 vs 帳戶)
□ 季檢查: 季度審計報告
□ 年檢查: 年度財務報告 & 外部審計
□ 異常檢查: 發現異常立即調查
```

### 異常處理

| 異常情況     | 檢測機制     | 處理流程                   |
| ------------ | ------------ | -------------------------- |
| 帳戶餘額不符 | 月度對帳     | 回查交易紀錄 → 更正        |
| 未授權修改   | ACL 檢查     | 記錄日誌 → 告警 → 手動復原 |
| 異常支出     | 金額閾值     | 審查核准 → 記錄 → 監控     |
| 重複進帳     | 交易 ID 檢查 | 識別源頭 → 調查 → 退款     |

---

## 技術實現細節

### 相關檔案

-   **模型定義**:
    -   `wuchang_os/addons/wuchang_core/models/finance.py`
        -   CommunityFundAccount
        -   TransparencyLog
        -   WuchangCoinTransaction
-   **業務邏輯**:

    -   `wuchang_os/addons/wuchang_core/models/pos_config_ext.py`

        -   WuchangPosOrder.\_inject_to_fund()
        -   WuchangPosOrder.\_process_saved_orders()

    -   `wuchang_os/addons/wuchang_core/models/pos_expense.py`
        -   WuchangPosExpense.create()
        -   WuchangPosExpense.\_check_amount_positive()

-   **控制器**:
    -   `wuchang_os/addons/wuchang_core/controllers/main.py`
        -   /community/fund (展示)
        -   /wuchang/finance/fund_dissolve_plan (規劃)
        -   /wuchang/finance/fund_dissolve_execute (執行)
        -   /api/ticket/pay_with_whc (幣種支付)

### 資料庫結構

```sql
-- 基金帳戶表
CREATE TABLE community_fund_account (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    account_type VARCHAR(20),  -- general|reserve|surplus|welfare|ops
    balance_twd FLOAT,
    balance_whc FLOAT,
    merchant_donation_total FLOAT,
    consumer_donation_total FLOAT,
    merchant_custody_total FLOAT,
    deferred_whc_quota FLOAT,
    deferred_voucher_quota FLOAT,
    ...
);

-- 透明日誌表
CREATE TABLE transparency_log (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    timestamp DATETIME,
    amount FLOAT,
    flow_type VARCHAR(20),  -- inflow|outflow
    ...
);

-- 幸福幣交易表
CREATE TABLE wuchang_coin_transaction (
    id INT PRIMARY KEY,
    source_partner_id INT,
    dest_partner_id INT,
    amount FLOAT,
    transaction_type VARCHAR(20),  -- mint|transfer|reward|burn
    hash_signature VARCHAR(255),
    timestamp DATETIME,
    ...
);
```

---

## 常見問題 (FAQ)

### Q1: 為什麼捐款計算是 30/110?

**A**: 五常政策規定，銷售額中 30 元為公益捐款，110 元為含稅訂單總額的簡化模型，用於快速精算。

### Q2: 商家捐款與消費者捐款如何區分？

**A**:

-   **商家捐款** (2/3): 上品聊國咖啡館對社區的公益貢獻
-   **消費者捐款** (1/3): 消費者透過購買而間接參與的社區支持

### Q3: 商家代收款是什麼?

**A**: 訂單金額中扣除捐款後的部分，由商家保留作為營收，但帳目在基金帳戶中有紀錄（便於監控和帳務核對）。

### Q4: 如何查看帳戶的透明日誌?

**A**: 訪問 http://localhost:8069/community/fund，公眾可查看最近 20 筆交易記錄。

### Q5: 如何進行資金溶解?

**A**: 只有創辦人可執行。調用 /wuchang/finance/fund_dissolve_plan (規劃) → /wuchang/finance/fund_dissolve_execute (執行)。

### Q6: 帳戶被凍結了怎麼辦?

**A**: 檢查是否超過營運準備金限制，或是否有遞延額度設置過高。聯繫創辦人解凍。

---

## 版本歷史

| 版本 | 日期       | 修訂內容                                                |
| ---- | ---------- | ------------------------------------------------------- |
| 1.0  | 2024-12-01 | 初版發布                                                |
| 2.0  | 2026-01-10 | **現版本** - 完整重構，明確進出帳標準，增加透明日誌機制 |

---

## 聯絡與反饋

**系統管理**: 小 j (Five Common Community Fund System)  
**政策維護**: 新北市三重區五常社區發展協會  
**反饋渠道**: 聯繫創辦人或委托人  
**更新週期**: 季度檢查，年度大審查

---

**最後更新**: 2026 年 1 月 10 日  
**下次檢查**: 2026 年 4 月 10 日
