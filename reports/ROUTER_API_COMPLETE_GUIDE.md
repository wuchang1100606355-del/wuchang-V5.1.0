# 華碩路由器 RT-BE86U 完整 API 控管指南

## 📋 路由器資訊

- **型號**: ASUS RT-BE86U
- **本地 IP**: `192.168.50.84`
- **外部 IP**: `220.135.21.74`
- **管理端口**: `8443` (HTTPS)
- **SSH 端口**: `22` (標準), `65433` (自訂)
- **DDNS**: `coffeeLofe.asuscomm.com`

## 🔧 工具說明

### 1. router_api_explorer.py
**用途**: 自動探索和發現路由器 API 端點

**功能**:
- 測試常見 API 端點
- 從 Web 介面提取 API 資訊
- 分析 HTML/JavaScript 找出 API 調用
- 生成 API 探索報告

**使用方式**:
```bash
# 基本探索（無認證）
python router_api_explorer.py --host 192.168.50.84 --port 8443

# 完整探索（需要認證）
python router_api_explorer.py --host 192.168.50.84 --port 8443 --username admin --password your_password
```

### 2. router_api_controller.py
**用途**: 完整的路由器 API 控制介面

**功能**:
- 系統資訊查詢
- 網路狀態監控
- 設定備份/還原
- 端口轉發管理
- 路由器重啟

**使用方式**:
```bash
# 獲取所有資訊
python router_api_controller.py --host 192.168.50.84 --username admin --password your_password --action info

# 備份設定
python router_api_controller.py --host 192.168.50.84 --username admin --password your_password --action backup --file router_backup.cfg

# 還原設定
python router_api_controller.py --host 192.168.50.84 --username admin --password your_password --action restore --file Settings_RT-BE86U.CFG

# 重啟路由器
python router_api_controller.py --host 192.168.50.84 --username admin --password your_password --action reboot
```

## 📡 完整 API 端點列表

### 認證相關

#### 登錄
- **端點**: `/login.cgi`
- **方法**: POST
- **參數**:
  ```json
  {
    "login_authorization": "base64(username:password)",
    "action_mode": "login"
  }
  ```

#### 登出
- **端點**: `/logout.cgi`
- **方法**: GET/POST

### 資訊查詢 API (appGet.cgi)

所有資訊查詢 API 使用相同的端點格式：
```
/appGet.cgi?hook=函數名稱()
```

#### 系統資訊類

| Hook 函數 | 說明 | 返回資料 |
|-----------|------|---------|
| `get_system_info()` | 系統基本資訊 | 型號、韌體版本、運行時間等 |
| `get_firmware_info()` | 韌體資訊 | 版本號、更新日期等 |
| `get_wan_status()` | WAN 連線狀態 | IP、閘道、DNS、連線狀態 |
| `get_lan_status()` | LAN 狀態 | 網段、DHCP 狀態等 |
| `get_wireless_client()` | 無線客戶端列表 | 連線設備、MAC、IP、訊號強度 |
| `get_client_list()` | 所有客戶端列表 | 有線+無線設備清單 |
| `get_ddns_status()` | DDNS 狀態 | DDNS 服務狀態、IP 更新記錄 |
| `get_vpn_status()` | VPN 狀態 | VPN 連線狀態、伺服器資訊 |
| `get_port_forwarding_rules()` | 端口轉發規則 | 所有端口轉發設定 |
| `get_firewall_rules()` | 防火牆規則 | 防火牆規則列表 |
| `get_qos_status()` | QoS 狀態 | 頻寬管理狀態 |
| `get_usb_status()` | USB 狀態 | USB 設備狀態 |
| `get_traffic_monitor()` | 流量監控 | 網路流量統計 |

#### 無線網路類

| Hook 函數 | 說明 |
|-----------|------|
| `get_wireless_2g_status()` | 2.4G 無線狀態 |
| `get_wireless_5g_status()` | 5G 無線狀態 |
| `get_wireless_6g_status()` | 6G 無線狀態（如果支援） |
| `get_wireless_guest_status()` | 訪客網路狀態 |

#### 進階功能類

| Hook 函數 | 說明 |
|-----------|------|
| `get_ai_protection_status()` | AI 防護狀態 |
| `get_parental_control_status()` | 家長控制狀態 |
| `get_game_acceleration_status()` | 遊戲加速狀態 |
| `get_adaptive_qos_status()` | 自適應 QoS 狀態 |

### 設定 API (appSet.cgi)

#### 基本格式
```
/appSet.cgi
```

**方法**: POST

**參數格式**:
```json
{
  "action_mode": "apply",
  "action_script": "restart_service",
  "參數名稱1": "參數值1",
  "參數名稱2": "參數值2"
}
```

#### 常用 action_script

- `restart_firewall` - 重啟防火牆
- `restart_wan` - 重啟 WAN
- `restart_wireless` - 重啟無線網路
- `restart_dns` - 重啟 DNS
- `restart_httpd` - 重啟 Web 服務
- `restart_network` - 重啟網路服務

### 應用設定 API (apply.cgi)

#### 備份設定
- **端點**: `/apply.cgi?action_mode=backup`
- **方法**: GET
- **說明**: 下載設定備份檔案（.CFG 格式）

#### 還原設定
- **端點**: `/apply.cgi`
- **方法**: POST (multipart/form-data)
- **參數**:
  ```json
  {
    "action_mode": "restore",
    "action_script": "restore",
    "next_page": "Advanced_SettingBackup_Content.asp"
  }
  ```
