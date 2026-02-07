# Android POS 設備納管指南

**文件日期**: 2025-01-07  
**系統版本**: Wuchang OS V5.1.0  
**設備**: v3_mix_edla_gl (Android 13)  
**AI 身份**: Little J (小j)

---

## 🎯 設備資訊

| 項目 | 資訊 |
|------|------|
| **設備名稱** | v3_mix_edla_gl |
| **作業系統** | Android 13 |
| **設備類型** | POS Terminal |
| **IP 地址** | 192.168.50.86 |
| **通訊埠** | 41895 |
| **開發者模式** | ✅ 已開啟 |
| **USB 偵錯** | ✅ 已開啟 |
| **GPU 偵錯** | ✅ 已開啟 |
| **WiFi 偵錯** | ✅ 已開啟 |
| **Demo Mode** | ❌ 不需要開啟 |

---

## ❓ 關於 UI 示範模式 (Demo Mode)

### 📋 Demo Mode 是什麼？

Android 的 **UI 示範模式 (Demo Mode)** 是一個特殊的系統模式，主要用於：

- 📱 **零售展示**：在商店展示設備時使用
- 🖼️ **示範內容**：顯示固定的示範內容（時間、電池、訊號等）
- 🏷️ **標記顯示**：在狀態列顯示「示範模式」標記

### ✅ 對於 POS 設備的建議

**❌ 不需要開啟 Demo Mode**

**原因：**

1. **Demo Mode 的用途不同**
   - Demo Mode 主要用於零售展示，不是用於實際 POS 運作
   - 會顯示「示範模式」標記，可能影響使用者體驗

2. **開發者模式已足夠**
   - ✅ 開發者模式已開啟，足以進行設備管理和調試
   - ✅ 可以進行 ADB 連接和遠程管理
   - ✅ 可以安裝和更新應用程式

3. **Kiosk 模式更適合**
   - 如果需要鎖定設備到特定應用（如 Odoo POS），應使用 **Google Workspace MDM** 的 Kiosk 模式
   - Kiosk 模式可以鎖定到 Odoo POS 應用，防止使用者離開應用
   - 更專業且符合企業管理標準

### 💡 推薦方案

**使用 Google Workspace MDM 進行設備管理：**

1. **Kiosk 模式設定**
   - 透過 Google Workspace Admin Console 設定
   - 鎖定設備到 Odoo POS 應用程式
   - 防止使用者離開應用或安裝其他應用

2. **應用程式管理**
   - 強制安裝 Odoo POS 應用
   - 自動更新應用程式
   - 限制只能使用授權應用

3. **安全策略**
   - 設備加密
   - 密碼策略
   - 遠程鎖定和擦除

---

## 🚀 納管步驟

### Step 1: 確認設備設定

在 Android 設備上確認以下設定：

- ✅ **開發者模式**：已開啟
- ✅ **USB 偵錯**：已開啟（用於 ADB 連接和設備管理）
- ✅ **GPU 偵錯**：已開啟（用於圖形效能調試）
- ✅ **WiFi 偵錯**：已開啟（用於無線 ADB 連接）
- ❌ **Demo Mode**：保持關閉（不需要）
- ✅ **網路連線**：連接到與 VM 伺服器相同的網路（192.168.50.0/24）
- ✅ **IP 地址**：192.168.50.86
- ✅ **通訊埠**：41895

### Step 2: 執行納管腳本

#### 方式 1: 在 Android 設備上執行（推薦）

如果設備已安裝 Python 環境：

```bash
# 下載納管腳本到設備
# 執行納管
python3 enroll_android_pos.py \
  --device-name "v3_mix_edla_gl" \
  --android-version "13" \
  --ip "192.168.50.86" \
  --port 41895 \
  --developer-mode \
  --vm-ip "192.168.50.84"
```

#### 方式 2: 透過 ADB 遠程執行

從電腦透過 ADB 連接設備並執行：

```bash
# 連接設備
adb connect <設備IP>:5555

# 推送腳本到設備
adb push enroll_android_pos.py /sdcard/

# 執行腳本
adb shell "python3 /sdcard/enroll_android_pos.py \
  --device-name 'v3_mix_edla_gl' \
  --android-version '13' \
  --developer-mode \
  --vm-ip '192.168.50.84'"
```

#### 方式 3: 手動納管（使用 curl）

```bash
curl -X POST "http://192.168.50.84:8069/api/device/enroll/android" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "ANDROID_V3_MIX_EDLA_GL",
    "device_name": "v3_mix_edla_gl",
    "device_type": "pos",
    "os_type": "android",
    "os_version": "13",
    "ip_address": "192.168.50.86",
    "port": 41895,
    "mac_address": "<MAC地址>",
    "developer_mode": true,
    "demo_mode": false,
    "debug_options": {
      "usb": true,
      "gpu": true,
      "wifi": true
    },
    "capabilities": {
      "kiosk_mode": true,
      "remote_management": true,
      "app_deployment": true,
      "data_sync": true
    }
  }'
```

