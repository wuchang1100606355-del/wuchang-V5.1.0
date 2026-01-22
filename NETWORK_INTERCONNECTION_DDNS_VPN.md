# 兩機區網互通設定指南（DDNS / OpenVPN）

## 概述

本指南說明如何使用 DDNS 或 OpenVPN 實現兩機（本機與伺服器）之間的網路互通。

## 連接方式

### 方式一：DDNS（動態 DNS）

使用路由器的 DDNS 服務（例如：coffeeLofe.asuscomm.com）連接到遠端伺服器。

**優點：**
- 無需固定 IP
- 透過路由器直接連接
- 支援 HTTPS 加密連接

**設定步驟：**
1. 確認路由器 DDNS 已啟用
2. 記錄 DDNS 主機名（例如：coffeeLofe.asuscomm.com）
3. 設定路由器證書（如果需要）

### 方式二：OpenVPN

透過 VPN 隧道建立安全連接。

**優點：**
- 加密傳輸
- 跨網路連接
- 安全性高

**設定步驟：**
1. 建立 OpenVPN 連接
2. 確認 VPN 已連接
3. 使用 VPN 內網 IP 進行連接

## 快速設定

### 步驟 1：建立配置檔案

複製範例配置檔案：

```bash
Copy-Item network_interconnection_config.example.json network_interconnection_config.json
```

### 步驟 2：編輯配置檔案

#### DDNS 方式配置

```json
{
  "server_ddns": "coffeeLofe.asuscomm.com",
  "server_ip": "",
  "server_share": "\\\\192.168.1.100\\share\\wuchang",
  "health_url": "https://coffeeLofe.asuscomm.com:8443/health",
  "router": {
    "ddns": "coffeeLofe.asuscomm.com",
    "port": 8443,
    "cert_path": "certs/cert.pem",
    "key_path": "certs/key.pem"
  }
}
```

#### OpenVPN 方式配置

```json
{
  "server_ip": "10.8.0.1",
  "server_share": "\\\\10.8.0.1\\share\\wuchang",
  "health_url": "http://10.8.0.1:8788/health",
  "vpn": {
    "enabled": true,
    "server": "vpn.example.com",
    "config_path": "path/to/vpn/config.ovpn"
  }
}
```

### 步驟 3：設定路由器證書（DDNS 方式）

如果使用 DDNS 且需要證書認證：

```bash
# 1. 解壓縮證書檔案
python setup_router_cert.py "cert_key (1).tar"

# 2. 證書會自動複製到 certs/ 目錄
#    - certs/cert.pem
#    - certs/key.pem
```

### 步驟 4：執行自動設定

```bash
python setup_network_interconnection.py
```

## 詳細設定說明

### DDNS 設定

#### 1. 路由器 DDNS 資訊

- **DDNS 主機名**：`coffeeLofe.asuscomm.com`
- **端口**：`8443` (HTTPS)
- **證書**：需要客戶端證書（cert.pem + key.pem）

#### 2. 解析 DDNS 到 IP

腳本會自動解析 DDNS 主機名：

```python
# 自動解析
ddns_ip = resolve_ddns("coffeeLofe.asuscomm.com")
# 結果：220.135.21.74（動態 IP）
```

#### 3. 使用路由器連接

```python
from router_connection import AsusRouterConnection

router = AsusRouterConnection(
    hostname="coffeeLofe.asuscomm.com",
    port=8443,
    cert_path="certs/cert.pem",
    key_path="certs/key.pem"
)

# 測試連接
router.test_connection()
```

### OpenVPN 設定

#### 1. 檢查 VPN 連接

腳本會自動檢測 VPN 連接狀態：

```python
# 檢查 VPN 適配器
vpn_connected = check_vpn_connection()
```

#### 2. 使用 VPN 內網 IP

連接後，使用 VPN 分配的內網 IP：

```json
{
  "server_ip": "10.8.0.1",
  "server_share": "\\\\10.8.0.1\\share\\wuchang"
}
```

#### 3. 手動建立 VPN 連接

如果需要手動建立 VPN：

```powershell
# Windows: 使用 OpenVPN GUI 或命令列
# 或使用系統 VPN 設定
```

## 配置檔案完整範例

```json
{
  "server_ddns": "coffeeLofe.asuscomm.com",
  "server_ip": "192.168.1.100",
  "server_share": "\\\\192.168.1.100\\share\\wuchang",
  "health_url": "https://coffeeLofe.asuscomm.com:8443/health",
  "hub_url": "http://192.168.1.100:8799",
  "hub_token": "your_hub_token_here",
  "vpn": {
    "enabled": false,
    "server": "vpn.example.com",
    "config_path": "path/to/vpn/config.ovpn"
  },
  "router": {
    "ddns": "coffeeLofe.asuscomm.com",
    "port": 8443,
    "cert_path": "certs/cert.pem",
    "key_path": "certs/key.pem"
  }
}
```

## 自動化執行流程

### 完整自動化腳本

```bash
# 1. 設定路由器證書（如果需要）
python setup_router_cert.py "cert_key (1).tar"

# 2. 執行網路互通設定
python setup_network_interconnection.py

# 3. 自動授權（如果需要）
python auto_authorize_and_execute.py

# 4. 驗證連接
python check_server_connection.py

# 5. 執行檔案同步
python sync_all_profiles.py
```

## 測試連接

### 測試 DDNS 連接

```bash
# 解析 DDNS
nslookup coffeeLofe.asuscomm.com

# 測試端口
Test-NetConnection -ComputerName coffeeLofe.asuscomm.com -Port 8443

# 使用路由器連接工具
python router_connection.py
```

### 測試 OpenVPN 連接

```bash
# 檢查 VPN 適配器
ipconfig | findstr "TAP\|TUN\|VPN"

# 測試 VPN 內網 IP
ping 10.8.0.1

# 測試 SMB 共享
Test-Path "\\10.8.0.1\share\wuchang"
```

## 常見問題

### Q: DDNS 無法解析

**解決方案：**
1. 確認 DDNS 服務正常運行
2. 檢查網路連接
3. 確認 DNS 設定正確
4. 嘗試使用 IP 地址直接連接

### Q: 路由器證書錯誤

**解決方案：**
1. 確認證書檔案正確解壓縮
2. 檢查證書和密鑰檔案路徑
3. 確認證書格式正確（PEM）
4. 檢查證書是否過期

### Q: OpenVPN 無法連接

**解決方案：**
1. 確認 VPN 伺服器運行正常
2. 檢查 VPN 配置檔案
3. 確認認證資訊正確
4. 檢查防火牆設定

### Q: 混合使用 DDNS 和 VPN

**解決方案：**
可以同時配置，腳本會：
1. 優先使用 VPN（如果已連接）
2. 如果 VPN 未連接，使用 DDNS
3. 自動選擇最佳連接方式

## 相關工具

- `setup_network_interconnection.py` - 網路互通設定工具
- `setup_router_cert.py` - 路由器證書設定工具
- `router_connection.py` - 路由器連接工具
- `check_server_connection.py` - 連接狀態檢查
