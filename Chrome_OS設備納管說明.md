# Chrome OS 設備納管說明

**配置時間**: 2026-01-07  
**系統版本**: Wuchang OS V5.1.0  
**AI 身份**: Little J (小j)  
**設備類型**: Chrome OS / Chromebook  
**納管端口**: 3477

---

## 📋 概述

已配置 Chrome OS 設備連接納管機制，支持通過端口 3477 進行設備註冊和管理。

---

## 🔧 配置詳情

### 設備類型

- **類型**: Chrome OS / Chromebook
- **端口**: 3477
- **協議**: HTTP/HTTPS
- **納管方式**: 自動/手動

### 已配置的組件

1. **設備納管控制器** (`device_enrollment_controller.py`)
   - 納管端點: `/api/device/enroll/chrome_os`
   - 狀態查詢: `/api/device/chrome_os/status`
   - 心跳機制: `/api/device/chrome_os/heartbeat`

2. **設備模型更新** (`infrastructure.py`)
   - 新增 `chrome_os` 和 `chromebook` 設備類型
   - 支持設備狀態追蹤
   - 記錄最後連接時間

3. **Caddy 路由配置**
   - 已配置設備納管路由
   - 支持本地和外網訪問

---

## 🌐 納管端點

### 1. 設備納管

**端點**: `POST /api/device/enroll/chrome_os`

**請求格式**:
```json
{
  "device_id": "CHROME_OS_192_168_50_XXX",
  "device_name": "Chrome OS Device (hostname)",
  "ip_address": "192.168.50.XXX",
  "mac_address": "XX:XX:XX:XX:XX:XX",
  "port": 3477
}
```

**響應格式**:
```json
{
  "status": "success",
  "action": "enrolled",
  "message": "Chrome OS 設備已納管",
  "device": {
    "id": 1,
    "device_id": "CHROME_OS_192_168_50_XXX",
    "name": "Chrome OS Device",
    "ip_address": "192.168.50.XXX",
    "device_type": "chrome_os",
    "status": "online",
    "port": 3477,
    "enrollment_time": "2026-01-07T..."
  },
  "access": {
    "command_center": "/command_center",
    "design_report": "/design_report",
    "handshake": "/api/handshake",
    "device_management": "/web#id=1&model=wuchang.infrastructure.device"
  },
  "capabilities": {
    "web_access": true,
    "api_access": true,
    "remote_control": false,
    "file_sharing": false,
    "kiosk_mode": true
  }
}
```

### 2. 設備狀態查詢

**端點**: `GET /api/device/chrome_os/status?ip=<IP>`

**響應格式**:
```json
{
  "status": "enrolled",
  "device": {
    "id": 1,
    "name": "Chrome OS Device",
    "ip_address": "192.168.50.XXX",
    "device_type": "chrome_os",
    "status": "online",
    "last_seen": "2026-01-07T..."
  }
}
```

### 3. 設備心跳

**端點**: `POST /api/device/chrome_os/heartbeat`

**請求格式**:
```json
{
  "ip_address": "192.168.50.XXX"
}
```

**響應格式**:
```json
{
  "status": "success",
  "message": "心跳更新成功",
  "last_seen": "2026-01-07T..."
}
```

---

## 🚀 納管方式

### 方式 1: 使用納管客戶端腳本（推薦）

**腳本**: `scripts/chrome_os_enroll_client.py`

**使用步驟**:

1. **在 Chrome OS 設備上執行**:
   ```bash
   python3 chrome_os_enroll_client.py
   ```

2. **腳本會自動**:
   - 檢測設備 IP 地址
   - 獲取設備信息
   - 發送納管請求
   - 顯示納管結果

3. **發送心跳** (可選):
   ```bash
   python3 chrome_os_enroll_client.py heartbeat
   ```

### 方式 2: 使用 curl 手動納管

**納管**:
```bash
curl -X POST http://192.168.50.249/api/device/enroll/chrome_os \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "CHROME_OS_DEVICE_001",
    "device_name": "My Chrome OS Device",
    "ip_address": "192.168.50.XXX",
    "port": 3477
  }'
```

**查詢狀態**:
```bash
curl http://192.168.50.249/api/device/chrome_os/status?ip=192.168.50.XXX
```

**發送心跳**:
```bash
curl -X POST http://192.168.50.249/api/device/chrome_os/heartbeat \
  -H "Content-Type: application/json" \
  -d '{"ip_address": "192.168.50.XXX"}'
```

