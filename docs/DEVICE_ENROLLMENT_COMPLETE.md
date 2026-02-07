# 設備納管完整指南

**文件日期**: 2025-01-07  
**系統版本**: Wuchang OS V5.1.0

---

## 📋 納管設備類型

### 1. POS 設備
- **設備**: v3_mix_edla_gl (Android 13)
- **IP**: 192.168.50.86
- **狀態**: 待納管

### 2. 客戶顯示器 (Customer Display)
- **用途**: 顯示 POS 交易資訊給客戶
- **URL**: http://192.168.50.249:8069/pos/customer_display
- **狀態**: 待納管

### 3. Chrome OS 設備
- **用途**: 昨日已納管的 Chrome OS 設備
- **端口**: 3477
- **狀態**: 需批量寫入管理

---

## 🚀 納管方式

### 方式 1: API 納管（推薦）

#### 客戶顯示器納管
```powershell
python scripts\enroll_customer_display.py `
    --device-name "Customer Display" `
    --ip "192.168.50.XXX" `
    --display-url "http://192.168.50.249:8069/pos/customer_display" `
    --vm-ip "192.168.50.249"
```

#### Chrome OS 設備批量納管
```powershell
# 1. 建立設備清單檔案 (chrome_os_devices.json)
python scripts\batch_enroll_chrome_os_devices.py --create-template

# 2. 編輯 chrome_os_devices.json，填入設備資訊

# 3. 批量納管
python scripts\batch_enroll_chrome_os_devices.py `
    --devices-file "chrome_os_devices.json" `
    --vm-ip "192.168.50.249"
```

### 方式 2: 批量納管腳本

```powershell
.\scripts\enroll_all_devices.ps1 `
    -VMIP "192.168.50.249" `
    -CustomerDisplayIP "192.168.50.XXX" `
    -CustomerDisplayName "Customer Display" `
    -ChromeOSDevicesFile "chrome_os_devices.json"
```

### 方式 3: Odoo UI 手動納管

1. 訪問: http://192.168.50.249:8069/web/login
2. 進入「基礎設施」→「設備」→「建立」
3. 填入設備資訊：
   - **客戶顯示器**:
     - 名稱: Customer Display
     - IP: 192.168.50.XXX
     - 類型: Customer Display
     - 狀態: Online
   - **Chrome OS 設備**:
     - 名稱: Chrome OS Device
     - IP: 192.168.50.XXX
     - 類型: Chrome OS
     - 狀態: Online

---

## 📊 設備清單範本

### Chrome OS 設備清單 (chrome_os_devices.json)

```json
{
  "devices": [
    {
      "name": "Chrome OS Device 1",
      "ip": "192.168.50.XXX",
      "port": 3477,
      "mac": "XX:XX:XX:XX:XX:XX"
    },
    {
      "name": "Chrome OS Device 2",
      "ip": "192.168.50.XXX",
      "port": 3477,
      "mac": ""
    }
  ]
}
```

---

## ✅ 納管後確認

納管成功後，在 Odoo 中應該可以看到：

1. **POS 設備**
   - 設備名稱: v3_mix_edla_gl
   - IP 地址: 192.168.50.86
   - 類型: POS Terminal
   - 狀態: Online

2. **客戶顯示器**
   - 設備名稱: Customer Display
   - IP 地址: 192.168.50.XXX
   - 類型: Customer Display
   - 狀態: Online

3. **Chrome OS 設備**
   - 設備名稱: Chrome OS Device X
   - IP 地址: 192.168.50.XXX
   - 類型: Chrome OS
   - 狀態: Online

---

## 🔗 API 端點

### 客戶顯示器納管
- **端點**: `/api/device/enroll/customer_display`
- **方法**: POST
- **格式**: JSON

### Chrome OS 設備納管
- **端點**: `/api/device/enroll/chrome_os`
- **方法**: POST
- **格式**: JSON

---

## 📋 後續步驟

1. **在 Odoo 中確認設備記錄**
   - 檢查所有設備是否正確納管
   - 確認設備狀態為 Online

2. **在 Sister Control 中配置**
   - 配置客戶顯示器 URL
   - 配置 POS URL
   - 測試設備連線

3. **測試設備功能**
   - 測試客戶顯示器顯示功能
   - 測試 Chrome OS 設備連線
   - 測試 POS 設備功能

---

**文件版本**: 1.0  
**最後更新**: 2025-01-07  
**維護者**: 小J (Little J)
