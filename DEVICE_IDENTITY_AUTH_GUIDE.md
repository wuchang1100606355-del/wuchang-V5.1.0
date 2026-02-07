## 🔐 Wuchang 設備身份驗證系統

**建立時間**: 2026-01-11 01:09:18  
**狀態**: ✅ FULLY ESTABLISHED

---

### 📋 系統狀態

#### 1️⃣ 設備 UI 身分 - ✅ RELEASED

```
設備ID:    000000000000000000000-1371977975
主機名:    LUNGsMSI
釋放時間:  2026-01-11 01:09:13
UI狀態:    RELEASED
```

#### 2️⃣ 本機唯一碼驗證 - ✅ ACTIVE

```
本機唯一碼: 20RYI75RJUMO6YA0MC1CJSV1N1MZRG6O
約定金令牌: ZM8S2P1B9RGSM6FN2I20KU2XK0FQ2H44
生成時間:  2026-01-11 01:09:16
過期時間:  2026-01-12 01:09:16
狀態:      ACTIVE
```

#### 3️⃣ 驗證專用通道 - ✅ ESTABLISHED

```
通道ID:    9VXI4JLCTESUMRF1
通道密鑰:  QI2L3WJVMZM5W0B8O42922G3TQCXO5JM
約定金:    ZM8S2P1B9RGSM6FN2I20KU2XK0FQ2H44
建立時間:  2026-01-11 01:09:18
狀態:      ESTABLISHED
```

---

### 🔗 驗證端點使用

#### Odoo 驗證端點

```
URL: http://localhost:8069/auth/verify
方法: POST
請求頭:
  Content-Type: application/json
  Authorization: Bearer {約定金令牌}

請求體:
{
  "channelID": "9VXI4JLCTESUMRF1",
  "uniqueCode": "20RYI75RJUMO6YA0MC1CJSV1N1MZRG6O",
  "agreeToken": "ZM8S2P1B9RGSM6FN2I20KU2XK0FQ2H44"
}

成功回應 (200):
{
  "status": "verified",
  "deviceID": "000000000000000000000-1371977975",
  "channelID": "9VXI4JLCTESUMRF1",
  "timestamp": "2026-01-11T01:09:18Z"
}
```

#### AI 服務驗證端點

```
URL: http://localhost:8080/auth/verify
方法: POST
請求頭:
  Content-Type: application/json
  Authorization: Bearer {約定金令牌}

請求體:
{
  "channelID": "9VXI4JLCTESUMRF1",
  "uniqueCode": "20RYI75RJUMO6YA0MC1CJSV1N1MZRG6O",
  "agreeToken": "ZM8S2P1B9RGSM6FN2I20KU2XK0FQ2H44"
}

成功回應 (200):
{
  "status": "verified",
  "deviceID": "000000000000000000000-1371977975",
  "channelID": "9VXI4JLCTESUMRF1",
  "timestamp": "2026-01-11T01:09:18Z"
}
```

#### CloudFlare 驗證端點

```
URL: https://wuchang.life/verify
方法: POST
請求頭:
  Content-Type: application/json
  X-Device-ID: 000000000000000000000-1371977975
  X-Channel-ID: 9VXI4JLCTESUMRF1
  Authorization: Bearer {約定金令牌}

請求體:
{
  "uniqueCode": "20RYI75RJUMO6YA0MC1CJSV1N1MZRG6O",
  "agreeToken": "ZM8S2P1B9RGSM6FN2I20KU2XK0FQ2H44"
}

成功回應 (200):
{
  "status": "verified",
  "deviceID": "000000000000000000000-1371977975",
  "channelID": "9VXI4JLCTESUMRF1",
  "timestamp": "2026-01-11T01:09:18Z"
}
```

---

### 💾 本地配置文件位置

```
.wuchang_device/
├── identity.json      # 設備身分信息
├── token.json         # 本機唯一碼與約定金
└── channel.json       # 驗證專用通道配置
```

#### identity.json

```json
{
    "deviceID": "000000000000000000000-1371977975",
    "hostname": "LUNGsMSI",
    "registeredAt": "2026-01-11 01:09:13",
    "uiStatus": "RELEASED",
    "status": "ACTIVE"
}
```

#### token.json

