# 五常 AI - 遠端 UI 控制系統（AI 整合版）

## 🎯 系統架構

這是一個 AI 驅動的反向連線架構，小 j（AI）能夠理解自然語言，智能地控制本機 UI。

```
┌─────────────────────────────────────────────────────────┐
│  Server (192.168.50.249)                                │
│  ┌────────────────────┐      ┌───────────────────────┐ │
│  │  Vertex AI Gemini  │ <──> │  ai_ui_controller.py  │ │
│  │  (小j 大腦)        │      │  (AI 智能控制器)      │ │
│  └────────────────────┘      └───────────────────────┘ │
│              │                         │                 │
│              │                         v                 │
│              │              ┌───────────────────────┐   │
│              │              │  server_ui_client.py  │   │
│              │              │  (UI 控制客戶端)      │   │
│              │              └───────────────────────┘   │
└──────────────┼──────────────────────┼───────────────────┘
               │                      │ WebSocket
               v                      v
       自然語言理解          ┌──────────────────────┐
       智能決策              │  本機 (192.168.50.84) │
                             │  local_ui_server.py  │
                             │  (服務端)            │
                             └──────────────────────┘
                                      │
                                      v
                             ┌─────────────────┐
                             │  本機 UI 操作   │
                             │  - 打開瀏覽器   │
                             │  - 執行腳本     │
                             │  - 系統控制     │
                             └─────────────────┘
```

## ✨ 新功能：AI 智能控制

現在小 j（AI）可以：

-   🧠 **理解自然語言**: "幫我打開 Odoo" → 自動執行
-   🎯 **智能決策**: 根據上下文判斷需要執行的操作
-   💬 **對話式控制**: 像和家人聊天一樣控制系統
-   🔄 **自動執行**: AI 自動判斷並執行 UI 操作
-   📊 **狀態回報**: 執行後自動回報結果

## 📦 文件結構

```
remote_ui_control/
├── ai_ui_controller.py         # 🤖 AI 智能控制器（新）
├── chat_app_integrated.py      # 🌐 Streamlit Web 介面（新）
├── local_ui_server.py          # 本機端 WebSocket 服務
├── server_ui_client.py         # Server 端客戶端
├── start_ai_ui_control.ps1     # 🚀 AI 控制系統啟動腳本（新）
├── start_local_server.ps1      # 本機端啟動腳本
├── start_server_client.sh      # Server 端啟動腳本
├── .env.example                # 環境配置範例
├── requirements.txt            # Python 依賴
└── README.md                   # 說明文檔
```

## 🚀 快速開始（AI 整合版）

### 方案 A: Streamlit Web 介面（推薦）

#### 步驟 1: 啟動本機端服務

```powershell
# 本機 (192.168.50.84)
cd "c:\wuchang V5.1.0\remote_ui_control"
.\start_local_server.ps1
```

#### 步驟 2: 啟動 AI 智能控制系統

```powershell
# Server (192.168.50.249) 或本地測試
cd "c:\wuchang V5.1.0\remote_ui_control"
.\start_ai_ui_control.ps1
# 選擇 2 (Streamlit Web 介面)
```

#### 步驟 3: 開始對話

瀏覽器將自動打開，你可以：

-   💬 "幫我打開 Odoo"
-   💬 "檢查一下本機狀態"
-   💬 "打開 Google"
-   💬 "刷新一下瀏覽器"

### 方案 B: 命令行互動模式

```powershell
# Server 端
.\start_ai_ui_control.ps1
# 選擇 1 (命令行互動模式)
```

然後就可以自然對話：

```
你: 幫我打開 Odoo
小j: 好的哥哥，我馬上為你打開 Odoo 系統 ✨
  🎮 已執行: open_odoo
  ✅ 已打開: http://localhost:8069
```

## 🎮 AI 對話範例

### 範例 1: 打開應用

```
你: 幫我打開 Odoo
小j: 好的哥哥，我馬上為你打開 Odoo 系統 ✨
    🎮 已執行: open_odoo
    ✅ 已打開: http://localhost:8069
```

### 範例 2: 檢查狀態

```
你: 檢查一下本機狀態
小j: 讓我檢查一下本機的運行狀態...
    🎮 已執行: get_status
    ✅ {
      "hostname": "DESKTOP-XXX",
      "services": {
        "odoo": true,
        "ai_assistant": true
      }
    }
```

### 範例 3: 開啟網頁

```
你: 打開 Google
小j: 為你打開 Google 🌐
    🎮 已執行: open_browser
    ✅ 已打開: https://www.google.com
```

### 範例 4: 多重操作

```
你: 幫我開啟 Odoo 和 AI 介面
小j: 好的，我為你開啟這兩個系統 💫
    🎮 已執行: open_odoo
    ✅ 已打開: http://localhost:8069
    🎮 已執行: open_ai
    ✅ 已打開: http://localhost:8080
```

## 🤖 AI 工作原理

### 1. 自然語言理解

AI 分析你的對話，識別意圖：

-   "打開 Odoo" → 識別為 UI 操作需求
-   "檢查狀態" → 識別為系統查詢需求

### 2. 指令生成

AI 自動生成 UI 控制指令：

```json
[UI_COMMAND]
{
  "action": "open_odoo"
}
[/UI_COMMAND]
```

### 3. 自動執行

系統自動執行指令並回報結果

### 4. 智能回應

AI 結合執行結果給出回應

## 🎮 可用指令

傳統命令行模式下的指令（AI 模式會自動處理）：

### 1. 打開 Odoo UI

```bash
python3 server_ui_client.py open_odoo
```

### 2. 打開 AI Assistant UI

```bash
python3 server_ui_client.py open_ai
```

