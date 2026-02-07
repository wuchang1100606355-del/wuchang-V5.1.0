# Google AI Studio 非營利組織使用指南

**建立時間：** 2026-01-20  
**適用對象：** 非營利組織

---

## 📋 Google AI Studio 概述

Google AI Studio 是一個基於瀏覽器的整合開發環境 (IDE)，可幫助您使用生成模型進行原型設計。您可以快速嘗試各種模型，使用不同的提示進行試驗。

---

## 💰 非營利組織使用費用

### ✅ 免費使用額度

**Google AI Studio 提供免費使用額度：**

1. **免費層級**
   - 提供每月免費使用額度
   - 適合開發和測試用途
   - 無需信用卡即可開始使用

2. **免費額度包含**
   - 一定數量的 API 請求
   - 基本的模型使用
   - 適合小規模測試和原型開發

### 💳 付費使用

**超過免費額度後：**

1. **按使用量計費**
   - 根據實際使用的 API 請求數計費
   - 價格因模型類型而異

2. **非營利組織優惠**
   - 可申請 Google Cloud for Nonprofits 抵免額
   - 每月 $350 美元抵免額可用於所有 Google Cloud 服務
   - **AI Studio 的 API 使用可以使用此抵免額**

---

## 🎯 非營利組織使用建議

### 方案 1：純免費使用（推薦開始）

**適用情況：**
- 開發和測試階段
- 小規模使用
- 原型開發

**優點：**
- ✅ 完全免費
- ✅ 無需信用卡
- ✅ 無需申請

**限制：**
- ⚠️ 有使用量限制
- ⚠️ 可能無法滿足大量需求

### 方案 2：使用 Google Cloud 非營利抵免額

**適用情況：**
- 需要更多使用額度
- 正式環境使用
- 較大規模的應用

**優點：**
- ✅ 每月 $350 美元抵免額
- ✅ 可用於 AI Studio API
- ✅ 超出部分才需付費

**申請步驟：**
1. 申請 Google Cloud for Nonprofits
2. 獲得每月 $350 美元抵免額
3. 使用抵免額支付 AI Studio API 費用

---

## 🔧 啟用 Google AI Studio

### 步驟 1：驗證域名

**必須先完成：**
- 驗證 Google Workspace 域名
- 確保域名所有權

### 步驟 2：啟用 AI Studio

根據 Google 管理控制台操作：

1. **登入 Google 管理控制台**
   ```
   https://admin.google.com
   ```

2. **導航至 AI Studio**
   ```
   應用 > 附加 Google 服務 > AI Studio
   ```

3. **啟用服務**
   - 選擇「對所有人啟用」
   - 或為特定組織部門/群組啟用

4. **保存設定**

### 步驟 3：用戶使用

用戶可以：
- 訪問：https://aistudio.google.com
- 使用 Google Workspace 帳號登入
- 開始使用生成式 AI 模型

---

## 💡 成本控制建議

### 1. 監控使用量

- 定期檢查 API 使用量
- 設定使用量提醒
- 監控抵免額使用情況

### 2. 優化使用

- 使用較便宜的模型進行測試
- 批次處理請求以降低成本
- 快取常見結果

### 3. 設定預算提醒

在 Google Cloud Console 設定：
- 預算上限
- 使用量提醒
- 自動停止機制

---

## 📊 Google Cloud 非營利抵免額詳情

### 抵免額資訊

- **每月額度：** $350 美元
- **適用服務：** 所有 Google Cloud 服務
- **包括：** AI Studio API 使用
- **不累積：** 當月未用完的抵免額不會累積

### 申請方式

參考系統文件：
- `reports/GOOGLE_CLOUD_NONPROFIT_APPLICATION_GUIDE.md`
- `scripts/setup_google_cloud_nonprofit_credits.py`

### 使用範圍

抵免額可用於：
- ✅ Compute Engine（虛擬機器）
- ✅ Cloud Storage（雲端儲存）
- ✅ Cloud SQL（資料庫）
- ✅ Vertex AI（AI/ML 服務）
- ✅ **AI Studio API**（生成式 AI）
- ✅ 其他 Google Cloud 服務

---

## ⚠️ 重要注意事項

### 1. 區域限制

某些區域可能無法使用 AI Studio：
- 檢查服務可用性
- 確認所在區域支援

### 2. 使用限制

- 免費層級有速率限制
- 某些高級模型可能不在免費層級
- 商業使用需要付費帳號

### 3. 非營利資格

- 必須通過 Google for Nonprofits 驗證
- 需要符合非營利組織資格
- 定期需要重新驗證

---

## 🎯 總結

### 非營利組織使用 Google AI Studio 是否需要付費？

**答案：視使用量而定**

1. **免費使用：**
   - ✅ 有免費使用額度
   - ✅ 適合開發和測試
   - ✅ 小規模使用

2. **使用抵免額：**
   - ✅ 申請 Google Cloud for Nonprofits
   - ✅ 獲得每月 $350 美元抵免額
   - ✅ 可用於 AI Studio API
   - ✅ 超出部分才需付費

3. **付費使用：**
   - ⚠️ 超過免費額度和抵免額後
   - ⚠️ 按實際使用量計費

### 建議

對於非營利組織：
1. **開始階段：** 使用免費額度進行測試
2. **正式使用：** 申請 Google Cloud for Nonprofits 抵免額
3. **成本控制：** 監控使用量，設定預算提醒

---

## 📚 相關資源

- **AI Studio 官方文件：** https://aistudio.google.com
- **非營利組織申請：** https://cloud.google.com/apply-for-nonprofit-credits
- **Google Cloud 定價：** https://cloud.google.com/pricing
- **系統非營利申請指南：** `reports/GOOGLE_CLOUD_NONPROFIT_APPLICATION_GUIDE.md`

---

**建立時間：** 2026-01-20  
**最後更新：** 2026-01-20  
**組織：** 五常非營利組織