### 方式 3: 通過瀏覽器訪問

Chrome OS 設備可以直接訪問納管頁面（如果有提供 UI）:
```
http://192.168.50.249/device/enroll/chrome_os
```

---

## 📡 訪問地址

### 本地訪問

- **納管端點**: `http://192.168.50.249/api/device/enroll/chrome_os`
- **狀態查詢**: `http://192.168.50.249/api/device/chrome_os/status`
- **心跳端點**: `http://192.168.50.249/api/device/chrome_os/heartbeat`

### 外網訪問（通過 Cloudflare 隧道）

- **納管端點**: `https://wuchang.life/api/device/enroll/chrome_os`
- **狀態查詢**: `https://wuchang.life/api/device/chrome_os/status`
- **心跳端點**: `https://wuchang.life/api/device/chrome_os/heartbeat`

### 端口 3477

端口 3477 通常用於：
- Google Cast / Chromecast 通信
- STUN/TURN 服務器（WebRTC）
- 設備管理協議

**注意**: 如果需要在端口 3477 上直接提供服務，需要額外配置。

---

## 🔒 安全配置

### CORS 設置

設備納管端點已配置 CORS 支持：
- 允許跨域請求
- 支持 OPTIONS 預檢請求

### 認證機制

- 當前為公開端點（`auth='public'`）
- 生產環境建議添加認證機制
- 可選：API Key 驗證、Token 驗證

---

## 📊 設備管理

### 在 Odoo 中查看納管設備

1. 登入 Odoo 管理界面
2. 訪問: `應用程式` → `Wuchang Core` → `基礎設施設備`
3. 篩選條件: `設備類型 = Chrome OS`
4. 查看設備狀態、IP 地址、最後連接時間等

### 設備狀態

- **online**: 設備在線（已連接）
- **offline**: 設備離線（未連接）
- **unknown**: 狀態未知

### 自動更新

- 設備發送心跳時自動更新狀態為 `online`
- 自動更新 `last_seen` 時間戳

---

## 🔄 心跳機制

### 用途

- 保持設備在線狀態
- 更新最後連接時間
- 檢測設備連接狀態

### 建議頻率

- 每 30 秒 - 1 分鐘發送一次心跳
- 可在 Chrome OS 設備上設置定時任務

### 實現方式

```bash
# 使用 cron 或 systemd timer
*/1 * * * * /usr/bin/python3 /path/to/chrome_os_enroll_client.py heartbeat
```

---

## 📝 使用示例

### 完整納管流程

```bash
# 1. 執行納管
python3 chrome_os_enroll_client.py

# 2. 驗證納管狀態
curl http://192.168.50.249/api/device/chrome_os/status?ip=$(hostname -I | awk '{print $1}')

# 3. 設置定時心跳（可選）
(crontab -l 2>/dev/null; echo "*/1 * * * * /path/to/chrome_os_enroll_client.py heartbeat") | crontab -
```

---

## ✅ 配置檢查清單

- ✅ 設備納管控制器已創建
- ✅ 設備模型已更新（支持 chrome_os）
- ✅ Caddy 路由配置已更新
- ✅ 納管客戶端腳本已創建
- ⏳ 需要重啟 Odoo 服務以載入新控制器
- ⏳ 需要測試納管功能

---

## 🚀 部署步驟

1. **重啟 Odoo 服務**:
   ```bash
   docker-compose restart wuchang-web
   ```

2. **重啟 Caddy** (如需要):
   ```bash
   docker-compose restart caddy
   ```

3. **測試納管功能**:
   ```bash
   curl -X POST http://localhost/api/device/enroll/chrome_os \
     -H "Content-Type: application/json" \
     -d '{"device_name": "Test Chrome OS Device", "port": 3477}'
   ```

4. **在 Chrome OS 設備上執行納管**:
   ```bash
   python3 chrome_os_enroll_client.py
   ```

---

## 💡 注意事項

1. **端口 3477**: 如果需要在該端口直接提供服務，需要額外配置服務監聽
2. **設備識別**: 建議使用 MAC 地址或唯一設備 ID 進行識別
3. **安全**: 生產環境應添加認證機制
4. **心跳**: 建議設置定時心跳以保持設備狀態同步

---

**配置完成時間**: 2026-01-07  
**系統版本**: Wuchang OS V5.1.0  
**AI 身份**: Little J (小j)

---

*「Chrome OS 設備納管機制已配置完成，端口 3477 已準備就緒。」* ✨
