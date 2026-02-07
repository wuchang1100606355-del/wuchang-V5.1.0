# Chrome OS 設備納管指南

**文件日期**: 2025-01-07  
**系統版本**: Wuchang OS V5.1.0

---

## 🎯 重要說明

**客戶顯示器就是 Chrome OS 設備**

- 客戶顯示器是 Chrome OS 設備的一種用途
- 所有 Chrome OS 設備都使用相同的納管 API 端點
- 通過 `device_purpose` 欄位區分用途：
  - `customer_display`: 客戶顯示器
  - `signage`: 數位看板
  - `other`: 其他用途

---

## 📋 如何區分不同的 Chrome OS 設備

### 1. 通過 IP 地址
每個 Chrome OS 設備都有唯一的 IP 地址

### 2. 通過設備名稱
為每個設備設定不同的名稱（例如：Customer Display 1, Customer Display 2）

### 3. 通過 MAC 地址
每個設備都有唯一的 MAC 地址

### 4. 通過用途標記
使用 `device_purpose` 欄位標記設備用途

---

## 🚀 納管方式

### 方式 1: 納管客戶顯示器（Chrome OS）

```powershell
python scripts\enroll_chrome_os_customer_display.py `
    --device-name "Customer Display 1" `
    --ip "192.168.50.XXX" `
    --port 3477 `
    --display-url "http://192.168.50.249:8069/pos/customer_display"
```

### 方式 2: 批量納管多個 Chrome OS 設備

#### 建立設備清單檔案 (chrome_os_devices.json)

```json
{
  "devices": [
    {
      "name": "Chrome OS Customer Display 1",
      "ip": "192.168.50.XXX",
      "port": 3477,
      "mac": "XX:XX:XX:XX:XX:XX",
      "purpose": "customer_display",
      "display_url": "http://192.168.50.249:8069/pos/customer_display"
    },
    {
      "name": "Chrome OS Customer Display 2",
      "ip": "192.168.50.YYY",
      "port": 3477,
      "mac": "YY:YY:YY:YY:YY:YY",
      "purpose": "customer_display",
      "display_url": "http://192.168.50.249:8069/pos/customer_display"
    },
    {
      "name": "Chrome OS Signage",
      "ip": "192.168.50.ZZZ",
      "port": 3477,
      "mac": "ZZ:ZZ:ZZ:ZZ:ZZ:ZZ",
      "purpose": "signage"
    }
  ]
}
```

#### 執行批量納管

```powershell
python scripts\batch_enroll_chrome_os_devices.py `
    --devices-file "chrome_os_devices.json"
```

### 方式 3: 直接使用 Chrome OS 納管 API

```python
import requests

enrollment_data = {
    'device_name': 'Customer Display 1',
    'ip_address': '192.168.50.XXX',
    'port': 3477,
    'device_purpose': 'customer_display',  # 標記為客戶顯示器
    'display_url': 'http://192.168.50.249:8069/pos/customer_display'
}

response = requests.post(
    'http://192.168.50.249:8069/api/device/enroll/chrome_os',
    json=enrollment_data
)
```

---

## 📊 設備區分範例

### 範例 1: 兩台客戶顯示器

| 設備 | IP 地址 | 設備名稱 | 用途 |
|------|---------|----------|------|
| 客戶顯示器 1 | 192.168.50.100 | Customer Display 1 | customer_display |
| 客戶顯示器 2 | 192.168.50.101 | Customer Display 2 | customer_display |

**納管方式**：
```powershell
# 納管第一台
python scripts\enroll_chrome_os_customer_display.py `
    --device-name "Customer Display 1" `
    --ip "192.168.50.100"

# 納管第二台
python scripts\enroll_chrome_os_customer_display.py `
    --device-name "Customer Display 2" `
    --ip "192.168.50.101"
```

### 範例 2: 客戶顯示器 + 數位看板

| 設備 | IP 地址 | 設備名稱 | 用途 |
|------|---------|----------|------|
| 客戶顯示器 | 192.168.50.100 | Customer Display | customer_display |
| 數位看板 | 192.168.50.200 | Digital Signage | signage |

**納管方式**：
```powershell
# 納管客戶顯示器
python scripts\enroll_chrome_os_customer_display.py `
    --device-name "Customer Display" `
    --ip "192.168.50.100"

# 納管數位看板（使用通用 Chrome OS 納管）
python scripts\batch_enroll_chrome_os_devices.py `
    --devices-file "signage_device.json"
```

---

## ✅ 納管後確認

納管成功後，在 Odoo 中應該可以看到：

1. **設備列表**
   - 所有 Chrome OS 設備（包括客戶顯示器）
   - 每個設備有唯一的 IP 地址和名稱

2. **設備資訊**
   - 設備名稱
   - IP 地址
   - 用途標記（device_purpose）
   - 顯示 URL（如果是客戶顯示器）

3. **設備狀態**
   - Online/Offline
   - 最後連線時間

---

## 🔗 API 端點

### Chrome OS 設備納管（包括客戶顯示器）
- **端點**: `/api/device/enroll/chrome_os`
- **方法**: POST
- **格式**: JSON
- **參數**:
  - `device_name`: 設備名稱
  - `ip_address`: IP 地址
  - `port`: 通訊埠（預設: 3477）
  - `mac_address`: MAC 地址（可選）
  - `device_purpose`: 用途（'customer_display', 'signage', 'other'）
  - `display_url`: 顯示 URL（客戶顯示器用）

---

## 💡 總結

1. **客戶顯示器 = Chrome OS 設備**
   - 使用相同的納管 API
   - 通過 `device_purpose` 標記用途

2. **如何區分不同設備**
   - IP 地址（主要區分方式）
   - 設備名稱
   - MAC 地址
   - 用途標記

3. **納管方式**
   - 單一設備：使用 `enroll_chrome_os_customer_display.py`
   - 批量設備：使用 `batch_enroll_chrome_os_devices.py` + JSON 檔案

---

**文件版本**: 1.0  
**最後更新**: 2025-01-07  
**維護者**: 小J (Little J)