### Step 3: 在 Odoo 中確認納管

1. 登入 Odoo 管理界面
2. 進入「基礎設施」→「設備」
3. 搜尋設備名稱 `v3_mix_edla_gl`
4. 確認設備狀態為「在線」

### Step 4: Google Workspace MDM 設定（推薦）

1. **登入 Google Workspace Admin Console**
   - 網址: `https://admin.google.com`
   - 帳號: `admin@wuchang.life`

2. **註冊設備**
   - 進入「設備」→「行動裝置與端點」→「Android」
   - 選擇「註冊設備」
   - 輸入設備資訊：
     - 設備名稱: `v3_mix_edla_gl`
     - 設備 ID: `ANDROID_V3_MIX_EDLA_GL`
     - 組織單位: `POS-重新總店`

3. **設定 Kiosk 模式**
   - 進入設備設定 →「應用程式」→「Kiosk 模式」
   - 選擇「單一應用 Kiosk 模式」
   - 指定應用: `Odoo POS`（需要先安裝）
   - 啟用「鎖定到應用程式」

4. **設定應用程式政策**
   - 強制安裝: `Odoo POS App`
   - 允許應用: 必要的 POS 相關應用
   - 禁止應用: 其他未授權應用

5. **設定安全策略**
   - 設備加密: 強制啟用
   - 密碼策略: 最少 8 位元
   - 螢幕鎖定: 5 分鐘無操作自動鎖定

---

## 📋 納管檢查清單

### 設備設定

- [ ] 開發者模式已開啟
- [ ] USB 調試已開啟（可選，用於 ADB）
- [ ] Demo Mode 保持關閉（不需要）
- [ ] 網路連線正常
- [ ] 可以連接到 VM 伺服器 (192.168.50.84:8069)

### 納管執行

- [ ] 已執行納管腳本或 API 呼叫
- [ ] 納管成功，收到確認回應
- [ ] 在 Odoo 中可以看到設備記錄
- [ ] 設備狀態顯示為「在線」

### Google Workspace MDM（推薦）

- [ ] 設備已註冊到 Google Workspace
- [ ] Kiosk 模式已設定
- [ ] Odoo POS 應用已安裝
- [ ] 應用程式政策已套用
- [ ] 安全策略已設定

### 功能測試

- [ ] 可以從 Odoo 發送控制指令到設備
- [ ] 設備可以接收並執行指令
- [ ] Google Drive 同步功能正常
- [ ] POS 應用可以正常運作

---

## 🔧 常見問題

### Q1: 為什麼不需要開啟 Demo Mode？

**A:** Demo Mode 主要用於零售展示，不是用於實際 POS 運作。對於 POS 設備，應使用 Google Workspace MDM 的 Kiosk 模式來鎖定設備到特定應用。

### Q2: 開發者模式是否安全？

**A:** 開發者模式在生產環境中確實有安全風險。建議：
- 在開發和測試階段使用開發者模式
- 生產環境中透過 Google Workspace MDM 管理設備
- 使用 MDM 的安全策略來保護設備

### Q3: 如何鎖定設備到 Odoo POS 應用？

**A:** 使用 Google Workspace MDM 的 Kiosk 模式：
1. 在 Admin Console 中設定單一應用 Kiosk 模式
2. 指定 Odoo POS 應用
3. 啟用「鎖定到應用程式」選項

### Q4: 納管失敗怎麼辦？

**A:** 檢查以下項目：
1. VM 伺服器的 Odoo 服務是否運行
2. 網路連線是否正常
3. IP 地址是否正確
4. 防火牆是否阻擋連線
5. 查看 Odoo 日誌中的錯誤訊息

---

## 📊 納管後的功能

納管成功後，設備將具備以下功能：

1. **遠程管理**
   - 從 Odoo 發送控制指令
   - 遠程更新應用程式
   - 遠程配置設備設定

2. **資料同步**
   - Google Drive 自動同步
   - POS 資料即時更新
   - 交易記錄自動備份

3. **安全保護**
   - 設備加密
   - 密碼策略
   - 遠程鎖定和擦除

4. **應用程式管理**
   - 自動安裝和更新
   - 版本控制
   - 應用程式限制

---

## 🎯 總結

### ✅ 建議設定

- **開發者模式**: ✅ 已開啟（用於開發和調試）
- **Demo Mode**: ❌ **不需要開啟**
- **Kiosk 模式**: ✅ 使用 Google Workspace MDM 設定
- **應用程式鎖定**: ✅ 透過 MDM 鎖定到 Odoo POS

### 📝 下一步

1. 執行納管腳本將設備納管到 Odoo
2. 在 Google Workspace Admin Console 註冊設備
3. 設定 Kiosk 模式鎖定到 Odoo POS 應用
4. 配置 Google Drive 同步
5. 測試所有功能

---

**文件版本**: 1.0  
**最後更新**: 2025-01-07  
**維護者**: 小J (Little J)  
**設備**: v3_mix_edla_gl (Android 13)
