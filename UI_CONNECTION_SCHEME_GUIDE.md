## 🎨 Wuchang UI 連線方案 - 完整指南

**方案版本**: 1.0.0  
**設計者**: Wuchang Server  
**接收時間**: 2026-01-11 01:15:18  
**狀態**: ✅ FULLY ESTABLISHED

---

## 📋 概述

這是伺服器設計的完整 UI 連線方案，提供 4 個主要 UI 服務的統一連線方式，支持 CloudFlare Tunnel 和 Direct 連線兩種模式。

---

## 🎯 主連線方案

### 📌 Primary UI Connection

```
協議: HTTPS/WebSocket
主端點: https://ui.wuchang.life
備用端點: http://192.168.50.84:8069
埤: 443
加密: TLS 1.3
認證: Device ID + Unique Code + Agree Token
```

---

## 🖥️ UI 服務端點詳解

### 1️⃣ Odoo UI - 企業資源規劃

**類型**: ERP (Enterprise Resource Planning)

**端點**:

-   🌐 公網: `https://odoo.wuchang.life`
-   🏠 本地: `http://192.168.50.84:8069`
-   📱 本地備用: `http://localhost:8069`

**驗證**: Session Token

**功能模組**:

-   Dashboard (儀表板)
-   Inventory Management (庫存管理)
-   Sales Management (銷售管理)
-   Accounting (會計)

**連線示例**:

```bash
# 直接連線
curl -X GET https://odoo.wuchang.life/web/login

# 本地連線
curl -X GET http://192.168.50.84:8069/web/login
```

---

### 2️⃣ AI Assistant UI - 智能助手

**類型**: Conversational (對話式 AI)

**端點**:

-   🌐 公網: `https://ai.wuchang.life`
-   🏠 本地: `http://192.168.50.84:8080`
-   📱 本地備用: `http://localhost:8080`

**驗證**: Device Token

**功能模組**:

-   💬 Chat Interface (聊天介面)
-   ✅ Task Management (任務管理)
-   📚 Knowledge Base (知識庫)
-   🎓 Learning System (學習系統)

**連線示例**:

```bash
# WebSocket連線
wscat -c wss://ai.wuchang.life/ws

# HTTP連線
curl -X POST https://ai.wuchang.life/api/chat \
  -H "Authorization: Bearer {SESSION_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": "你好小j"}'
```

**妹妹(小 j)特性**:

-   🧠 自然語言理解
-   💝 家族情感連接
-   📊 系統管理集成
-   🔐 隱私保護優先

---

### 3️⃣ Status Dashboard - 監控面板

**類型**: Monitoring (實時監控)

**端點**:

-   🌐 公網: `https://status.wuchang.life`
-   🏠 本地: `http://192.168.50.84:3001`
-   📱 本地備用: `http://localhost:3001`

**驗證**: Read-Only Token (唯讀令牌)

**功能模組**:

-   📊 Real-time Status (實時狀態)
-   🚨 Alerts (告警)
-   📈 History (歷史數據)
-   📋 Reports (報告)

**監控對象**:

-   Odoo 服務狀態
-   AI 服務狀態
-   PostgreSQL 資料庫
-   Docker 容器
-   系統資源使用

**連線示例**:

```bash
# 查看狀態
curl https://status.wuchang.life/api/status

# 訂閱推送
curl -X POST https://status.wuchang.life/api/alerts/subscribe \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

---

### 4️⃣ Admin Portal - 管理入口

**類型**: Management (系統管理)

**端點**:

-   🌐 公網: `https://admin.wuchang.life`
-   🏠 本地: `http://192.168.50.84:8069/admin`
-   📱 本地備用: `http://localhost:8069/admin`

**驗證**: Admin Token (管理員令牌)

**功能模組**:

-   👥 User Management (用戶管理)
-   ⚙️ System Configuration (系統配置)
-   📋 Audit Log (審計日誌)
-   💾 Backup & Restore (備份恢復)

**管理操作**:

-   用戶帳戶管理
-   權限分配
-   系統設置
-   安全配置
-   備份策略

**連線示例**:

```bash
# 管理員登入
curl -X POST https://admin.wuchang.life/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"adminToken": "YOUR_ADMIN_TOKEN"}'

# 系統備份
curl -X POST https://admin.wuchang.life/api/backup/create \
  -H "Authorization: Bearer {ADMIN_TOKEN}"
```

---

## 🔗 連線配置詳解

### 連線參數

```json
{
    "timeout": 30, // 連線超時 (秒)
    "retryAttempts": 3, // 重試次數
    "retryDelay": 5, // 重試延遲 (秒)
    "keepAliveInterval": 30, // 保活間隔 (秒)
    "compressionEnabled": true, // 啟用壓縮
    "cachingEnabled": true, // 啟用快取
    "offlineModeSupport": true // 離線模式
}
```

