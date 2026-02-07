# v3_mix_edla_gl Android POS 設備納管指南

**文件日期**: 2025-01-07  
**系統版本**: Wuchang OS V5.1.0  
**設備**: v3_mix_edla_gl (Android 13)  
**AI 身份**: Little J (小j)

---

## 📋 設備資訊

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

## ✅ 設備設定確認

### 已完成的設定

- ✅ **開發者模式**：已開啟
- ✅ **USB 偵錯**：已開啟（用於 ADB 連接）
- ✅ **GPU 偵錯**：已開啟（用於圖形效能調試）
- ✅ **WiFi 偵錯**：已開啟（用於無線 ADB 連接）
- ✅ **網路連線**：已連接到 192.168.50.0/24 網路
- ✅ **IP 地址**：192.168.50.86
- ✅ **通訊埠**：41895

### 不需要的設定

- ❌ **Demo Mode (UI 示範模式)**：不需要開啟
  - Demo Mode 主要用於零售展示，不是用於實際 POS 運作
  - 應使用 Google Workspace MDM 的 Kiosk 模式來鎖定設備到 Odoo POS 應用

---

## 🚀 納管步驟

### Step 1: 確認 VM 伺服器狀態（VM 為本地機器 192.168.50.249）

在執行納管前，請確認 VM 伺服器 (192.168.50.84) 的 Odoo 服務正在運行：

```powershell
# 檢查 Odoo 服務是否可訪問
Test-NetConnection -ComputerName 192.168.50.249 -Port 8069

# 或使用瀏覽器訪問
# http://192.168.50.249:8069
```

### Step 2: 執行納管

#### 方式 1: 使用 PowerShell 腳本（推薦）

```powershell
cd "c:\wuchang V5.1.0"
.\scripts\enroll_v3_mix_edla_gl.ps1
```

#### 方式 2: 使用 Python 腳本

```bash
cd "c:\wuchang V5.1.0"
python scripts\enroll_android_pos.py \
  --device-name "v3_mix_edla_gl" \
  --ip "192.168.50.86" \
  --port 41895 \
  --android-version "13" \
  --developer-mode \
  --vm-ip "192.168.50.249"
```

#### 方式 3: 使用 curl（手動納管）

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

### Step 3: 驗證納管結果

納管成功後，您應該看到：

```
✅ 設備納管成功！

設備資訊：
  設備 ID: ANDROID_V3_MIX_EDLA_GL
  設備名稱: v3_mix_edla_gl
  IP 地址: 192.168.50.86
  通訊埠: 41895
  狀態: online
  開發者模式: True
  Demo Mode: False

偵錯選項：
  USB 偵錯: True
  GPU 偵錯: True
  WiFi 偵錯: True
```

### Step 4: 在 Odoo 中確認

1. 登入 Odoo 管理界面：`http://192.168.50.84:8069/web/login`
2. 進入「基礎設施」→「設備」
3. 搜尋設備名稱 `v3_mix_edla_gl`
4. 確認設備狀態為「在線」

---

## 🔧 偵錯選項說明

### USB 偵錯

**用途**：
- 透過 USB 連接進行 ADB 調試
- 安裝和更新應用程式
- 查看設備日誌

**設定位置**：
- 設定 → 關於手機 → 連續點擊「版本號碼」7 次
- 設定 → 開發者選項 → USB 偵錯

### GPU 偵錯

**用途**：
- 圖形效能調試
- 渲染效能分析
- 顯示問題診斷

**設定位置**：
- 設定 → 開發者選項 → GPU 渲染設定檔

### WiFi 偵錯

**用途**：
- 無線 ADB 連接（不需要 USB 線）
- 遠程調試和管理
- 更方便的設備管理

**設定位置**：
- 設定 → 開發者選項 → WiFi 偵錯
- 需要配對碼進行連接

**使用方式**：
```bash
# 在電腦上連接設備（需要配對碼）
adb connect 192.168.50.86:41895
```

---

## 📱 Google Workspace MDM 設定（推薦）

### Step 1: 註冊設備到 Google Workspace

1. **登入 Google Workspace Admin Console**
   - 網址: `https://admin.google.com`
   - 帳號: `admin@wuchang.life`

2. **註冊設備**
   - 進入「設備」→「行動裝置與端點」→「Android」
   - 選擇「註冊設備」
   - 輸入設備資訊：
     - 設備名稱: `v3_mix_edla_gl`
     - 設備 ID: `ANDROID_V3_MIX_EDLA_GL`
     - IP 地址: `192.168.50.86`
     - 通訊埠: `41895`
     - 組織單位: `POS-重新總店`

