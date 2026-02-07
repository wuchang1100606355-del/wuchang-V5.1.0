# Google Maps API 設定指南（Google 非營利組織）

**文件日期**: 2025-01-07  
**系統版本**: Wuchang OS V5.1.0  
**適用對象**: Google 非營利組織帳號

---

## 🎯 Google 非營利組織免費額度

### Maps API 免費額度

Google 為非營利組織提供以下免費額度：

| API | 免費額度 | 說明 |
|-----|---------|------|
| **Maps Embed API** | 無限制 | 嵌入地圖（我們使用） |
| **Geocoding API** | 每月 $200 免費額度 | 地址解析（約 40,000 次請求） |
| **Maps JavaScript API** | 每月 $200 免費額度 | 互動式地圖 |

**注意**：$200 免費額度通常足夠一般使用，超過後才需要付費。

---

## 📋 啟用步驟

### Step 1: 確認 Google 非營利組織狀態

1. 訪問：https://www.google.com/nonprofits/
2. 確認您的組織已通過 Google 非營利組織認證
3. 確認帳號：`admin@wuchang.life` 有管理權限

### Step 2: 啟用 Google Maps API

1. **訪問 Google Cloud Console**
   - 網址：https://console.cloud.google.com/
   - 使用 `admin@wuchang.life` 登入

2. **選擇或建立專案**
   - 如果已有專案，選擇現有專案
   - 如果沒有，建立新專案（例如：`wuchang-community`）

3. **啟用必要的 API**
   - 進入「API 和服務」→「程式庫」
   - 搜尋並啟用以下 API：
     - ✅ **Maps Embed API**（嵌入地圖）
     - ✅ **Geocoding API**（地址解析）
     - ✅ **Maps JavaScript API**（可選，用於進階功能）

4. **建立 API Key**
   - 進入「API 和服務」→「憑證」
   - 點擊「建立憑證」→「API 金鑰」
   - 複製 API Key（格式：`AIza...`）

5. **設定 API Key 限制（建議）**
   - 點擊剛建立的 API Key
   - 在「應用程式限制」中選擇「HTTP 參照網址（網站）」
   - 新增允許的網址：
     - `http://192.168.50.249:8069/*`
     - `https://wuchang.life/*`
     - `https://shop.wuchang.life/*`
   - 在「API 限制」中選擇「限制金鑰」
   - 只勾選：
     - Maps Embed API
     - Geocoding API
     - Maps JavaScript API（如果啟用）

---

## 🔧 在 Odoo 中設定 API Key

### 方式 1: 透過 Odoo UI（推薦）

1. 登入 Odoo：http://192.168.50.249:8069/web/login
2. 進入「設定」→「技術」→「參數」→「系統參數」
3. 搜尋或建立以下參數：

   | 參數名稱 | 參數值 | 說明 |
   |---------|--------|------|
   | `google.maps.api_key` | `您的 API Key` | Google Maps API Key |

4. 儲存設定

### 方式 2: 透過 Python 腳本

```python
# 在 Odoo shell 中執行
env['ir.config_parameter'].sudo().set_param('google.maps.api_key', '您的 API Key')
```

### 方式 3: 透過環境變數

```powershell
# 設定環境變數
$env:GOOGLE_MAPS_API_KEY = "您的 API Key"

# 使用腳本設定
python scripts/odoo_set_google_maps_key.py
```

---

## ✅ 驗證設定

### 檢查 API Key 是否設定

1. 訪問設備專屬網頁 APP：
   ```
   http://192.168.50.249:8069/device/<device_token>/app
   ```

2. 點擊「📍 取得目前位置」

3. 如果看到 Google Maps 地圖，表示設定成功！

### 檢查 API 使用量

1. 訪問 Google Cloud Console
2. 進入「API 和服務」→「儀表板」
3. 查看 API 使用量和配額

---

## 🔄 自動切換機制

系統會自動判斷：

- **如果有 Google Maps API Key**：
  - ✅ 使用 Google Maps（高品質、中文支援好）
  - ✅ 使用 Google Geocoding API（地址解析準確）

- **如果沒有 Google Maps API Key**：
  - ✅ 自動使用 OpenStreetMap（備選方案）
  - ✅ 使用 OpenStreetMap Nominatim（地址解析）

**無需手動切換**，系統會自動選擇最佳方案！

---

## 💡 使用建議

### 推薦設定

1. **啟用 Google Maps API**
   - 享受 Google 非營利組織免費額度
   - 更好的地圖品質和中文支援
   - 更準確的地址解析

2. **設定 API Key 限制**
   - 限制只能從您的網域使用
   - 防止 API Key 被濫用
   - 保護您的配額

3. **監控使用量**
   - 定期檢查 API 使用量
   - 確保不超過免費額度
   - 必要時調整使用策略

---

## 🐛 故障排除

### API Key 無效

1. **檢查 API Key 是否正確**
   - 確認複製時沒有多餘空格
   - 確認 API Key 格式正確（以 `AIza` 開頭）

2. **檢查 API 是否啟用**
   - 確認 Maps Embed API 已啟用
   - 確認 Geocoding API 已啟用

3. **檢查 API Key 限制**
   - 確認網址限制設定正確
   - 確認 API 限制包含必要的 API

### 超過免費額度

1. **檢查使用量**
   - 查看 Google Cloud Console 中的使用量
   - 確認是否真的超過額度

2. **優化使用**
   - 減少不必要的 API 呼叫
   - 使用快取機制

3. **備選方案**
   - 系統會自動切換到 OpenStreetMap
   - 不會影響功能使用

---

## 📊 Google 非營利組織額度詳情

### Maps Embed API
- **免費額度**：無限制
- **用途**：嵌入地圖到網頁
- **我們的使用**：設備位置顯示

### Geocoding API
- **免費額度**：每月 $200（約 40,000 次請求）
- **用途**：座標轉地址、地址轉座標
- **我們的使用**：反向地理編碼（取得地址）

### 估算使用量

假設：
- 10 台設備
- 每台設備每 5 分鐘更新一次位置
- 每天 12 小時運作

**每日請求數**：
- 位置更新：10 台 × (12小時 × 60分鐘 / 5分鐘) = 1,440 次
- 地址解析：1,440 次

**每月請求數**：
- 約 43,200 次（略超過免費額度）

**建議**：
- 可以調整更新頻率（例如每 10 分鐘一次）
- 或使用快取機制減少 API 呼叫
- 或混合使用（Google Maps 顯示 + OpenStreetMap 地址解析）

---

## 🎯 下一步

1. ✅ 啟用 Google Maps API
2. ✅ 建立 API Key
3. ✅ 在 Odoo 中設定 API Key
4. ✅ 驗證設定
5. ✅ 享受 Google 非營利組織免費額度！

---

**文件版本**: 1.0  
**最後更新**: 2025-01-07  
**維護者**: 小J (Little J)