### 3. 打開指定 URL

```python
# 互動模式中輸入
3
# 然後輸入 URL
https://example.com
```

### 4. 獲取本機狀態

```bash
python3 server_ui_client.py status
```

### 5. 刷新 UI

```bash
python3 server_ui_client.py refresh
```

### 6. 執行腳本

```python
# 互動模式中輸入
6
# 然後輸入要執行的 PowerShell 命令
Get-Process | Where-Object {$_.Name -like "python*"}
```

## 🔐 安全機制

### HMAC Token 認證

-   使用 HMAC-SHA256 生成認證 Token
-   Token 包含時間戳，5 分鐘有效期（防止重放攻擊）
-   使用共享密鑰 (WUCHANG_SECRET)

### 時間戳驗證

```python
# Token 生成公式
token = HMAC-SHA256(SECRET, "SERVER_IP:TIMESTAMP")
```

### IP 白名單（可選）

可以在 `local_ui_server.py` 中添加 IP 白名單：

```python
ALLOWED_IPS = ["192.168.50.249"]

def is_ip_allowed(ip: str) -> bool:
    return ip in ALLOWED_IPS
```

## 📊 WebSocket 通訊協議

### 認證消息

```json
{
    "token": "abc123...",
    "timestamp": "1234567890.123",
    "server_ip": "192.168.50.249"
}
```

### 認證響應

```json
{
    "type": "auth_response",
    "status": "success",
    "message": "認證成功，已建立連線"
}
```

### UI 操作指令

```json
{
    "type": "open_odoo",
    "payload": {},
    "timestamp": "2026-01-12T10:30:00"
}
```

### 指令響應

```json
{
    "status": "success",
    "result": "已打開: http://localhost:8069"
}
```

## 🛠️ 支援的指令類型

| 指令類型         | 說明                 | Payload             |
| ---------------- | -------------------- | ------------------- |
| `open_odoo`      | 打開 Odoo UI         | -                   |
| `open_ai`        | 打開 AI Assistant UI | -                   |
| `open_browser`   | 打開指定 URL         | `{"url": "..."}`    |
| `execute_script` | 執行腳本             | `{"script": "..."}` |
| `get_status`     | 獲取系統狀態         | -                   |
| `refresh_ui`     | 刷新瀏覽器           | -                   |

## 🔧 防火牆配置

### 本機端 (Windows)

```powershell
# 允許 8765 端口入站連線
netsh advfirewall firewall add rule name="Allow-UI-Control-8765" dir=in action=allow protocol=tcp localport=8765 remoteip=192.168.50.249
```

### Server 端 (Linux)

```bash
# UFW 防火牆（如果需要）
sudo ufw allow from 192.168.50.84 to any port 8765
```

## 📝 日誌

### 本機端日誌

```
2026-01-12 10:30:00 - UIControlServer - INFO - 🚀 本機 UI 控制服務啟動
2026-01-12 10:30:00 - UIControlServer - INFO - 📡 監聽: 0.0.0.0:8765
2026-01-12 10:30:15 - UIControlServer - INFO - 新連線來自: ('192.168.50.249', 54321)
2026-01-12 10:30:15 - UIControlServer - INFO - ✅ Server ('192.168.50.249', 54321) 認證成功
2026-01-12 10:30:20 - UIControlServer - INFO - 收到指令: open_odoo
```

### Server 端日誌

```
2026-01-12 10:30:15 - UIControlClient - INFO - 🔌 嘗試連線到: ws://192.168.50.84:8765
2026-01-12 10:30:15 - UIControlClient - INFO - ✅ 已成功連線到本機: 192.168.50.84
2026-01-12 10:30:20 - UIControlClient - INFO - 📋 請求打開 Odoo UI...
2026-01-12 10:30:20 - UIControlClient - INFO - 結果: {'status': 'success', 'result': '已打開: http://localhost:8069'}
```

## 🚨 故障排除

### 1. 連線失敗

```
錯誤: [WinError 10061] 無法連線，因為目標電腦拒絕連線
解決: 確認本機端服務已啟動
```

### 2. 認證失敗

```
錯誤: 認證失敗
解決: 檢查 .env 中的 WUCHANG_SECRET 是否一致
```

### 3. 防火牆阻擋

```
錯誤: 連線超時
解決: 檢查防火牆規則，允許 8765 端口
```

### 4. 時間不同步

```
錯誤: Token 過期
解決: 確保本機和 Server 的系統時間同步
```

## 🔄 自動重連

Server 端客戶端支援自動重連，如果連線中斷會每 5 秒重試一次。

## 📱 整合到現有系統

### 與 chat_app.py 整合

```python
# 在 chat_app.py 中添加
import asyncio
from remote_ui_control.server_ui_client import UIControlClient

async def open_local_ui():
    client = UIControlClient()
    if await client.connect():
        await client.open_odoo_ui()
        await client.close()

# Streamlit 按鈕
if st.button("打開本機 Odoo"):
    asyncio.run(open_local_ui())
```

## 🌟 進階功能

### 1. 定時任務

在 Server 端可以設定定時檢查狀態：

```python
async def periodic_status_check():
    client = UIControlClient()
    await client.connect()

    while True:
        status = await client.get_client_status()
        logger.info(f"本機狀態: {status}")
        await asyncio.sleep(60)  # 每分鐘檢查
```

### 2. 批量操作

```python
async def batch_operations():
    client = UIControlClient()
    await client.connect()

    await client.open_odoo_ui()
    await asyncio.sleep(2)
    await client.open_ai_ui()
```

## 📄 授權

此系統為五常 AI 專用，僅供內部使用。

## 🤝 支援

如有問題，請聯繫：小 j (Wuchang AI Assistant)