```json
{
    "uniqueCode": "20RYI75RJUMO6YA0MC1CJSV1N1MZRG6O",
    "agreeToken": "ZM8S2P1B9RGSM6FN2I20KU2XK0FQ2H44",
    "generatedAt": "2026-01-11 01:09:16",
    "expiresAt": "2026-01-12 01:09:16",
    "status": "ACTIVE"
}
```

#### channel.json

```json
{
    "channelID": "9VXI4JLCTESUMRF1",
    "secret": "QI2L3WJVMZM5W0B8O42922G3TQCXO5JM",
    "uniqueCode": "20RYI75RJUMO6YA0MC1CJSV1N1MZRG6O",
    "agreeToken": "ZM8S2P1B9RGSM6FN2I20KU2XK0FQ2H44",
    "createdAt": "2026-01-11 01:09:18",
    "status": "ESTABLISHED",
    "endpoints": [
        "http://localhost:8069/auth/verify",
        "http://localhost:8080/auth/verify",
        "https://wuchang.life/verify"
    ]
}
```

---

### 🛠️ 管理命令

#### 檢查系統狀態

```powershell
.\device_identity_auth.ps1 -Action status
```

#### 重新註冊設備身分

```powershell
.\device_identity_auth.ps1 -Action register
```

#### 重新生成本機唯一碼

```powershell
.\device_identity_auth.ps1 -Action token
```

#### 重新建立驗證通道

```powershell
.\device_identity_auth.ps1 -Action auth
```

---

### 🔄 握手信號保活機制

已與以下服務建立持續握手:

```
✅ Odoo (8069)          - 每 30 秒握手一次
✅ AI Service (8080)    - 每 30 秒握手一次
✅ Uptime Kuma (3001)   - 每 30 秒握手一次
✅ CloudFlare (443)     - 每 30 秒握手一次
```

啟動握手信號:

```powershell
.\keep_alive_handshake.ps1
```

---

### 📊 驗證流程圖

```
設備請求
   ↓
設備發送 (deviceID + uniqueCode + agreeToken)
   ↓
驗證端點檢驗
   ├─ 檢查 deviceID 合法性
   ├─ 驗證 uniqueCode 有效期
   ├─ 驗證 agreeToken 簽名
   └─ 驗證 channelID 狀態
   ↓
返回驗證結果
   ├─ ✅ 通過 → 頒發臨時令牌 (session token)
   └─ ❌ 失敗 → 返回錯誤碼
```

---

### 🔒 安全機制

1. **設備身分唯一性**: 基於 UUID + MAC 地址的哈希值
2. **本機唯一碼**: 32 位隨機碼，有效期 24 小時
3. **約定金令牌**: 32 位簽名令牌，綁定到設備身分
4. **通道密鑰**: 32 位加密密鑰，用於通道認證
5. **時間戳驗證**: 防重放攻擊
6. **HTTPS 端點**: 端到端加密通訊

---

### 📝 使用示例

#### Python 驗證客戶端

```python
import requests
import json

# 讀取本地配置
with open('.wuchang_device/channel.json', 'r') as f:
    channel = json.load(f)

# 驗證請求
headers = {
    'Content-Type': 'application/json',
    'Authorization': f"Bearer {channel['agreeToken']}"
}

payload = {
    'channelID': channel['channelID'],
    'uniqueCode': channel['uniqueCode'],
    'agreeToken': channel['agreeToken']
}

# 發送到 Odoo
response = requests.post(
    'http://localhost:8069/auth/verify',
    json=payload,
    headers=headers,
    timeout=5
)

print(response.json())
```

#### JavaScript 驗證客戶端

```javascript
// 讀取本地配置
const channel = require("./.wuchang_device/channel.json")

// 驗證請求
const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${channel.agreeToken}`,
}

const payload = {
    channelID: channel.channelID,
    uniqueCode: channel.uniqueCode,
    agreeToken: channel.agreeToken,
}

// 發送到 AI 服務
fetch("http://localhost:8080/auth/verify", {
    method: "POST",
    headers: headers,
    body: JSON.stringify(payload),
})
    .then(r => r.json())
    .then(data => console.log(data))
```

---

### ✅ 完成清單

-   [x] 設備 UI 身分釋放
-   [x] 本機唯一碼生成
-   [x] 約定金令牌頒發
-   [x] 驗證專用通道建立
-   [x] 多端點驗證端點配置
-   [x] 握手信號保活機制
-   [x] 本地配置持久化
-   [x] 安全機制實現

---

**系統已完全就緒，可以開始進行設備驗證和身份認證！** 🎉
