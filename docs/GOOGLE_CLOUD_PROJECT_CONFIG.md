# Google Cloud 專案設定文件

**文件日期**: 2025-01-07  
**系統版本**: Wuchang OS V5.1.0  
**專案名稱**: wuchang-community-os  
**專案顯示名稱**: 五常社區系統

---

## 📋 專案基本資訊

### 專案識別

| 項目 | 內容 |
|------|------|
| **專案名稱** | `wuchang-community-os` |
| **專案顯示名稱** | 五常社區系統 |
| **專案 ID** | `wuchang-community-os`（或系統自動生成） |
| **組織** | 新北市三重區五常社區發展協會 |
| **帳單帳戶** | Google 非營利組織帳戶 |

### 管理員帳號

| 角色 | 電子郵件 | 權限 |
|------|---------|------|
| **主要管理員** | `admin@wuchang.life` | 擁有者 (Owner) |
| **專案管理員** | `wuchang11006355@gmail.com` | 編輯者 (Editor) 或 專案管理員 (Project Editor) |

---

## 👥 管理員設定

### 新增管理員步驟

1. **訪問 IAM 與管理**
   - 網址：https://console.cloud.google.com/iam-admin/iam
   - 確認已選擇正確專案：`wuchang-community-os`

2. **新增成員**
   - 點擊「授予存取權」
   - 在「新增成員」欄位輸入：`wuchang11006355@gmail.com`

3. **選擇角色**
   - 建議角色：**專案編輯者 (Project Editor)**
   - 或：**編輯者 (Editor)**
   - 權限說明：
     - ✅ 可以管理專案資源
     - ✅ 可以啟用/停用 API
     - ✅ 可以建立和管理資源
     - ❌ 不能刪除專案
     - ❌ 不能管理帳單

4. **儲存設定**
   - 點擊「儲存」
   - 確認新管理員已出現在成員列表中

---

## 🔑 啟用的 API 清單

### 必須啟用的 API（優先級 1）

| API 名稱 | API ID | 用途 | 費用 |
|---------|--------|------|------|
| **Maps Embed API** | `maps-embed-backend.googleapis.com` | 嵌入地圖顯示 | 免費（無限制） |
| **Geocoding API** | `geocoding-backend.googleapis.com` | 地址解析 | 免費（$200/月） |
| **Maps JavaScript API** | `maps-javascript-backend.googleapis.com` | 互動式地圖（可選） | 免費（$200/月） |

### 可選啟用的 API（優先級 2）

| API 名稱 | API ID | 用途 | 費用 |
|---------|--------|------|------|
| **Cloud Storage API** | `storage-component.googleapis.com` | 檔案儲存 | 約 $5-10/月 |
| **Compute Engine API** | `compute.googleapis.com` | VM 伺服器 | 約 $20-50/月 |
| **Cloud SQL Admin API** | `sqladmin.googleapis.com` | 資料庫管理 | 約 $15-40/月 |

---

## 🔐 API Key 設定

### 需要建立的 API Key

| API Key 名稱 | 用途 | 限制設定 |
|-------------|------|---------|
| **Maps API Key** | 地圖顯示和地址解析 | HTTP 參照網址限制 |

### API Key 限制設定

**應用程式限制**：
- 類型：HTTP 參照網址（網站）
- 允許的網址：
  - `http://192.168.50.249:8069/*`
  - `https://wuchang.life/*`
  - `https://shop.wuchang.life/*`
  - `https://*.wuchang.life/*`

**API 限制**：
- 類型：限制金鑰
- 允許的 API：
  - Maps Embed API
  - Geocoding API
  - Maps JavaScript API（如果啟用）

---

## 💰 預算與配額

### Google 非營利組織免費額度

| 項目 | 免費額度 | 說明 |
|------|---------|------|
| **Google Cloud 抵免額度** | $300 | 一次性抵免 |
| **Maps Embed API** | 無限制 | 完全免費 |
| **Geocoding API** | $200/月 | 約 40,000 次請求 |

### 預算警報設定

| 警報名稱 | 金額 | 說明 |
|---------|------|------|
| **預算警報 1** | $50 | 初期使用提醒 |
| **預算警報 2** | $100 | 中度使用提醒 |
| **預算警報 3** | $200 | 高度使用提醒 |
| **預算上限** | $300 | 避免超過免費額度 |

