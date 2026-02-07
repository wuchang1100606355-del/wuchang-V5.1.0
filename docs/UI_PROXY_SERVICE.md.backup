# UI 代理服務說明文件

**文件日期**: 2025-01-07  
**系統版本**: Wuchang OS V5.1.0  
**功能**: 當 UI 設備離線時，伺服器自動代理 UI 的工作

---

## 🎯 功能概述

UI 代理服務是一個故障轉移機制，當 UI 設備（控制端）離線時，VM 伺服器（被控制端）會自動接管並代理 UI 設備的功能，確保系統持續運作。

### 核心特性

- ✅ **自動故障檢測**：每分鐘檢查 UI 設備心跳狀態
- ✅ **自動代理啟動**：檢測到 UI 離線時自動啟用代理模式
- ✅ **自動恢復**：UI 設備恢復連線時自動停止代理
- ✅ **功能完整**：代理 Sister Control、POS 同步、設備管理等核心功能
- ✅ **統計追蹤**：記錄代理次數和時長

---

## 📋 架構設計

### 控制流程

```
┌─────────────────────────────────────────┐
│         UI 設備（控制端）                │
│     每 30 秒發送心跳                    │
└─────────────────────────────────────────┘
                    │
                    │ 心跳
                    ▼
┌─────────────────────────────────────────┐
│      VM 伺服器（被控制端）              │
│                                         │
│  ┌─────────────────────────────────┐  │
│  │  心跳監控服務                    │  │
│  │  - 檢查最後心跳時間              │  │
│  │  - 判斷 UI 狀態                  │  │
│  └─────────────────────────────────┘  │
│                    │                    │
│         ┌──────────┴──────────┐         │
│         │                     │         │
│    UI 在線              UI 離線        │
│         │                     │         │
│         ▼                     ▼         │
│  ┌──────────┐        ┌──────────────┐ │
│  │ 正常模式  │        │  代理模式     │ │
│  │          │        │              │ │
│  │ UI 控制  │        │ 伺服器代理   │ │
│  └──────────┘        └──────────────┘ │
└─────────────────────────────────────────┘
```

### 代理功能清單

當 UI 離線時，伺服器會代理以下功能：

1. **Sister Control**：控制 POS 和客顯設備
2. **POS 同步**：執行 POS 資料同步
3. **設備管理**：管理網路設備
4. **指令執行**：執行控制指令

---

## 🔧 設定步驟

### Step 1: 建立 UI 代理服務記錄

1. 登入 Odoo 管理界面
2. 進入「妹妹控制」→「UI 代理服務」
3. 點擊「建立」
4. 填寫以下資訊：
   - **UI 設備 IP**：UI 設備的 IP 地址（例如：`192.168.50.84`）
   - **UI 設備名稱**：UI 設備的識別名稱（例如：`UI Control Endpoint`）
   - **心跳間隔**：UI 設備發送心跳的間隔（預設：30 秒）
   - **心跳超時**：超過此時間未收到心跳視為離線（預設：90 秒）
   - **代理模式**：選擇「自動」（檢測到離線時啟用）

### Step 2: 配置 UI 設備發送心跳

在 UI 設備上設定定時發送心跳：

#### PowerShell 腳本（Windows）

```powershell
# scripts/ui_heartbeat.ps1
$VMIP = "192.168.50.84"
$UI_IP = "192.168.50.XX"  # UI 設備的 IP
$HeartbeatURL = "http://${VMIP}:8069/wuchang/ui/heartbeat"

while ($true) {
    try {
        $body = @{
            device_ip = $UI_IP
            device_name = "UI Control Endpoint"
        } | ConvertTo-Json
        
        Invoke-RestMethod -Uri $HeartbeatURL -Method POST -Body $body -ContentType "application/json"
        Write-Host "[$(Get-Date)] 心跳已發送" -ForegroundColor Green
    } catch {
        Write-Host "[$(Get-Date)] 心跳發送失敗: $_" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 30
}
```

#### Python 腳本（跨平台）

```python
# scripts/ui_heartbeat.py
import requests
import time
import socket

VM_IP = "192.168.50.84"
HEARTBEAT_URL = f"http://{VM_IP}:8069/wuchang/ui/heartbeat"

def get_local_ip():
    """獲取本機 IP 地址"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def send_heartbeat():
    """發送心跳"""
    try:
        device_ip = get_local_ip()
        payload = {
            'device_ip': device_ip,
            'device_name': 'UI Control Endpoint'
        }
        response = requests.post(HEARTBEAT_URL, json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 心跳已發送 - 代理狀態: {data.get('is_proxying', False)}")
        else:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 心跳發送失敗: {response.status_code}")
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 心跳發送失敗: {e}")

if __name__ == '__main__':
    print(f"UI 心跳服務啟動 - VM: {VM_IP}")
    while True:
        send_heartbeat()
        time.sleep(30)
```

### Step 3: 設定定時任務

#### Windows（使用工作排程器）

1. 開啟「工作排程器」
2. 建立基本工作
3. 設定：
   - **名稱**：UI Heartbeat Service
   - **觸發程序**：登入時或系統啟動時
   - **動作**：啟動程式
   - **程式**：`powershell.exe`
   - **引數**：`-File "C:\wuchang V5.1.0\scripts\ui_heartbeat.ps1"`

#### Linux/macOS（使用 systemd 或 cron）