- **檔案**: 上傳 .CFG 設定檔案

#### 重啟路由器
- **端點**: `/apply.cgi`
- **方法**: POST
- **參數**:
  ```json
  {
    "action_mode": "reboot"
  }
  ```

#### 恢復出廠設定
- **端點**: `/apply.cgi`
- **方法**: POST
- **參數**:
  ```json
  {
    "action_mode": "clear",
    "action_script": "clear_nvram"
  }
  ```

### 網頁介面端點

#### 主要頁面
- `/` - 主頁（重定向到登錄或狀態頁）
- `/Main_Login.asp` - 登錄頁面
- `/index.asp` - 主索引頁
- `/Main_Status_Content.asp` - 狀態總覽

#### 設定頁面
- `/Advanced_System_Content.asp` - 系統設定
- `/Advanced_WAN_Content.asp` - WAN 設定
- `/Advanced_LAN_Content.asp` - LAN 設定
- `/Advanced_Wireless_Content.asp` - 無線設定
- `/Advanced_Firewall_Content.asp` - 防火牆設定
- `/Advanced_VPN_Content.asp` - VPN 設定
- `/Advanced_SettingBackup_Content.asp` - 備份/還原設定
- `/Advanced_PortForward_Content.asp` - 端口轉發設定
- `/Advanced_DDNS_Content.asp` - DDNS 設定

## 💻 Python 使用範例

### 基本連接與查詢

```python
from router_api_controller import RouterAPIController

# 建立控制器
controller = RouterAPIController(
    hostname="192.168.50.84",
    port=8443,
    username="admin",
    password="your_password"
)

# 登錄
if controller.login():
    print("登錄成功")
    
    # 獲取系統資訊
    system_info = controller.get_system_info()
    print("系統資訊:", system_info)
    
    # 獲取 WAN 狀態
    wan_status = controller.get_wan_status()
    print("WAN 狀態:", wan_status)
    
    # 獲取所有資訊
    all_info = controller.get_all_info()
    print(json.dumps(all_info, ensure_ascii=False, indent=2))
```

### 端口轉發管理

```python
# 獲取端口轉發規則
rules = controller.get_port_forwarding_rules()
print("端口轉發規則:", rules)

# 設定新的端口轉發規則
new_rule = {
    "vts_enable_x": "1",
    "vts_port_x": "65433",
    "vts_ipaddr_x": "192.168.50.84",
    "vts_proto_x": "TCP",
    "vts_desc_x": "SSH-65433"
}
controller.set_port_forwarding_rule(new_rule)
```

### 備份與還原

```python
# 備份設定
controller.backup_config("router_backup_20260122.cfg")

# 還原設定
controller.restore_config("Settings_RT-BE86U.CFG")
```

### 自訂 API 調用

```python
# 調用自訂 hook 函數
result = controller.app_get("get_custom_info()")
print(result)

# 設定參數
controller.app_set(
    action_mode="apply",
    action_script="restart_wireless",
    data={"wl_ssid": "NewSSID", "wl_key": "NewPassword"}
)
```

## 🔍 API 探索流程

### 步驟 1: 執行探索工具

```bash
python router_api_explorer.py --host 192.168.50.84 --port 8443 --username admin --password your_password
```

### 步驟 2: 查看探索結果

探索結果保存在 `router_api_docs/router_api_discovery.json`，包含：
- 所有測試的端點
- 響應狀態碼
- 響應時間
- 響應內容樣本
- 發現的新端點

### 步驟 3: 分析結果

使用發現的 API 端點建立自訂控制腳本。

## 📝 常見操作範例

### 1. 監控網路狀態

```python
controller = RouterAPIController(hostname="192.168.50.84", username="admin", password="password")
controller.login()

# 每 5 分鐘檢查一次 WAN 狀態
import time
while True:
    wan_status = controller.get_wan_status()
    print(f"WAN 狀態: {wan_status}")
    time.sleep(300)
```

### 2. 自動備份設定

```python
from datetime import datetime

controller = RouterAPIController(hostname="192.168.50.84", username="admin", password="password")
controller.login()

backup_file = f"router_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.cfg"
controller.backup_config(backup_file)
```

### 3. 管理端口轉發

```python
# 添加 SSH 端口轉發（65433 -> 22）
rule = {
    "vts_enable_x": "1",
    "vts_port_x": "65433",
    "vts_ipaddr_x": "192.168.50.84",
    "vts_proto_x": "TCP",
    "vts_desc_x": "SSH-Custom"
}
controller.set_port_forwarding_rule(rule)
```

## ⚠️ 注意事項

1. **認證安全**
   - 不要在程式碼中硬編碼密碼
   - 使用環境變數或設定檔案
   - 定期更換密碼

2. **操作風險**
   - 重啟路由器會中斷網路連線
   - 還原設定會覆蓋現有配置
   - 恢復出廠設定會清除所有設定

3. **連線問題**
   - 如果本地 IP 無法連接，嘗試使用外部 IP
   - 確認防火牆允許連接
   - 檢查路由器是否啟用遠程管理

4. **API 限制**
   - 某些 API 可能需要特定權限
   - 頻繁調用可能被限制
   - 部分操作需要等待路由器處理完成

## 🔗 相關檔案

- `router_api_explorer.py` - API 探索工具
- `router_api_controller.py` - API 控管工具
- `router_connection.py` - 基本連接工具
- `router_api_docs/router_api_discovery.json` - 探索結果
- `ROUTER_API_DOCUMENTATION.md` - API 文檔

## 📅 文檔建立日期

2026-01-22
