# Google Cloud 專案設定與抵免額度指南

**文件日期**: 2025-01-07  
**系統版本**: Wuchang OS V5.1.0  
**適用對象**: Google 非營利組織（admin@wuchang.life）

---

## 🚨 問題 1: 選錯專案

### 情況說明

如果送件時選錯了專案（例如選到有 SBIR 字樣的專案），可以：

### 解決方案

#### 方案 A: 建立新專案（推薦）

1. **訪問 Google Cloud Console**
   - 網址：https://console.cloud.google.com/
   - 使用 `admin@wuchang.life` 登入

2. **建立新專案**
   - 點擊頂部專案選擇器
   - 點擊「新增專案」
   - 專案名稱建議：
     - `wuchang-community-os`（五常社區系統）
     - `wuchang-nonprofit`（五常非營利組織）
     - `wuchang-community`（五常社區）
   - 組織：選擇「新北市三重區五常社區發展協會」
   - 點擊「建立」

3. **切換到新專案**
   - 在專案選擇器中選擇新建立的專案

#### 方案 B: 在現有專案中繼續使用

如果 SBIR 專案可以繼續使用，也可以：
- 確認專案設定正確
- 確認組織和帳單設定正確
- 繼續使用該專案

---

## 💰 問題 2: Google Cloud 抵免額度

### Google 非營利組織免費額度

| 項目 | 免費額度 | 說明 |
|------|---------|------|
| **Google Cloud 抵免額度** | **$300** | 新帳號一次性抵免 |
| **Maps API** | 每月 $200 | Maps Embed API 無限制 |
| **Geocoding API** | 每月 $200 | 約 40,000 次請求 |

### 啟用抵免額度

1. **確認帳單帳戶**
   - 訪問：https://console.cloud.google.com/billing
   - 確認有帳單帳戶（即使有免費額度也需要設定帳單帳戶）

2. **啟用免費試用**
   - 如果尚未啟用，系統會提示啟用免費試用
   - 需要提供付款方式（但不會收費，除非超過免費額度）
   - 獲得 $300 免費抵免額度

3. **確認抵免額度**
   - 在「帳單」→「預算與配額」中查看
   - 確認 $300 抵免額度已啟用

---

## 📊 問題 3: 資源運用規劃

### 建議的資源分配

#### 優先級 1: 核心服務（必須）

| 服務 | 用途 | 預估費用 | 優先級 |
|------|------|---------|--------|
| **Maps Embed API** | 地圖顯示 | 免費（無限制） | ⭐⭐⭐⭐⭐ |
| **Geocoding API** | 地址解析 | 免費（$200/月） | ⭐⭐⭐⭐⭐ |
| **Cloud Storage** | 檔案儲存 | 約 $5-10/月 | ⭐⭐⭐⭐ |
| **Compute Engine** | VM 伺服器 | 約 $20-50/月 | ⭐⭐⭐⭐ |

#### 優先級 2: 進階服務（可選）

| 服務 | 用途 | 預估費用 | 優先級 |
|------|------|---------|--------|
| **Vertex AI** | AI 服務 | 約 $10-30/月 | ⭐⭐⭐ |
| **Cloud SQL** | 資料庫 | 約 $15-40/月 | ⭐⭐⭐ |
| **Cloud Functions** | 無伺服器函數 | 約 $5-15/月 | ⭐⭐ |

### 預算規劃建議

**第一階段（前 3 個月）**：
- 使用 $300 免費額度
- 重點：Maps API、基礎儲存
- 預估使用：$50-100/月

**第二階段（3-6 個月）**：
- 開始使用付費服務
- 重點：VM 伺服器、資料庫
- 預估使用：$100-200/月

**第三階段（長期營運）**：
- 穩定營運模式
- 優化成本
- 預估使用：$150-300/月

---

## 🔍 問題 4: SBIR 專案說明

### SBIR 是什麼？

**SBIR** = **Small Business Innovation Research**（小型企業創新研究）

這是**美國政府**的一個計劃，用於：
- 支援小型企業的創新研究
- 通常與政府合約相關
- 主要用於美國本土企業

### 為什麼會有 SBIR 專案？

可能的原因：
1. **誤選**：建立專案時選錯了範本或標籤
2. **測試專案**：之前測試時建立的
3. **其他用途**：可能有其他用途的專案

### 建議

**如果這是誤選的專案**：
- ✅ 建議建立新專案（見方案 A）
- ✅ 使用更合適的專案名稱
- ✅ 確保專案設定正確

**如果這個專案有其他用途**：
- ✅ 可以保留，但建議建立新專案用於五常社區系統
- ✅ 避免混淆

---

## 🎯 建議的專案結構

### 專案 1: 五常社區系統（主要）

**專案名稱**：`wuchang-community-os`

**用途**：
- Odoo 系統
- Maps API
- 設備管理
- 社區服務

**預算**：使用 $300 免費額度 + 每月預算

### 專案 2: SBIR 專案（保留或刪除）

**專案名稱**：`sbir-xxx`（現有）

**建議**：
- 如果不確定用途，可以保留
- 如果確定不需要，可以刪除
- 避免與主要專案混淆

---

## 📋 設定檢查清單

### 專案設定

- [ ] 建立新專案 `wuchang-community-os`
- [ ] 確認組織設定正確
- [ ] 確認帳單帳戶已連結
- [ ] 確認 $300 免費額度已啟用

### API 啟用

- [ ] Maps Embed API
- [ ] Geocoding API
- [ ] Maps JavaScript API（可選）
- [ ] Cloud Storage API（如果需要）
- [ ] Compute Engine API（如果需要）

### 安全設定

- [ ] 設定 API Key 限制
- [ ] 設定預算警報
- [ ] 設定使用量監控

---

## 🛠️ 快速設定腳本

### 建立新專案

```bash
# 使用 gcloud CLI（如果已安裝）
gcloud projects create wuchang-community-os \
    --name="五常社區系統" \
    --organization=YOUR_ORG_ID

# 設定為當前專案
gcloud config set project wuchang-community-os
```

### 啟用必要 API

```bash
# Maps API
gcloud services enable maps-embed-backend.googleapis.com
gcloud services enable geocoding-backend.googleapis.com

# 其他服務（如果需要）
gcloud services enable storage-component.googleapis.com
gcloud services enable compute.googleapis.com
```

---

## 💡 成本優化建議

1. **使用免費額度優先**
   - Maps Embed API（無限制）
   - Geocoding API（$200/月免費）

2. **設定預算警報**
   - 設定 $50、$100、$200 警報
   - 避免意外超支

3. **定期檢查使用量**
   - 每月檢查一次
   - 優化不必要的服務

4. **使用預留實例**
   - 如果需要長期使用 VM
   - 可以節省約 30-50% 成本

---

## 📞 需要協助？

如果遇到問題：
1. **Google Cloud 支援**：https://cloud.google.com/support
2. **Google 非營利組織支援**：https://support.google.com/nonprofits
3. **小J 協助**：我可以幫您檢查設定

---

**文件版本**: 1.0  
**最後更新**: 2025-01-07  
**維護者**: 小J (Little J)