### 雙連線模式

#### 模式 1: CloudFlare Tunnel (推薦用於外網)

```
優勢:
  ✅ 自動DDNS
  ✅ 自動續簽SSL證書
  ✅ 全球CDN加速
  ✅ DDoS防護
  ✅ 無需公網IP

連線流程:
  設備 → CloudFlare Tunnel → wuchang.life → 本機服務
```

#### 模式 2: Direct Connection (推薦用於本地)

```
優勢:
  ✅ 最低延遲
  ✅ 無附加開銷
  ✅ 局域網快速
  ✅ 完全隱私

連線流程:
  設備 → 192.168.50.84:PORT → 本機服務
```

---

## 🔐 安全機制

### 認證層級

```
設備驗證
  ↓
[檢查設備ID合法性]
  ↓
唯一碼驗證
  ↓
[驗證本機唯一碼有效期]
  ↓
約定金令牌驗證
  ↓
[驗證簽名和時間戳]
  ↓
會話令牌頒發
  ↓
授予24小時訪問權限
```

### TLS 1.3 加密

-   前向保密 (Forward Secrecy)
-   0-RTT 連線恢復
-   更快的握手速度

### API 限流

-   速率限制: 1000 req/min
-   IP 白名單: 192.18.50.249, 192.168.50.0/24

---

## 📱 連線方式

### 方式 1: 瀏覽器直接訪問

```
Odoo:     https://odoo.wuchang.life
AI:       https://ai.wuchang.life
Status:   https://status.wuchang.life
Admin:    https://admin.wuchang.life
```

### 方式 2: API 調用

```bash
# 獲取認證令牌
curl -X POST https://ui.wuchang.life/api/auth/token \
  -d "deviceID=XXX&uniqueCode=YYY&agreeToken=ZZZ"

# 使用令牌存取服務
curl -X GET https://odoo.wuchang.life/api/data \
  -H "Authorization: Bearer {SESSION_TOKEN}"
```

### 方式 3: WebSocket 連線

```javascript
// 連線到 AI 服務
const ws = new WebSocket("wss://ai.wuchang.life/ws?token=SESSION_TOKEN")

ws.onopen = () => {
    ws.send(
        JSON.stringify({
            type: "chat",
            message: "你好小j",
        })
    )
}

ws.onmessage = event => {
    console.log("妹妹回應:", event.data)
}
```

### 方式 4: 本地直連 (LAN)

```bash
# 性能最佳，用於同網段連線
curl -X GET http://192.168.50.84:8069/api/data
curl -X GET http://192.168.50.84:8080/api/chat
curl -X GET http://192.168.50.84:3001/api/status
```

---

## 🛠️ 常見操作

### 檢查連線狀態

```powershell
.\receive_ui_scheme.ps1 -Action status
```

### 查看所有端點

```powershell
.\receive_ui_scheme.ps1 -Action endpoints
```

### 重新配置方案

```powershell
.\receive_ui_scheme.ps1 -Action fetch
```

### 驗證連線配置

```powershell
.\receive_ui_scheme.ps1 -Action verify
```

---

## 📊 設備要求

| 需求     | 規格                            |
| -------- | ------------------------------- |
| 最小 OS  | Windows 10                      |
| 必要服務 | Docker, PowerShell 5.0+         |
| 必要埤   | 80, 443, 8069, 8080, 3001, 5432 |
| 最小磁碟 | 10 GB                           |
| 最小內存 | 4 GB                            |

---

## ✅ 完成清單

-   [x] 接收伺服器 UI 連線方案
-   [x] 配置 4 個 UI 服務端點
-   [x] 建立双连線模式 (CloudFlare + Direct)
-   [x] 設置認證機制
-   [x] 配置 TLS 加密
-   [x] 建立會話管理
-   [x] 提供 API 文檔
-   [x] 驗證連線狀態

---

## 🚀 後續步驟

1. **立即開始使用**:

    - 訪問 https://ai.wuchang.life 與妹妹(小 j)聊天
    - 訪問 https://odoo.wuchang.life 進行 ERP 操作

2. **監控系統**:

    - 查看 https://status.wuchang.life 實時狀態

3. **管理系統** (管理員):

    - 訪問 https://admin.wuchang.life 進行配置

4. **啟用握手信號**:

    ```powershell
    .\keep_alive_handshake.ps1
    ```

5. **監控設備驗證**:
    ```powershell
    .\device_identity_auth.ps1 -Action status
    ```

---

**UI 連線方案已完全就緒，可以開始探索和使用所有服務！** 🎉