```bash
# systemd 服務檔案：/etc/systemd/system/ui-heartbeat.service
[Unit]
Description=UI Heartbeat Service
After=network.target

[Service]
Type=simple
User=wuchang
WorkingDirectory=/opt/wuchang
ExecStart=/usr/bin/python3 /opt/wuchang/scripts/ui_heartbeat.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# 啟用服務
sudo systemctl enable ui-heartbeat.service
sudo systemctl start ui-heartbeat.service
```

---

## 📊 監控與管理

### 在 Odoo 中查看代理狀態

1. 登入 Odoo 管理界面
2. 進入「妹妹控制」→「UI 代理服務」
3. 查看以下資訊：
   - **UI 設備狀態**：在線/離線/未知
   - **正在代理**：是否正在代理 UI 工作
   - **最後心跳時間**：最後一次收到心跳的時間
   - **總代理次數**：歷史代理次數
   - **總代理時長**：歷史代理總時長（小時）

### API 查詢代理狀態

```bash
# 查詢代理狀態
curl -X GET "http://192.168.50.84:8069/wuchang/ui/proxy/status" \
  -H "Content-Type: application/json" \
  -b "session_id=YOUR_SESSION_ID"
```

回應範例：

```json
{
  "status": "success",
  "is_proxying": false,
  "ui_device_status": "online",
  "ui_device_ip": "192.168.50.XX",
  "last_heartbeat": "2025-01-07T10:30:00",
  "proxy_start_time": null
}
```

---

## 🔄 工作流程

### 正常運作流程

1. UI 設備每 30 秒發送心跳到 VM 伺服器
2. VM 伺服器每分鐘檢查 UI 設備狀態
3. 如果收到心跳，更新 `last_heartbeat` 時間
4. UI 設備狀態設為「在線」
5. 如果正在代理，自動停止代理

### UI 離線流程

1. VM 伺服器檢測到超過 90 秒未收到心跳
2. UI 設備狀態設為「離線」
3. 如果代理模式為「自動」且代理功能已啟用：
   - 啟動代理模式（`is_proxying = True`）
   - 記錄代理開始時間
   - 執行代理功能（Sister Control、POS 同步等）
   - 發送通知訊息

### UI 恢復流程

1. UI 設備恢復連線並發送心跳
2. VM 伺服器收到心跳，更新 `last_heartbeat`
3. UI 設備狀態設為「在線」
4. 如果正在代理：
   - 停止代理模式（`is_proxying = False`）
   - 記錄代理結束時間
   - 計算代理時長並累加到總時長
   - 發送通知訊息

---

## ⚙️ 進階設定

### 自訂代理功能

在 UI 代理服務記錄中，可以自訂 `proxy_capabilities`（JSON 格式）：

```json
{
  "sister_control": true,
  "pos_sync": true,
  "device_management": true,
  "command_execution": true,
  "custom_function_1": true,
  "custom_function_2": false
}
```

### 手動控制代理

- **強制啟用代理**：點擊「強制啟用代理」按鈕，即使 UI 在線也會啟用代理
- **停止代理**：點擊「停止代理」按鈕，手動停止代理模式

---

## 🧪 測試

### 測試 UI 離線檢測

1. 停止 UI 設備的心跳服務
2. 等待 90 秒（心跳超時時間）
3. 在 Odoo 中查看 UI 代理服務記錄
4. 確認：
   - UI 設備狀態變為「離線」
   - 「正在代理」變為「是」
   - 代理開始時間已記錄

### 測試 UI 恢復

1. 重新啟動 UI 設備的心跳服務
2. 等待心跳發送（最多 30 秒）
3. 在 Odoo 中查看 UI 代理服務記錄
4. 確認：
   - UI 設備狀態變為「在線」
   - 「正在代理」變為「否」
   - 代理結束時間已記錄
   - 總代理次數和時長已更新

---

## 📝 注意事項

1. **心跳間隔**：建議設定為 30 秒，確保及時檢測到離線
2. **心跳超時**：建議設定為 90 秒（3 個心跳間隔），避免誤判
3. **網路延遲**：如果網路延遲較高，可以適當增加心跳超時時間
4. **代理功能**：確保伺服器有足夠權限執行代理功能
5. **日誌監控**：定期檢查 Odoo 日誌，確認代理功能正常運作

---

## 🔍 故障排除

### 問題：UI 設備狀態一直顯示「未知」

**原因**：從未收到心跳或無法連接到 UI 設備

**解決方案**：
1. 確認 UI 設備的心跳服務正在運行
2. 檢查網路連線
3. 確認 VM 伺服器可以訪問 UI 設備的 IP
4. 檢查防火牆設定

### 問題：代理模式未自動啟動

**原因**：代理模式設定為「手動」或「停用」

**解決方案**：
1. 檢查代理模式設定，改為「自動」
2. 確認代理功能已啟用（`proxy_enabled = True`）
3. 檢查 Odoo 日誌是否有錯誤訊息

### 問題：心跳發送失敗

**原因**：VM 伺服器無法訪問或 Odoo 服務未運行

**解決方案**：
1. 確認 VM 伺服器的 Odoo 服務正在運行
2. 檢查 URL 是否正確：`http://VM_IP:8069/wuchang/ui/heartbeat`
3. 檢查網路連線
4. 檢查 Odoo 日誌

---

**文件版本**: 1.0  
**最後更新**: 2025-01-07  
**維護者**: 小J (Little J)
