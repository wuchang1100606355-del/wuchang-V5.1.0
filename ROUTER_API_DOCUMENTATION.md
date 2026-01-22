# 華碩路由器 RT-BE86U API 文檔

## 📋 基本資訊

- **路由器型號**: ASUS RT-BE86U
- **管理介面**: `https://192.168.50.84:8443`
- **外部 IP**: `220.135.21.74`
- **DDNS**: `coffeeLofe.asuscomm.com`

## 🔐 認證方式

### 登錄 API

**端點**: `/login.cgi`

**方法**: POST

**參數**:
```json
{
  "login_authorization": "base64(username:password)",
  "action_mode": "login"
}
```

**範例**:
```python
auth_string = f"{username}:{password}"
auth_encoded = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
login_data = {
    "login_authorization": auth_encoded,
    "action_mode": "login"
}
```

## 📡 API 端點分類

### 1. 資訊查詢 API (appGet.cgi)

#### 1.1 系統資訊
- **端點**: `/appGet.cgi?hook=get_system_info()`
- **方法**: GET
- **說明**: 獲取系統基本資訊

#### 1.2 WAN 狀態
- **端點**: `/appGet.cgi?hook=get_wan_status()`
- **方法**: GET
- **說明**: 獲取 WAN 連線狀態

#### 1.3 LAN 狀態
- **端點**: `/appGet.cgi?hook=get_lan_status()`
- **方法**: GET
- **說明**: 獲取 LAN 狀態

#### 1.4 無線客戶端
- **端點**: `/appGet.cgi?hook=get_wireless_client()`
- **方法**: GET
- **說明**: 獲取無線客戶端列表

#### 1.5 客戶端列表
- **端點**: `/appGet.cgi?hook=get_client_list()`
- **方法**: GET
- **說明**: 獲取所有連線客戶端

#### 1.6 韌體資訊
- **端點**: `/appGet.cgi?hook=get_firmware_info()`
- **方法**: GET
- **說明**: 獲取韌體版本資訊

#### 1.7 DDNS 狀態
- **端點**: `/appGet.cgi?hook=get_ddns_status()`
- **說明**: 獲取 DDNS 服務狀態

#### 1.8 VPN 狀態
- **端點**: `/appGet.cgi?hook=get_vpn_status()`
- **說明**: 獲取 VPN 連線狀態

### 2. 設定 API (appSet.cgi)

#### 2.1 設定參數
- **端點**: `/appSet.cgi`
- **方法**: POST
- **參數**:
  ```json
  {
    "action_mode": "apply",
    "action_script": "restart_firewall",
    "參數名稱": "參數值"
  }
  ```

### 3. 應用設定 API (apply.cgi)

#### 3.1 備份設定
- **端點**: `/apply.cgi?action_mode=backup`
- **方法**: GET
- **說明**: 下載設定備份檔案

#### 3.2 還原設定
- **端點**: `/apply.cgi`
- **方法**: POST
- **參數**:
  ```json
  {
    "action_mode": "restore",
    "action_script": "restore",
    "next_page": "Advanced_SettingBackup_Content.asp"
  }
  ```
- **檔案**: 使用 multipart/form-data 上傳 .CFG 檔案

#### 3.3 重啟路由器
- **端點**: `/apply.cgi`
- **方法**: POST
- **參數**:
  ```json
  {
    "action_mode": "reboot"
  }
  ```

### 4. 網頁介面端點

#### 4.1 主要頁面
- `/Main_Login.asp` - 登錄頁面
- `/index.asp` - 主頁
- `/Main_Status_Content.asp` - 狀態頁面

#### 4.2 設定頁面
- `/Advanced_System_Content.asp` - 系統設定
- `/Advanced_WAN_Content.asp` - WAN 設定
- `/Advanced_LAN_Content.asp` - LAN 設定
- `/Advanced_Wireless_Content.asp` - 無線設定
- `/Advanced_Firewall_Content.asp` - 防火牆設定
- `/Advanced_VPN_Content.asp` - VPN 設定
- `/Advanced_SettingBackup_Content.asp` - 備份/還原設定

## 🛠️ 使用範例

### Python 範例

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
controller.login()

# 獲取系統資訊
system_info = controller.get_system_info()
print(system_info)

# 獲取 WAN 狀態
wan_status = controller.get_wan_status()
print(wan_status)

# 備份設定
controller.backup_config("router_backup.cfg")

# 重啟路由器
controller.reboot()
```

## 📝 注意事項

1. **認證**: 大部分 API 需要先登錄
2. **證書**: 使用 HTTPS 時需要客戶端證書（如果已設定）
3. **超時**: 某些操作（如重啟、還原）可能需要較長時間
4. **安全性**: 避免在公開環境中暴露認證資訊

## 🔍 API 探索

使用 `router_api_explorer.py` 可以自動發現更多 API 端點：

```bash
python router_api_explorer.py --host 192.168.50.84 --port 8443 --username admin --password your_password
```

探索結果會保存在 `router_api_docs/router_api_discovery.json`

## 📅 文檔更新日期

2026-01-22