---

## 📊 資源運用規劃

### 第一階段（前 3 個月）

**目標**：使用 $300 免費額度，建立基礎服務

| 服務 | 預估使用 | 費用 |
|------|---------|------|
| Maps Embed API | 無限制使用 | $0 |
| Geocoding API | 10,000 次/月 | $0（免費額度內） |
| Cloud Storage | 10 GB | $0.23/月 |
| Compute Engine | 小型 VM | $20-30/月 |
| **總計** | | **$20-30/月** |

### 第二階段（3-6 個月）

**目標**：穩定營運，優化成本

| 服務 | 預估使用 | 費用 |
|------|---------|------|
| Maps Embed API | 無限制使用 | $0 |
| Geocoding API | 20,000 次/月 | $0（免費額度內） |
| Cloud Storage | 50 GB | $1.15/月 |
| Compute Engine | 標準 VM | $40-60/月 |
| **總計** | | **$40-60/月** |

### 第三階段（長期營運）

**目標**：穩定營運，持續優化

| 服務 | 預估使用 | 費用 |
|------|---------|------|
| Maps Embed API | 無限制使用 | $0 |
| Geocoding API | 30,000 次/月 | $0（免費額度內） |
| Cloud Storage | 100 GB | $2.30/月 |
| Compute Engine | 優化 VM | $50-80/月 |
| **總計** | | **$50-80/月** |

---

## 🛡️ 安全設定

### IAM 角色與權限

| 角色 | 成員 | 權限 |
|------|------|------|
| **擁有者 (Owner)** | `admin@wuchang.life` | 完整權限 |
| **專案編輯者 (Editor)** | `wuchang11006355@gmail.com` | 管理資源，不能刪除專案 |
| **檢視者 (Viewer)** | （可選） | 只能查看 |

### 安全最佳實踐

1. **啟用雙因素驗證**
   - 所有管理員帳號啟用 2FA

2. **定期審查權限**
   - 每月檢查一次 IAM 設定
   - 移除不需要的權限

3. **API Key 安全**
   - 設定 HTTP 參照網址限制
   - 設定 API 限制
   - 定期輪換 API Key

4. **啟用審計日誌**
   - 記錄所有管理操作
   - 定期檢查異常活動

---

## 📝 專案檢查清單

### 專案設定

- [ ] 專案名稱：`wuchang-community-os`
- [ ] 專案顯示名稱：五常社區系統
- [ ] 組織設定正確
- [ ] 帳單帳戶已連結
- [ ] $300 免費抵免額度已啟用

### 管理員設定

- [ ] `admin@wuchang.life` 為擁有者
- [ ] `wuchang11006355@gmail.com` 為專案編輯者
- [ ] 所有管理員已啟用 2FA

### API 啟用

- [ ] Maps Embed API
- [ ] Geocoding API
- [ ] Maps JavaScript API（可選）
- [ ] Cloud Storage API（如果需要）
- [ ] Compute Engine API（如果需要）

### API Key 設定

- [ ] 建立 Maps API Key
- [ ] 設定 HTTP 參照網址限制
- [ ] 設定 API 限制
- [ ] 在 Odoo 中設定 API Key

### 預算設定

- [ ] 設定預算警報（$50, $100, $200）
- [ ] 設定預算上限（$300）
- [ ] 啟用使用量監控

---

## 🔄 定期維護

### 每月檢查項目

1. **使用量檢查**
   - 檢查 API 使用量
   - 檢查費用
   - 確認在免費額度內

2. **安全檢查**
   - 檢查 IAM 權限
   - 檢查 API Key 使用情況
   - 檢查異常活動

3. **優化建議**
   - 優化不必要的服務
   - 調整資源配置
   - 降低成本

---

## 📞 聯絡資訊

### Google Cloud 支援

- **Google Cloud Console**: https://console.cloud.google.com/
- **Google 非營利組織支援**: https://support.google.com/nonprofits
- **帳單支援**: https://console.cloud.google.com/billing

### 專案管理員

- **主要管理員**: `admin@wuchang.life`
- **專案管理員**: `wuchang11006355@gmail.com`

---

**文件版本**: 1.0  
**最後更新**: 2025-01-07  
**維護者**: 小J (Little J)