### Step 2: 設定 Kiosk 模式

1. **進入設備設定**
   - 選擇設備 `v3_mix_edla_gl`
   - 進入「應用程式」→「Kiosk 模式」

2. **設定單一應用 Kiosk 模式**
   - 選擇「單一應用 Kiosk 模式」
   - 指定應用: `Odoo POS`（需要先安裝）
   - 啟用「鎖定到應用程式」
   - 啟用「防止離開應用程式」

3. **設定應用程式政策**
   - 強制安裝: `Odoo POS App`
   - 允許應用: 必要的 POS 相關應用
   - 禁止應用: 其他未授權應用

### Step 3: 設定安全策略

1. **設備加密**
   - 強制啟用設備加密
   - 確保資料安全

2. **密碼策略**
   - 最少 8 位元
   - 複雜度要求（可選）

3. **螢幕鎖定**
   - 自動鎖定時間: 5 分鐘無操作
   - 鎖定方式: PIN 碼或密碼

### Step 4: 配置 Google Drive 同步

1. **建立 POS 資料資料夾**
   - 在 Google Drive 建立 `POS-重新總店` 資料夾
   - 設定適當的權限

2. **設定自動同步**
   - 在設備上安裝 Google Drive 應用
   - 設定自動同步到指定資料夾
   - 啟用離線存取

---

## 🔍 故障排除

### 問題 1: 無法連接到 VM 伺服器

**錯誤訊息**：
```
❌ 無法連接到 VM 伺服器 192.168.50.84:8069
```

**解決方案**：
1. 確認 VM 伺服器的 Odoo 服務正在運行
2. 檢查網路連線：`ping 192.168.50.84`
3. 檢查防火牆設定
4. 確認 IP 地址正確

### 問題 2: 納管 API 端點不存在

**錯誤訊息**：
```
404 Not Found
```

**解決方案**：
1. 確認 Odoo 服務已重啟以載入新的控制器
2. 檢查 URL 是否正確：`http://192.168.50.84:8069/api/device/enroll/android`
3. 查看 Odoo 日誌確認控制器已載入

### 問題 3: 設備無法被識別

**解決方案**：
1. 確認設備 IP 地址正確（192.168.50.86）
2. 確認設備與 VM 伺服器在同一網路
3. 檢查設備的網路連線狀態

### 問題 4: WiFi 偵錯無法連接

**解決方案**：
1. 確認 WiFi 偵錯已開啟
2. 確認設備和電腦在同一 WiFi 網路
3. 使用配對碼進行連接：
   ```bash
   adb pair 192.168.50.86:41895
   # 輸入配對碼後
   adb connect 192.168.50.86:41895
   ```

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

5. **Kiosk 模式**
   - 鎖定到 Odoo POS 應用
   - 防止離開應用程式
   - 專用設備模式

---

## 📋 納管檢查清單

### 設備設定

- [x] 開發者模式已開啟
- [x] USB 偵錯已開啟
- [x] GPU 偵錯已開啟
- [x] WiFi 偵錯已開啟
- [x] Demo Mode 保持關閉（不需要）
- [x] 網路連線正常
- [x] IP 地址: 192.168.50.86
- [x] 通訊埠: 41895

### 納管執行

- [ ] VM 伺服器 Odoo 服務正在運行
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
- [ ] Google Drive 同步已配置

### 功能測試

- [ ] 可以從 Odoo 發送控制指令到設備
- [ ] 設備可以接收並執行指令
- [ ] Google Drive 同步功能正常
- [ ] POS 應用可以正常運作
- [ ] Kiosk 模式正常運作

---

## 🎯 總結

### ✅ 設備設定狀態

- **開發者模式**: ✅ 已開啟
- **USB 偵錯**: ✅ 已開啟
- **GPU 偵錯**: ✅ 已開啟
- **WiFi 偵錯**: ✅ 已開啟
- **Demo Mode**: ❌ 不需要開啟

### 📝 下一步

1. **確認 VM 伺服器運行**：確保 Odoo 服務正在運行
2. **執行納管**：使用提供的腳本或 API 進行納管
3. **Google Workspace MDM**：註冊設備並設定 Kiosk 模式
4. **測試功能**：確認所有功能正常運作

---

**文件版本**: 1.0  
**最後更新**: 2025-01-07  
**維護者**: 小J (Little J)  
**設備**: v3_mix_edla_gl (Android 13, IP: 192.168.50.86:41895)
